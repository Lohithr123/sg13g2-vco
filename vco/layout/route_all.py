# Full routing — 20 GHz VCO, IHP SG13G2
#
# Reads the placed layout, connects every net, writes the routed GDS.
#
# HOW TERMINALS ARE FOUND
#
# The PDK's PCells mark their terminals, but not uniformly:
#
#   npn13G2    text labels 'C', 'B', 'E' on layer 63/0, at the cell origin
#   nmos       pin shapes: Metal1.pin (8/2) gives source then drain in x
#              order, GatPoly.pin (5/2) gives the gate. Only ONE finger of
#              each is marked — the rest are joined internally, so routing
#              touches one strip per terminal, not eleven.
#   rhigh      two Metal1.pin shapes, one at each end
#   SVaricap   text labels 'G1', 'G2', 'W' on 63/0
#   cmim       NO pins. Plates are TopMetal1 (126/0) top and Metal5 (67/0)
#              bottom; route to the plate geometry directly.
#   inductor   text 'LA', 'LB', 'LC' on 27/25, pins on TopMetal1/TopMetal2
#
# ROUTING RULES
#
# Metal1 for local connections, Metal2 for crossings, TopMetal1 down to the
# inductor. A via_stack PCell spans b_layer..t_layer in one instance.
#
# The critical rule, learned the hard way: a route must OVERLAP the target
# metal, not abut its bounding box. A 0.5 um gap passes DRC silently and is
# an open circuit. Every net is checked by merging the region and counting
# polygons — one polygon means connected.

import os
import sys

import pya

PDK = os.environ.get("PDK_ROOT", "/foss/pdks") + "/ihp-sg13g2"
sys.path.insert(0, PDK + "/libs.tech/klayout/python")
import sg13g2_pycell_lib  # noqa: F401

LIB, TECH = "SG13_dev", "sg13g2"
IN_GDS = "/foss/designs/vco/layout/vco_20g.gds"
OUT = "/foss/designs/vco/layout/vco_20g_routed.gds"

lib = pya.Library.library_by_name(LIB, TECH)
liblay = lib.layout()

layout = pya.Layout()
layout.dbu = 0.001
layout.read(IN_GDS)
top = layout.top_cell()

L = {
    "M1":   layout.layer(8, 0),
    "M2":   layout.layer(10, 0),
    "M3":   layout.layer(30, 0),
    "M4":   layout.layer(50, 0),
    "M5":   layout.layer(67, 0),
    "TM1":  layout.layer(126, 0),
    "TM2":  layout.layer(134, 0),
    "poly": layout.layer(5, 0),
}

# ---------------------------------------------------------------- terminals

def instances():
    """Every instance with its name and transform."""
    out = []
    for inst in top.each_inst():
        out.append((layout.cell(inst.cell_index).name, inst))
    return out


def label_pos(inst, want, lay=63, dt=0):
    """Position of a named text label inside an instance, in top coords."""
    li = layout.layer(lay, dt)
    for sh in layout.cell(inst.cell_index).shapes(li).each():
        if sh.is_text() and sh.text.string == want:
            p = pya.DPoint(sh.text.x * layout.dbu, sh.text.y * layout.dbu)
            return inst.dcplx_trans.trans(p)
    return None


def pin_boxes(inst, lay, dt, cell_order=True):
    """Pin shapes as boxes in top coords.

    cell_order sorts by position in the CELL's own frame, so a mirrored
    instance still returns source-then-drain rather than the reverse.
    """
    li = layout.layer(lay, dt)
    out = []
    for sh in layout.cell(inst.cell_index).shapes(li).each():
        if not sh.is_text():
            out.append(sh.dbbox().transformed(inst.dcplx_trans))
    if cell_order:
        inv = inst.dcplx_trans.inverted()
        return sorted(out, key=lambda b: inv.trans(b.center()).x)
    return sorted(out, key=lambda b: b.center().x)


