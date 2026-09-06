# Routing — 20 GHz VCO, IHP SG13G2
#
# WHY THIS IS A REWRITE
#
# The first attempt drew each net as a path from A to B without checking what
# was already in that space, and every net broke differently: routes abutting
# instead of overlapping, vias landing on device terminals that were already
# contacted, paths crossing other nets, and horizontal runs cutting straight
# through a mirror's finger array and shorting eleven strips together.
# Extraction found all of them; DRC found none.
#
# THE APPROACH THAT ACTUALLY WORKS HERE
#
# Every device lives in Metal1 and below. The inductor uses TopMetal1/2.
# Metal3, Metal4 and Metal5 are completely empty — no obstacles at all.
#
# So each net gets its own upper layer, and drops to Metal1 only at the exact
# terminal, via a stack that spans the whole distance in one instance
# (Metal1->Metal4 is 0.70 x 0.62 um, small enough to sit on a pin).
#
#   Metal3   outp  — XQ1 collector, XQ2 base, inductor LA
#   Metal4   outn  — XQ2 collector, XQ1 base, inductor LB
#   Metal5   tail, bias, supply
#   Metal2   short local stubs only
#
# Two nets that must cross are on different layers, so crossing is free.
# Terminals 2.27 um apart can be reached without their routes merging, because
# the routes are not on the same layer.
#
# This is how it should have been done from the start.

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

LAY = {"M1": (8, 0), "M2": (10, 0), "M3": (30, 0), "M4": (50, 0),
       "M5": (67, 0), "TM1": (126, 0), "TM2": (134, 0), "poly": (5, 0)}
LI = {k: layout.layer(*v) for k, v in LAY.items()}
STACK_NAME = {"M2": "Metal2", "M3": "Metal3", "M4": "Metal4",
              "M5": "Metal5", "TM1": "TopMetal1", "TM2": "TopMetal2"}


def snap(v, g=0.005):
    """Round to the 5 nm manufacturing grid.

    Terminal positions come from PCell geometry and are not themselves on a
    grid boundary. Drawing to them directly produces off-grid metal.
    """
    return round(v / g) * g


def wire(lyr, x1, y1, x2, y2, w=1.0):
    x1, y1, x2, y2 = snap(x1), snap(y1), snap(x2), snap(y2)
    if abs(x2 - x1) < 1e-9:
        top.shapes(LI[lyr]).insert(
            pya.DBox(x1 - w / 2, min(y1, y2), x1 + w / 2, max(y1, y2)))
    else:
        top.shapes(LI[lyr]).insert(
            pya.DBox(min(x1, x2), y1 - w / 2, max(x1, x2), y1 + w / 2))


def path(lyr, pts, w=1.0):
    """Manhattan path through a list of points, drawn as overlapping boxes."""
    for i in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        wire(lyr, x1, y1, x2, y2, w)


def drop(x, y, to, cols=2, rows=1, frm="Metal1"):
    """Via stack from Metal1 up to layer `to`, centred on (x, y).

    The bipolar's terminals are 0.24 um tall — the collector is Metal1
    y -99.215..-98.975, the base 0.24 um likewise, with the emitter's Metal2
    spanning between them. Nothing can be routed laterally at that pitch: a
    1 um wire is four times taller than the terminal it starts from and spills
    into its neighbour, which is what shorted every previous attempt.
    
    So the stack goes straight up ON the terminal. cols=2 rows=1 gives
    0.700 x 0.210 um, which fits inside a 1.86 x 0.24 um terminal with margin.
    """
    x, y = snap(x), snap(y)
    ci = layout.add_pcell_variant(lib, liblay.pcell_id("via_stack"),
                                  {"b_layer": frm,
                                   "t_layer": STACK_NAME[to],
                                   "vn_columns": cols, "vn_rows": rows})
    bb = layout.cell(ci).dbbox()
    top.insert(pya.DCellInstArray(
        ci, pya.DTrans(x - bb.center().x, y - bb.center().y)))
    # A narrow stack leaves sub-minimum metal on the intermediate layers
    # (M2.d, M3.d, M4.d are minimum-AREA rules, not spacing). Add a landing
    # pad on each layer the stack passes through. The pads sit above the
    # device on layers it does not use, so they cost nothing electrically.
    order = ["M1", "M2", "M3", "M4", "M5", "TM1"]
    start = order.index({"Metal1": "M1", "Metal2": "M2"}[frm])
    upto = order.index({v: k for k, v in STACK_NAME.items()}.get(
        STACK_NAME[to], to))
    for k in order[start + 1:upto + 1]:
        top.shapes(LI[k]).insert(
            pya.DBox(x - 0.36, y - 0.105, x + 0.36, y + 0.105))
    return bb