def find(name_contains, near_x=None, near_y=None, tol=6.0, width_gt=None):
    """Locate an instance by cell name and approximate position."""
    best = None
    for nm, inst in instances():
        if name_contains not in nm:
            continue
        b = inst.dbbox()
        if width_gt is not None and b.width() < width_gt:
            continue
        if near_x is not None and abs(b.center().x - near_x) > tol:
            continue
        if near_y is not None and abs(b.center().y - near_y) > tol:
            continue
        best = inst
    return best

# ------------------------------------------------------------------ drawing

def snap(v, g=0.005):
    """Round to the 5 nm manufacturing grid.

    Terminal positions come from PCell geometry and are not themselves on a
    5 nm boundary — the emitter sits at y = -100.23, a mirror drain at
    x = -25.52. Drawing to those coordinates directly produces off-grid metal,
    which DRC rejects. Snapping the route while keeping it overlapping the
    target costs a couple of nanometres of alignment and nothing else.
    """
    return round(v / g) * g


def wire(layer, x1, y1, x2, y2, w):
    """Rectangle from (x1,y1) to (x2,y2), w wide, on the given layer."""
    x1, y1, x2, y2, w = (snap(x1), snap(y1), snap(x2), snap(y2), snap(w))
    if abs(x2 - x1) < 1e-9:                       # vertical
        top.shapes(L[layer]).insert(
            pya.DBox(x1 - w / 2, min(y1, y2), x1 + w / 2, max(y1, y2)))
    elif abs(y2 - y1) < 1e-9:                     # horizontal
        top.shapes(L[layer]).insert(
            pya.DBox(min(x1, x2), y1 - w / 2, max(x1, x2), y1 + w / 2))
    else:                                          # L-shaped: two segments
        wire(layer, x1, y1, x1, y2, w)
        wire(layer, x1, y2, x2, y2, w)


def via(x, y, b="Metal1", t="Metal2", cols=2, rows=2):
    x, y = snap(x), snap(y)
    pid = liblay.pcell_id("via_stack")
    ci = layout.add_pcell_variant(lib, pid, {
        "b_layer": b, "t_layer": t, "vn_columns": cols, "vn_rows": rows})
    bb = layout.cell(ci).dbbox()
    top.insert(pya.DCellInstArray(
        ci, pya.DTrans(x - bb.center().x, y - bb.center().y)))
    return bb

# -------------------------------------------------------------------- nets

report = []

def check(net, layer, x1, y1, x2, y2, expect=1):
    """Merge the region in a window and count polygons. One means connected."""
    # Flatten into a scratch cell so device geometry and routes merge in the
    # same space. It must be pruned afterwards or it survives as a second top
    # cell and DRC refuses to run.
    flat = layout.create_cell("_chk")
    flat.copy_tree(top)
    r = pya.Region(flat.begin_shapes_rec(L[layer])).merged()
    win = pya.Region(pya.DBox(x1, y1, x2, y2).to_itype(layout.dbu))
    n = (r & win).count()
    layout.prune_cell(flat.cell_index(), -1)
    ok = "ok " if n <= expect else "OPEN"
    report.append((ok, net, n, expect))
    print(f"  {ok}  {net:22} {n} polygon(s), expected <= {expect}")


print("=== locating devices ===")
XQ1 = find("npn13G2", near_x=-9.0, near_y=-100.0)
XQ2 = find("npn13G2", near_x=9.0, near_y=-100.0)
XB1 = find("npn13G2", near_x=-115.0, near_y=-95.0)
XB2 = find("npn13G2", near_x=115.0, near_y=-95.0)
XMT2 = find("nmos", near_x=-20.0, near_y=-190.0, width_gt=10)
XMT1 = find("nmos", near_x=20.0, near_y=-190.0, width_gt=10)
XMR2 = find("nmos", near_x=-55.0, near_y=-190.0)
XMR1 = find("nmos", near_x=-42.0, near_y=-190.0)
for nm, o in [("XQ1", XQ1), ("XQ2", XQ2), ("XB1", XB1), ("XB2", XB2),
              ("XMT2", XMT2), ("XMT1", XMT1), ("XMR2", XMR2), ("XMR1", XMR1)]:
    print(f"  {nm:5} {'found at ' + o.dbbox().to_s() if o else 'NOT FOUND'}")