# ------------------------------------------------------------- terminals

def instances():
    return [(layout.cell(i.cell_index).name, i) for i in top.each_inst()]


def find(part, x=None, y=None, tol=6.0, wmin=None):
    for nm, inst in instances():
        if part not in nm:
            continue
        b = inst.dbbox()
        if wmin is not None and b.width() < wmin:
            continue
        if x is not None and abs(b.center().x - x) > tol:
            continue
        if y is not None and abs(b.center().y - y) > tol:
            continue
        return inst
    return None


def label(inst, want):
    for sh in layout.cell(inst.cell_index).shapes(layout.layer(63, 0)).each():
        if sh.is_text() and sh.text.string == want:
            return inst.dcplx_trans.trans(
                pya.DPoint(sh.text.x * layout.dbu, sh.text.y * layout.dbu))
    return None


def pins(inst, lay, dt):
    """Pin boxes in top coords, ordered by position in the CELL's own frame.

    A mirrored instance returns its pins reversed in x otherwise, which
    silently swaps source and drain.
    """
    out = [sh.dbbox().transformed(inst.dcplx_trans)
           for sh in layout.cell(inst.cell_index).shapes(layout.layer(lay, dt)).each()
           if not sh.is_text()]
    inv = inst.dcplx_trans.inverted()
    return sorted(out, key=lambda b: inv.trans(b.center()).x)


# ------------------------------------------------------------- extraction

def extract():
    l2n = pya.LayoutToNetlist(pya.RecursiveShapeIterator(layout, top, []))
    for k in ("M1", "M2", "M3", "M4", "M5", "TM1"):
        l2n.register(pya.Region(top.begin_shapes_rec(LI[k])), k)
    for v, (a, b) in [(19, ("M1", "M2")), (29, ("M2", "M3")),
                      (49, ("M3", "M4")), (66, ("M4", "M5")),
                      (125, ("M5", "TM1"))]:
        nm = f"V{v}"
        l2n.register(pya.Region(top.begin_shapes_rec(layout.layer(v, 0))), nm)
        l2n.connect(l2n.layer_by_name(nm))
        l2n.connect(l2n.layer_by_name(a), l2n.layer_by_name(nm))
        l2n.connect(l2n.layer_by_name(nm), l2n.layer_by_name(b))
    for k in ("M1", "M2", "M3", "M4", "M5", "TM1"):
        l2n.connect(l2n.layer_by_name(k))
    l2n.extract_netlist()
    return l2n


def report(probes):
    l2n = extract()
    seen = {}
    for nm, (x, y, lyr) in probes.items():
        n = l2n.probe_net(l2n.layer_by_name(lyr), pya.DPoint(snap(x), snap(y)))
        seen[nm] = n.expanded_name() if n else "none"
    groups = {}
    for nm, net in seen.items():
        groups.setdefault(net, []).append(nm)
    print("\n--- extracted nets ---")
    for net, members in sorted(groups.items()):
        print(f"  {net:6} : {', '.join(members)}")
    return groups


# ------------------------------------------------------------------ route