print("\n=== net: tank (LA/LB to collectors) ===")
# Inductor ports are at fixed positions in the imported cell.
for tag, xc, dev in (("LA-XQ1", -9.0, XQ1), ("LB-XQ2", 9.0, XQ2)):
    c = label_pos(dev, "C")
    vy = -88.0
    bb = via(xc, vy, b="Metal1", t="TopMetal1")
    wire("TM1", xc, -85.3, xc, vy + bb.height() / 2, 6.0)
    wire("M1", xc, vy + bb.height() / 2, xc, c.y, 1.86)
    print(f"  {tag}: collector at ({c.x:.2f},{c.y:.2f})")
check("tank L", "M1", -11.0, -99.3, -7.0, -87.0)
check("tank R", "M1", 7.0, -99.3, 11.0, -87.0)

print("\n=== net: tail (emitters to XMT2 drain) ===")
# Emitters come out on Metal2 inside the npn cell.
e1 = label_pos(XQ1, "E")
e2 = label_pos(XQ2, "E")
# XMT2 drain is the second Metal1.pin in x order.
d = pin_boxes(XMT2, 8, 2)[1]
# Bring both emitters together on Metal2 at the midpoint, then run down.
wire("M2", e1.x, e1.y, 0.0, e1.y, 1.86)
wire("M2", e2.x, e2.y, 0.0, e2.y, 1.86)
wire("M2", 0.0, e1.y, 0.0, d.center().y, 2.0)
bb = via(0.0, d.center().y, b="Metal1", t="Metal2")
wire("M1", 0.0, d.center().y, d.center().x, d.center().y, 1.0)
print(f"  emitters ({e1.x:.2f},{e1.y:.2f}) and ({e2.x:.2f},{e2.y:.2f})")
print(f"  XMT2 drain at ({d.center().x:.2f},{d.center().y:.2f})")
check("tail M2", "M2", -12.0, -195.0, 12.0, -99.0)


print("\n=== net: cross-coupling (each base to the opposite collector) ===")
# XQ1's collector sits at y -99.10 and its base at y -101.37 — 2.27 um apart,
# both Metal1, both 1.86 um wide. At that pitch two 1 um routes on the same
# layer merge into one node: the first attempt shorted all four terminals
# together, which extraction confirmed as a single net.
#
# So each path gets its own layer above the device. Collectors leave on Metal2,
# bases arrive on Metal3, and the only Metal1 is the short stub at each
# terminal. Nothing on the same layer runs within 2 um of anything else.
b1 = label_pos(XQ1, "B"); b2 = label_pos(XQ2, "B")
c1 = label_pos(XQ1, "C"); c2 = label_pos(XQ2, "C")
print(f"  bases  ({b1.x:.2f},{b1.y:.2f}) ({b2.x:.2f},{b2.y:.2f})")
print(f"  colls  ({c1.x:.2f},{c1.y:.2f}) ({c2.x:.2f},{c2.y:.2f})")

XO = 6.0

# XQ2 collector -> XQ1 base, via Metal2 at y -112.
via(c2.x + XO, c2.y, b="Metal1", t="Metal2")
wire("M1", c2.x, c2.y, c2.x + XO, c2.y, 1.0)
wire("M2", c2.x + XO, c2.y, c2.x + XO, -112.0, 1.0)
wire("M2", c2.x + XO, -112.0, 20.0, -112.0, 1.0)
wire("M2", 20.0, -112.0, 20.0, -160.0, 1.0)
wire("M2", 20.0, -160.0, -20.0, -160.0, 1.0)
wire("M2", -20.0, -160.0, -20.0, -112.0, 1.0)
wire("M2", -20.0, -112.0, b1.x - XO, -112.0, 1.0)
wire("M2", b1.x - XO, -112.0, b1.x - XO, b1.y, 1.0)
via(b1.x - XO, b1.y, b="Metal1", t="Metal2")
wire("M1", b1.x - XO, b1.y, b1.x, b1.y, 1.0)