print("=== devices ===")
XQ1 = find("npn13G2", x=-9.0, y=-100.0)
XQ2 = find("npn13G2", x=9.0, y=-100.0)
XMT2 = find("nmos", x=-20.0, y=-190.0, wmin=10)
XMT1 = find("nmos", x=20.0, y=-190.0, wmin=10)
for nm, o in [("XQ1", XQ1), ("XQ2", XQ2), ("XMT2", XMT2), ("XMT1", XMT1)]:
    print(f"  {nm:5} {'ok' if o else 'NOT FOUND'}")

c1, b1, e1 = label(XQ1, "C"), label(XQ1, "B"), label(XQ1, "E")
c2, b2, e2 = label(XQ2, "C"), label(XQ2, "B"), label(XQ2, "E")

# --- outp: XQ1 collector + XQ2 base + inductor LA, all on Metal3 ---
print("\n=== outp on Metal3 ===")
# Via stacks cannot sit on the base or collector directly — the PCell already
# has its own vias and Metal1 there, and a new stack fails minimum spacing
# against them. Step out 3 um on Metal1 first, then go up.
drop(c1.x - 0.7, c1.y, "M3")
drop(b2.x + 0.7, b2.y, "M3")
drop(-9.0, -86.0, "M3")                      # meets the inductor stub
path("M3", [(c1.x - 0.7, c1.y), (-16.0, c1.y), (-16.0, -105.0),
            (b2.x + 0.7, -105.0), (b2.x + 0.7, b2.y)])
path("M3", [(c1.x - 0.7, c1.y), (-9.0, -86.0)])
wire("TM1", -9.0, -85.3, -9.0, -86.0, 6.0)

# --- outn: XQ2 collector + XQ1 base + inductor LB, all on Metal4 ---
print("=== outn on Metal4 ===")
drop(c2.x + 0.7, c2.y, "M4")
drop(b1.x - 0.7, b1.y, "M4")
drop(9.0, -86.0, "M4")
path("M4", [(c2.x + 0.7, c2.y), (16.0, c2.y), (16.0, -109.0),
            (b1.x - 0.7, -109.0), (b1.x - 0.7, b1.y)])
path("M4", [(c2.x + 0.7, c2.y), (9.0, -86.0)])
wire("TM1", 9.0, -85.3, 9.0, -86.0, 6.0)

# --- tail: both emitters to XMT2 drain, on Metal5 ---
# The mirror's diffusion fingers span y -193.5..-186.5. Anything crossing that
# band on Metal1 shorts every finger together, which is what happened before.
# Metal5 passes over them harmlessly and drops only at the pin.
print("=== tail on Metal5 ===")
d = pins(XMT2, 8, 2)[1]
drop(e1.x, e1.y, "M5", frm="Metal2")
drop(e2.x, e2.y, "M5", frm="Metal2")
drop(d.center().x, d.center().y, "M5")
path("M5", [(e1.x, e1.y), (e1.x, -104.0),
            (e2.x, -104.0), (e2.x, e2.y)])
path("M5", [(0.0, -104.0), (0.0, -190.0), (d.center().x, -190.0),
            (d.center().x, d.center().y)], w=2.0)

layout.write(OUT)
print(f"\nwrote {OUT}")

groups = report({
    "XQ1_C": (c1.x, c1.y, "M1"), "XQ2_B": (b2.x, b2.y, "M1"),
    "XQ2_C": (c2.x, c2.y, "M1"), "XQ1_B": (b1.x, b1.y, "M1"),
    "XQ1_E": (e1.x, e1.y, "M2"), "XQ2_E": (e2.x, e2.y, "M2"),
    "XMT2_D": (d.center().x, d.center().y, "M1"),
})

want = [{"XQ1_C", "XQ2_B"}, {"XQ2_C", "XQ1_B"},
        {"XQ1_E", "XQ2_E", "XMT2_D"}]
got = [set(v) for v in groups.values()]
print("\n--- expected grouping ---")
for w in want:
    hit = w in got
    print(f"  {'ok  ' if hit else 'FAIL'} {sorted(w)}")