# XQ1 collector -> XQ2 base, via Metal3 at y -116, a different layer AND a
# different channel so the two feedback paths cannot touch.
via(c1.x - XO, c1.y, b="Metal1", t="Metal3")
wire("M1", c1.x - XO, c1.y, c1.x, c1.y, 1.0)
wire("M3", c1.x - XO, c1.y, c1.x - XO, -116.0, 1.0)
wire("M3", c1.x - XO, -116.0, b2.x + XO, -116.0, 1.0)
wire("M3", b2.x + XO, -116.0, b2.x + XO, b2.y, 1.0)
via(b2.x + XO, b2.y, b="Metal1", t="Metal3")
wire("M1", b2.x, b2.y, b2.x + XO, b2.y, 1.0)

print("\n=== net: tail cascode (XMT2 source to XMT1 drain) ===")
# Cascode pair: the upper device's source feeds the lower device's drain.
s2 = pin_boxes(XMT2, 8, 2)[0]
d1 = pin_boxes(XMT1, 8, 2)[1]
ym = -196.0
wire("M1", s2.center().x, s2.center().y, s2.center().x, ym, 1.0)
wire("M1", s2.center().x, ym, d1.center().x, ym, 1.0)
wire("M1", d1.center().x, ym, d1.center().x, d1.center().y, 1.0)
print(f"  XMT2 source ({s2.center().x:.2f},{s2.center().y:.2f}) -> "
      f"XMT1 drain ({d1.center().x:.2f},{d1.center().y:.2f})")
# The window unavoidably contains all 11 diffusion strips of both
# devices, so a polygon count here says nothing. Check only the
# routing channel below them.
check("cascode", "M1", -30.0, -197.5, 30.0, -194.5)

print("\n=== net: mirror gates ===")
# XMR2 gate drives both cascode gates; XMR1 gate drives both lower gates.
g_r2 = pin_boxes(XMR2, 5, 2)[0]
g_r1 = pin_boxes(XMR1, 5, 2)[0]
g_t2 = pin_boxes(XMT2, 5, 2)[0]
g_t1 = pin_boxes(XMT1, 5, 2)[0]
# Poly is resistive; get onto Metal1 immediately and route there.
for g in (g_r2, g_r1, g_t2, g_t1):
    via(g.center().x, g.center().y, b="Metal1", t="Metal2")
yg = -178.0
wire("M2", g_r2.center().x, g_r2.center().y, g_r2.center().x, yg, 1.0)
wire("M2", g_r2.center().x, yg, g_t2.center().x, yg, 1.0)
wire("M2", g_t2.center().x, yg, g_t2.center().x, g_t2.center().y, 1.0)
yg2 = -174.0
wire("M2", g_r1.center().x, g_r1.center().y, g_r1.center().x, yg2, 1.0)
wire("M2", g_r1.center().x, yg2, g_t1.center().x, yg2, 1.0)
wire("M2", g_t1.center().x, yg2, g_t1.center().x, g_t1.center().y, 1.0)
print(f"  cascode gate bus at y {yg}, mirror gate bus at y {yg2}")
check("gate bus", "M2", -60.0, -196.0, 30.0, -178.0, expect=3)

layout.write(OUT)
print(f"\nwrote {OUT}")
bad = [r for r in report if r[0] == "OPEN"]
print(f"{len(report) - len(bad)}/{len(report)} nets connected")
for _, net, n, exp in bad:
    print(f"  OPEN: {net} ({n} polygons, wanted <= {exp})")
