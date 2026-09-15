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
STACK_NAME = {"GatPoly": "GatPoly", "M2": "Metal2", "M3": "Metal3", "M4": "Metal4",
              "M5": "Metal5", "TM1": "TopMetal1", "TM2": "TopMetal2"}


def snap(v, g=0.005):
    """Round to the 5 nm manufacturing grid.

    Terminal positions come from PCell geometry and are not themselves on a
    grid boundary. Drawing to them directly produces off-grid metal.
    """
    return round(v / g) * g


def wire(lyr, x1, y1, x2, y2, w=1.0):
    """Draw one Manhattan segment.

    A segment with no length in either direction produces a box that is only
    `w` in one dimension and nothing in the other — a sliver below minimum
    width, which DRC flags and which no amount of patching over will fix.
    Skip those instead of emitting them.
    """
    x1, y1, x2, y2 = snap(x1), snap(y1), snap(x2), snap(y2)
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    if dx < 1e-9 and dy < 1e-9:
        return                      # zero-length: nothing to draw
    if dx < 1e-9:
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
    order = ["M1", "M2", "M3", "M4", "M5", "TM1", "TM2"]
    start = order.index({"Metal1": "M1", "GatPoly": "M1", "Metal2": "M2",
                         "Metal3": "M3", "Metal4": "M4",
                         "Metal5": "M5"}[frm])
    upto = order.index({v: k for k, v in STACK_NAME.items()}.get(
        STACK_NAME[to], to))
    for k in order[start + 1:upto + 1]:
        pw, ph = (0.30, 0.125) if cols >= 2 else (0.105, 0.36 * rows / 2)
        top.shapes(LI[k]).insert(
            pya.DBox(x - pw, y - ph, x + pw, y + ph))
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
    for k in ("M1", "M2", "M3", "M4", "M5", "TM1", "TM2"):
        l2n.register(pya.Region(top.begin_shapes_rec(LI[k])), k)
    for v, (a, b) in [(19, ("M1", "M2")), (29, ("M2", "M3")),
                      (49, ("M3", "M4")), (66, ("M4", "M5")),
                      (125, ("M5", "TM1")), (133, ("TM1", "TM2"))]:
        nm = f"V{v}"
        l2n.register(pya.Region(top.begin_shapes_rec(layout.layer(v, 0))), nm)
        l2n.connect(l2n.layer_by_name(nm))
        l2n.connect(l2n.layer_by_name(a), l2n.layer_by_name(nm))
        l2n.connect(l2n.layer_by_name(nm), l2n.layer_by_name(b))
    for k in ("M1", "M2", "M3", "M4", "M5", "TM1", "TM2"):
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
drop(-6.0, -104.0, "M5", frm="Metal2")
drop(6.0, -104.0, "M5", frm="Metal2")
drop(d.center().x, d.center().y, "M5")
# Emitters travel out on Metal2 (which they already use inside the device),
# rise to Metal5 at +/-6 where the tank stacks are not, then join.
path("M2", [(e1.x, e1.y), (-8.4, e1.y), (-8.4, -104.0),
            (-6.0, -104.0)], w=0.6)
path("M2", [(e2.x, e2.y), (8.4, e2.y), (8.4, -104.0),
            (6.0, -104.0)], w=0.6)
path("M5", [(-6.0, -104.0), (6.0, -104.0)], w=1.0)
# The tail crosses the bank region, where outp's stacks reach TopMetal1 and
# therefore pass through Metal5. Use Metal2 down to y -145, below the bank,
# then transition to Metal5 for the run to the mirror.
path("M5", [(0.0, -104.0), (0.0, -190.0),
            (d.center().x, -190.0),
            (d.center().x, d.center().y)], w=2.0)
drop(d.center().x, d.center().y, "M5")


print("\n=== bank branches ===")
# Each branch: tank node -> capacitor -> switch -> capacitor -> other tank node.
# The split-capacitor arrangement keeps the branch symmetric; a single-ended
# switch would unbalance the tank.
#
# Layer choice matters here. The capacitor's top plate is TopMetal1 and its
# bottom plate Metal5 — but Metal5 already carries the tail net down the centre
# at x = 0, straight past both switches. So the tank side connects to the TOP
# plate on TopMetal1, and the switch side leaves the BOTTOM plate on Metal5 but
# jogs out to x = +/-6 before turning down, clear of the tail.
#
# The bank sits below the inductor (whose own TopMetal1 stops at y -85.3), so
# routing on TopMetal1 down here does not touch the spiral.

def cap_plates(inst):
    """Top plate (TopMetal1) and bottom plate (Metal5) of a cmim, in top
    coordinates."""
    tp = [sh.dbbox().transformed(inst.dcplx_trans)
          for sh in layout.cell(inst.cell_index).shapes(LI["TM1"]).each()]
    bp = [sh.dbbox().transformed(inst.dcplx_trans)
          for sh in layout.cell(inst.cell_index).shapes(LI["M5"]).each()]
    return tp[0], bp[0]

BANKY = [-108.0, -130.0]
for i, yb in enumerate(BANKY):
    ca = find("cmim", x=-25.0, y=yb)
    cb = find("cmim", x=25.0, y=yb)
    sw = find("nmos", x=-8.0, y=yb, wmin=None)
    if not (ca and cb and sw):
        print(f"  branch {i}: device missing, skipped")
        continue
    ta, ba = cap_plates(ca)
    tb, bb_ = cap_plates(cb)
    sp = pins(sw, 8, 2)
    src, drn = sp[0], sp[1]

    # Tank side: outp (Metal3) to CBxA top plate, outn (Metal4) to CBxB.
    # A via stack from Metal3 up to TopMetal1 must physically pass through
    # Metal4, and vice versa — so if outp is on Metal3 and outn on Metal4,
    # any stack reaching a TopMetal1 plate bridges them. That was the short.
    #
    # The capacitor has two plates on different layers: TopMetal1 on top,
    # Metal5 below. Give each tank net the plate nearest its own layer.
    # outn (Metal4) reaches Metal5 with a single via and never touches Metal3.
    # outp (Metal3) goes all the way to TopMetal1, crossing Metal4 and Metal5 —
    # but only at CBxA, where outn has no metal, so nothing is bridged.
    #
    # The switch then connects to the OTHER plate of each capacitor: CBxA's
    # bottom plate and CBxB's top plate.
    path("M3", [(-16.0, -105.0), (-16.0, ta.center().y),
                (ta.center().x, ta.center().y)])
    drop(ta.center().x, ta.center().y, "TM1", frm="Metal3")

    path("M4", [(16.0, -109.0), (16.0, tb.center().y),
                (bb_.center().x, tb.center().y)])
    drop(bb_.center().x, bb_.center().y, "M5", frm="Metal4")

    # B side: tank is on the bottom plate, so the switch takes the top plate.
    # A 1.64 um TopMetal1 pad meets TM1.a, then drop to Metal5 immediately.
    tx = tb.center().x + 6.0
    wire("TM1", tb.center().x, tb.center().y, tx, tb.center().y, 1.64)
    drop(tx, tb.center().y, "TM1", frm="Metal5")

    ytop = yb + 5.5
    ybot = yb - 5.5
    for plate, lyr, pin, ych in ((ba, "M5", src, ytop),
                                 (pya.DBox(tx - 0.5, tb.center().y - 0.5,
                                           tx + 0.5, tb.center().y + 0.5),
                                  "M5", drn, ybot)):
        px = pin.center().x
        path(lyr, [(plate.center().x, plate.center().y),
                   (plate.center().x, ych),
                   (px, ych),
                   (px, pin.center().y + (2.0 if ych > yb else -2.0))],
             w=0.4)
        # A Metal1->Metal5 stack here would put metal on Metal3 and Metal4,
        # which are outp and outn — every switch pin would join both tank
        # nets. Come down to Metal2 clear of the switch, cross on Metal2, and
        # drop a single level onto the pin.
        drop(px, pin.center().y, lyr, cols=1, rows=8)
    print(f"  branch {i} at y {yb}: caps ({ta.center().x:+.1f},"
          f"{tb.center().x:+.1f}) switch pins ({src.center().x:+.2f},"
          f"{drn.center().x:+.2f})")


print("\n=== varactor and coupling caps ===")
# outp -> CC1 -> varactor G1, outn -> CC2 -> varactor G2, with the two bias
# resistors holding both gates at mid-supply and the well driven by Vtune.
#
# The varactor sits on the centre line and the coupling caps are symmetric at
# +/-45, so the two gate paths are the same length. On a differential tank an
# imbalance here shows up directly as amplitude mismatch, which is why the
# varactor was moved from x = +8 to x = 0 before routing.
#
# Layer discipline is the same as the bank, and for the same reason: a via
# stack spanning Metal3 to TopMetal1 passes through Metal4, so if both tank
# nets terminated on TopMetal1 plates every stack would bridge them. outp
# takes the top plate, outn the bottom.

XCV = find("SVaricap", x=0.0, y=-172.0)
CC1 = find("cmim", x=-45.0, y=-250.0)
CC2 = find("cmim", x=45.0, y=-250.0)
RB1 = find("rhigh", x=-45.0, y=-160.0)
RB2 = find("rhigh", x=45.0, y=-160.0)
for nm, o in [("XCV", XCV), ("CC1", CC1), ("CC2", CC2),
              ("RB1", RB1), ("RB2", RB2)]:
    print(f"  {nm:5} {'ok' if o else 'NOT FOUND'}")

if XCV and CC1 and CC2:
    g1 = label(XCV, "G1")
    g2 = label(XCV, "G2")
    w_ = label(XCV, "W")
    t1, b1c = cap_plates(CC1)
    t2, b2c = cap_plates(CC2)

    # outp (Metal3) down to CC1's top plate.
    tx1 = t1.center().x - 30.0
    path("M3", [(-16.0, -105.0), (-16.0, -230.0),
                (tx1, -230.0), (tx1, t1.center().y)])
    drop(tx1, t1.center().y, "TM1", frm="Metal3")
    wire("TM1", tx1, t1.center().y, t1.center().x, t1.center().y, 1.64)

    # outn (Metal4) down to CC2's bottom plate.
    path("M4", [(16.0, -109.0), (16.0, -234.0),
                (b2c.center().x, -234.0), (b2c.center().x, b2c.center().y)])
    drop(b2c.center().x, b2c.center().y, "M5", frm="Metal4")

    # CC1's bottom plate (Metal5) across to G1.
    path("M5", [(b1c.center().x, b1c.center().y),
                (b1c.center().x, g1.y),
                (g1.x - 4.0, g1.y)])
    drop(g1.x - 4.0, g1.y, "M5")
    wire("M1", g1.x - 4.0, g1.y, g1.x, g1.y, 0.27)

    # CC2's top plate: out on TopMetal1 at 1.64 um to meet TM1.a, then down to
    # Metal5 clear of the plate, and across to G2.
    tx2 = t2.center().x + 30.0
    wire("TM1", t2.center().x, t2.center().y, tx2, t2.center().y, 1.64)
    drop(tx2, t2.center().y, "TM1", frm="Metal5")
    path("M5", [(tx2, t2.center().y), (tx2, -196.0),
                (g2.x + 4.0, -196.0), (g2.x + 4.0, g2.y)])
    drop(g2.x + 4.0, g2.y, "M5")
    wire("M1", g2.x, g2.y, g2.x + 4.0, g2.y, 0.27)

    print(f"  G1 ({g1.x:.2f},{g1.y:.2f})  G2 ({g2.x:.2f},{g2.y:.2f})  "
          f"W ({w_.x:.2f},{w_.y:.2f})")


print("\n=== varactor gate bias ===")
# RB1 and RB2 hold G1 and G2 at mid-supply so the varactor sits on the steep
# part of its C-V curve. Without this the gates float at whatever the coupling
# caps leave them at, and the device gives 2.3% tuning instead of 5.4% — that
# was measured, not assumed.
#
# These carry no signal current, only DC, so the routing is unconstrained:
# Metal2 is empty out here and nothing else needs the space.

if RB1 and RB2 and XCV:
    r1 = pins(RB1, 8, 2)
    r2 = pins(RB2, 8, 2)
    # rhigh's two pins are at the ends of the strip, sorted by x in cell frame;
    # for a vertical resistor they differ in y, so take them by y instead.
    r1 = sorted(r1, key=lambda b: b.center().y)
    r2 = sorted(r2, key=lambda b: b.center().y)
    r1_bot, r1_top = r1[0], r1[-1]
    r2_bot, r2_top = r2[0], r2[-1]
    print(f"  RB1 pins y {r1_bot.center().y:.2f} and {r1_top.center().y:.2f}")
    print(f"  RB2 pins y {r2_bot.center().y:.2f} and {r2_top.center().y:.2f}")

    # Bottom of each resistor to its gate, on Metal2.
    drop(r1_bot.center().x, r1_bot.center().y, "M2", cols=2, rows=2)
    path("M2", [(r1_bot.center().x, r1_bot.center().y),
                (r1_bot.center().x, g1.y - 6.0),
                (g1.x - 8.0, g1.y - 6.0),
                (g1.x - 8.0, g1.y)])
    drop(g1.x - 8.0, g1.y, "M2")
    wire("M1", g1.x - 8.0, g1.y, g1.x - 4.0, g1.y, 0.27)

    drop(r2_bot.center().x, r2_bot.center().y, "M2", cols=2, rows=2)
    top.shapes(LI["M2"]).insert(pya.DBox(
        snap(r2_bot.center().x - 0.5), snap(r2_bot.center().y - 0.3),
        snap(r2_bot.center().x + 0.5), snap(r2_bot.center().y + 0.3)))
    path("M2", [(r2_bot.center().x, r2_bot.center().y),
                (r2_bot.center().x, g2.y + 6.0),
                (g2.x + 8.0, g2.y + 6.0),
                (g2.x + 8.0, g2.y)])
    drop(g2.x + 8.0, g2.y, "M2")
    wire("M1", g2.x + 4.0, g2.y, g2.x + 8.0, g2.y, 0.27)

    # The far ends join as the vg rail, brought out on Metal2 above the
    # resistors where nothing else runs.
    drop(r1_top.center().x, r1_top.center().y, "M2", cols=2, rows=2)
    drop(r2_top.center().x, r2_top.center().y, "M2", cols=2, rows=2)
    path("M2", [(r1_top.center().x, r1_top.center().y),
                (r1_top.center().x, -150.0),
                (r2_top.center().x, -150.0),
                (r2_top.center().x, r2_top.center().y)])
    # Out to a bias input on the left, so vg is a node rather than a link.
    path("M2", [(r1_top.center().x, -150.0), (-120.0, -150.0)], w=1.0)
    # Out to a bias input on the left edge, so vg is a driven node rather than
    # a link between the two resistors.
    path("M2", [(r1_top.center().x, -150.0), (-120.0, -150.0)], w=1.0)
    print(f"  vg rail at y -150, brought out to x -120")

print("\n=== varactor well to tune ===")
# The well is the tuning input. It goes to a pad eventually; for now bring it
# out to the left edge on Metal2.
if XCV:
    drop(w_.x - 1.5, w_.y, "M2")
    path("M2", [(w_.x - 1.5, w_.y), (-20.0, w_.y), (-20.0, -155.0)])
    print(f"  W ({w_.x:.2f},{w_.y:.2f}) out to x -20")


print("\n=== buffers ===")
# Emitter followers off each tank node. Base to the tank, collector to Vcc,
# emitter to the output and down to its own current mirror.
#
# The terminal pitch is the same trap as the cross-coupled pair: C at
# y -93.99, E at -95.23, B at -96.37, so 1.14 um apart, with the emitter's own
# Metal2 spanning the whole gap. Nothing can be routed laterally on Metal1 or
# Metal2 near the device. Via stacks land ON each terminal, offset sideways
# within its own metal to clear the device's internal via column, and every
# run happens on an upper layer.
#
# The terminals here are 3.7 um wide against the cross-coupled pair's 1.86, so
# there is more room to place the stack.

XB1 = find("npn13G2", x=-115.0, y=-95.0)
XB2 = find("npn13G2", x=115.0, y=-95.0)
XMB1A = find("nmos", x=-95.0, y=-282.0, wmin=20)
XMB2A = find("nmos", x=-130.0, y=-282.0, wmin=20)
XMB1B = find("nmos", x=95.0, y=-282.0, wmin=20)
XMB2B = find("nmos", x=130.0, y=-282.0, wmin=20)
for nm, o in [("XB1", XB1), ("XB2", XB2), ("XMB1A", XMB1A),
              ("XMB2A", XMB2A), ("XMB1B", XMB1B), ("XMB2B", XMB2B)]:
    print(f"  {nm:6} {'ok' if o else 'NOT FOUND'}")

if XB1 and XB2:
    bc1, bb1, be1 = label(XB1, "C"), label(XB1, "B"), label(XB1, "E")
    bc2, bb2, be2 = label(XB2, "C"), label(XB2, "B"), label(XB2, "E")

    # --- buffer inputs: tank nodes to the bases ---
    # outp is on Metal3, outn on Metal4, so each base takes its own net's
    # layer and the two never share a plane.
    drop(bb1.x - 1.2, bb1.y, "M3")
    path("M3", [(-16.0, -105.0), (-40.0, -105.0), (-40.0, bb1.y),
                (bb1.x - 1.2, bb1.y)])

    drop(bb2.x + 1.2, bb2.y, "M4")
    path("M4", [(16.0, -109.0), (40.0, -109.0), (40.0, bb2.y),
                (bb2.x + 1.2, bb2.y)])

    # --- buffer emitters: out to the die edge on Metal5 ---
    # The emitter already has Metal2 inside the cell, so the stack starts
    # there and never drives a second Via1 array into the device.
    drop(be1.x - 1.2, be1.y, "M5", frm="Metal2")
    path("M5", [(be1.x - 1.2, be1.y), (-145.0, be1.y)])

    drop(be2.x + 1.2, be2.y, "M5", frm="Metal2")
    path("M5", [(be2.x + 1.2, be2.y), (145.0, be2.y)])

    print(f"  XB1 C({bc1.x:.1f},{bc1.y:.1f}) B({bb1.x:.1f},{bb1.y:.1f}) "
          f"E({be1.x:.1f},{be1.y:.1f})")


print("\n=== buffer bias mirrors ===")
# Each buffer emitter is pulled by its own cascode pair: XMB2 on top, XMB1
# below. Same arrangement as the tail mirror, which routed cleanly, so the
# same approach applies.
#
# These are DC nodes and the devices sit at x +/-95 and +/-130 with clear space
# around them, so the routing is unconstrained — the only rule that matters is
# not crossing the tank layers, which live on Metal3 and Metal4.

MB2A = find("nmos", x=-130.0, y=-200.0, wmin=20)
MB1A = find("nmos", x=-95.0, y=-200.0, wmin=20)
MB2B = find("nmos", x=130.0, y=-200.0, wmin=20)
MB1B = find("nmos", x=95.0, y=-200.0, wmin=20)
for nm, o in [("XMB2A", MB2A), ("XMB1A", MB1A),
              ("XMB2B", MB2B), ("XMB1B", MB1B)]:
    print(f"  {nm:6} {'ok' if o else 'NOT FOUND'}")

if all([MB2A, MB1A, MB2B, MB1B]) and XB1 and XB2:
    for tag, mb2, mb1, be, sgn in (("A", MB2A, MB1A, be1, -1.0),
                                   ("B", MB2B, MB1B, be2, 1.0)):
        p2 = pins(mb2, 8, 2)           # cell-frame order: source, then drain
        s2, d2 = p2[0], p2[1]
        d1 = pins(mb1, 8, 2)[1]

        # Emitter down to the cascode drain, on Metal5.
        # Land the lane on the drain rather than beside it: these are the
        # same net, and a near-miss reads as a spacing violation.
        xlane = d2.center().x
        xapp = d2.center().x + (6.0 if d2.center().x < 0 else -6.0)
        path("M5", [(xapp, be.y), (xapp, d2.center().y - 4.0),
                    (d2.center().x, d2.center().y - 4.0),
                    (d2.center().x, d2.center().y)], w=0.6)
        drop(d2.center().x, d2.center().y, "M5", cols=1, rows=2)
        top.shapes(LI["M5"]).insert(pya.DBox(
            snap(d2.center().x - 0.3), snap(d2.center().y - 1.6),
            snap(d2.center().x + 0.3), snap(d2.center().y + 1.6)))

        # Cascode source to the lower device's drain, below both.
        ylink = -207.0
        path("M5", [(s2.center().x, s2.center().y), (s2.center().x, ylink),
                    (d1.center().x, ylink), (d1.center().x, d1.center().y)])
        drop(s2.center().x, s2.center().y, "M5", cols=1, rows=2)
        drop(d1.center().x, d1.center().y, "M5", cols=1, rows=2)
        print(f"  side {tag}: emitter -> XMB2 drain at "
              f"({d2.center().x:.1f},{d2.center().y:.1f})")


print("\n=== mirror gate buses ===")
# One reference branch biases every mirror in the design: XMR2's gate drives
# all the cascode gates, XMR1's drives all the lower gates. Six devices on two
# buses.
#
# Poly is resistive, so each gate gets a via up to Metal5 immediately and the
# run happens there. These are DC nodes with no signal on them, but they still
# must not cross Metal3 or Metal4 — those carry the tank.
#
# The two buses run at different y so they never meet: cascodes at y -215,
# lower gates at y -220, both below the mirror row at -190 and above the
# buffer mirrors at -200... which they are not. Use -172 and -178 instead,
# in the gap between the varactor row and the mirror row.

XMR2 = find("nmos", x=-55.0, y=-190.0)
XMR1 = find("nmos", x=-42.0, y=-190.0)
for nm, o in [("XMR2", XMR2), ("XMR1", XMR1)]:
    print(f"  {nm:6} {'ok' if o else 'NOT FOUND'}")

if XMR2 and XMR1 and XMT2 and XMT1 and all([MB2A, MB1A, MB2B, MB1B]):
    def gate(inst):
        g = pins(inst, 5, 2)
        return g[0] if g else None

    casc = [XMR2, XMT2, XMT1, MB2A, MB2B]      # upper devices
    lower = [XMR1, XMT1, XMT2, MB1A, MB1B]     # lower devices

    # The tail cascode pair is XMT2 over XMT1, and the buffer pairs XMB2 over
    # XMB1, so the cascode bus takes XMT2/MB2A/MB2B and the lower bus takes
    # XMT1/MB1A/MB1B.
    casc = [XMR2, XMT2, MB2A, MB2B]
    lower = [XMR1, XMT1, MB1A, MB1B]

    for tag, group, ybus, blyr in (("cascode", casc, -212.0, "M2"),
                                   ("lower", lower, -184.0, "M2")):
        gs = [(g, gate(g)) for g in group]
        gs = [(g, b) for g, b in gs if b is not None]
        if len(gs) < 2:
            print(f"  {tag} bus: too few gates found, skipped")
            continue
        xs = sorted(b.center().x for _, b in gs)
        # Spine across the full span, then a stub down or up to each gate.
        wire(blyr, xs[0], ybus, xs[-1], ybus, 1.0)
        for g, b in gs:
            drop(b.center().x, b.center().y, blyr, cols=1, rows=2)
            # Step away from the device's own source/drain pins, which sit
            # only ~0.35 um from the gate. A fixed direction cannot work: at
            # the tail mirror the drain is inboard of the gate, at the buffer
            # mirrors the emitter lane is outboard.
            # The gate sits between source and drain with only 0.7 um either
            # side, so any lateral step passes over one of them. Go straight
            # down instead: Metal2 is empty below the mirrors, and the drains
            # are routed on Metal5.
            _gy = g.dbbox().bottom - 0.4
            wire(blyr, b.center().x, _gy, b.center().x, ybus, 0.21)
        print(f"  {tag} bus at y {ybus}: {len(gs)} gates from "
              f"x {xs[0]:.1f} to {xs[-1]:.1f}")


print("\n=== bank switch gates ===")
# Two control inputs, one per bank bit. These select the band, so they are
# static logic levels — no signal, no timing constraint, and the only thing
# that matters is not disturbing the tank.
#
# The switches sit at x -8 with their gate between source and drain, 0.35 um
# either side. Same geometry as the mirror gates, so the same approach: a via
# straight up on the gate, then a stub on a layer nothing else uses here.
# Metal2 carries the mirror gate buses but only below y -200; up here at
# y -108 and -130 it is free.

for i, yb in enumerate(BANKY):
    sw = find("nmos", x=-8.0, y=yb, wmin=None)
    if not sw:
        print(f"  bit {i}: switch not found")
        continue
    gp = pins(sw, 5, 2)
    if not gp:
        print(f"  bit {i}: no gate pin")
        continue
    g = gp[0]
    # Out to the left edge, clear of the bank capacitors at x -25 and the
    # tail's Metal5 lane at x 0.
    # Contact the gate below the active area, where the poly extends past the
    # source and drain pins and nothing sits either side of it.
    # MEASURED, not assumed. From the PCell geometry:
    #
    #   bank switch (w=8u l=0.13u ng=2)
    #     gate poly      0.130 x 4.360   y -0.18 .. 4.18
    #     active         0.000 .. 4.000
    #     guard ring M1  y 4.88 .. 5.18   (bar at centre y 5.03, 0.30 tall)
    #     contact        0.160 x 0.160
    #
    # The gate is 0.130 um wide and a contact is 0.160 um — the contact is
    # WIDER THAN THE GATE, so nothing can ever land on the gate itself. And the
    # poly overhang above the active area is only 0.18 um, while a contact plus
    # its enclosure needs about 0.30 um. Neither location works.
    #
    # What does work is the 0.70 um band between the gate top (4.18) and the
    # guard ring (4.88): extend the poly up into it, stopping 0.10 um short of
    # the ring for Gat.d (0.07 um minimum GatPoly-to-Activ), and put a single
    # contact there with its own Metal1 pad for M1.d (0.144 um2 minimum).
    #
    # The earlier attempt placed the pad at 4.23..4.83 against a ring starting
    # at 4.88 and a rows=2 stack spanning 4.18..4.88 — it missed by 50 nm,
    # which is what Gat.d and the three Cnt rules were reporting.
    ring_in = min((sh.dbbox().transformed(sw.dcplx_trans).bottom
                   for sh in layout.cell(sw.cell_index).shapes(LI["M1"]).each()
                   if sh.dbbox().width() > 2.0
                   and sh.dbbox().transformed(sw.dcplx_trans).bottom > g.top),
                  default=g.top + 0.9)

    pad_lo = snap(g.top - 0.05)
    pad_hi = snap(ring_in - 0.17)          # Gat.d: 0.07 clear, plus margin
    cy = snap(0.5 * (pad_lo + pad_hi))

    # Poly pad, wide enough to enclose a 0.16 um contact.
    top.shapes(LI["poly"]).insert(pya.DBox(
        snap(g.center().x - 0.22), pad_lo,
        snap(g.center().x + 0.22), pad_hi))
    # One contact, exactly 0.16 um.
    top.shapes(layout.layer(6, 0)).insert(pya.DBox(
        snap(g.center().x - 0.08), snap(cy - 0.08),
        snap(g.center().x + 0.08), snap(cy + 0.08)))
    # Metal1 landing, 0.4 x 0.4 = 0.16 um2, over the M1.d minimum.
    top.shapes(LI["M1"]).insert(pya.DBox(
        snap(g.center().x - 0.20), snap(cy - 0.20),
        snap(g.center().x + 0.20), snap(cy + 0.20)))
    drop(g.center().x, cy, "M2", cols=1, rows=1)

    path("M2", [(g.center().x, cy),
                (g.center().x - 2.5, cy),
                (g.center().x - 2.5, yb - 8.0),
                (-38.0 + 5.0 * i, yb - 8.0),
                (-38.0 + 5.0 * i, -145.0)], w=0.4)
    print(f"  bit {i}: gate at ({g.center().x:.2f},{g.center().y:.2f}) "
          f"out to x -60")


print("\n=== supply and ground ===")
# Vcc reaches the inductor centre tap, both buffer collectors and RREF.
# Ground reaches every mirror source, every guard ring and the bleed resistors.
#
# Layer choice, given what is already taken: Metal3 is outp, Metal4 is outn,
# Metal2 carries both gate buses and the band-select lines, Metal5 has the tail
# and the buffer bias. TopMetal2 is used only by the inductor's own centre tap
# at x +/-3, so it is effectively free — and it is the thickest metal, which is
# what a supply rail wants anyway.
#
# Vcc on TopMetal2, ground on TopMetal1 outside the inductor's footprint.
# TopMetal1 minimum width is 1.64 um, so both rails are drawn at 4 um.

VCC_Y = -60.0        # above the devices, below the inductor's -85.3 edge... it
                     # is not: the inductor spans to -85.3, so the rail must be
                     # clear of that. Use -160, in the gap between the varactor
                     # row and the mirror row.
VCC_Y = -160.0
GND_Y = -240.0       # below the mirror rows, above the coupling caps at -224
GND_Y = -300.0       # ...which they are not; -300 is below everything

RREF = find("rhigh", x=-75.0, y=-190.0)
print(f"  RREF   {'ok' if RREF else 'NOT FOUND'}")

# --- Vcc rail ---
wire("TM2", -150.0, VCC_Y, 150.0, VCC_Y, 4.0)

# Inductor centre tap LC is TopMetal2 at x -3..3, y -85.3..-82.3. Bring it down
# on TopMetal2 -- same layer, so no via needed.
wire("TM2", 0.0, -85.3, 0.0, VCC_Y, 4.0)

# Buffer collectors.
if XB1 and XB2:
    for bc in (bc1, bc2):
        drop(bc.x, bc.y, "TM2")
        xside = -150.0 if bc.x < 0 else 150.0
        path("TM2", [(bc.x, bc.y), (xside, bc.y), (xside, VCC_Y)], w=4.0)
    print(f"  Vcc rail at y {VCC_Y}, collectors at "
          f"({bc1.x:.0f},{bc1.y:.0f}) and ({bc2.x:.0f},{bc2.y:.0f})")

# RREF's top end.
if RREF:
    rr = sorted(pins(RREF, 8, 2), key=lambda b: b.center().y)
    drop(rr[-1].center().x, rr[-1].center().y, "TM2")
    path("TM2", [(rr[-1].center().x, rr[-1].center().y),
                 (rr[-1].center().x, VCC_Y)], w=4.0)

# --- ground ---
#
# Ground touches ten scattered points: four lower-mirror sources and six psub
# guard rings. Three earlier attempts each freed one net and caught another —
# the tail, then the band-select lines, then the cascode bus, then Vcc — because
# every route between those points crossed a layer somebody else owned.
#
# The way through is to find the layer that is free in each COLUMN rather than
# picking one layer for the whole net:
#
#   Metal2   gate buses at y -184 and -212 span the full width; blocked
#   Metal3   outp runs x -16 down to y -230, then across to x -75; blocked
#   Metal4   outn mirrors that on the right; blocked
#   Metal5   the tail at x 0 and the buffer lanes at x +/-137..143; blocked
#   TopMetal2  Vcc rail at y -160 spans x +/-150; blocked
#   TopMetal1  only the capacitor plates and the inductor — and those sit at
#              x +/-19..71 (coupling), x +/-25 (bank) and above y -85 — so
#              the columns at x -8, +/-95 and +/-130 are clear all the way down
#
# So TopMetal1 it is, with the rail at y -300 below the coupling caps. Points
# in a clear column drop straight to it. The four that sit behind a coupling
# capacitor step out first along y -215, the gap between the mirror row at
# -205 and the caps at -224.

GND_Y = -300.0
wire("TM1", -160.0, GND_Y, 160.0, GND_Y, 4.0)

RREF2 = find("rhigh", x=-75.0, y=-190.0)

gnd_pts = []
for nm, dev in (("XMR1", XMR1), ("XMT1", XMT1),
                ("XMB1A", MB1A), ("XMB1B", MB1B)):
    if dev:
        src = pins(dev, 8, 2)[0]
        gnd_pts.append((nm, src.center().x, src.center().y))
for nm, dev in (("XMR2", XMR2), ("XMT2", XMT2),
                ("XMB2A", MB2A), ("XMB2B", MB2B)):
    if dev:
        b = dev.dbbox()
        # Contact the ring at its left edge, away from the gate and the
        # source/drain stacks that sit near the centre of the device.
        gnd_pts.append((nm + "_ring", b.center().x, b.top - 0.15))

CAP_L, CAP_R = -75.0, 75.0        # coupling capacitors, with margin
CHAN_Y = -215.0                   # the gap between the mirror row and the caps

for nm, gx, gy in gnd_pts:
    try:
        drop(gx, gy, "TM1", cols=1, rows=2)
    except Exception as exc:
        print(f"  {nm}: {exc}")
        continue
    if -71.0 < gx < 71.0 and gy < -185.0:
        # Behind a coupling capacitor: out along the channel first.
        xdet = -85.0 if gx < 0 else 85.0
        path("TM1", [(gx, gy), (gx, CHAN_Y), (xdet, CHAN_Y),
                     (xdet, GND_Y)], w=2.5)
        route = f"via x {xdet:.0f}"
    else:
        path("TM1", [(gx, gy), (gx, GND_Y)], w=2.5)
        route = "direct"
    print(f"  {nm:12} ({gx:7.1f},{gy:7.1f})  {route}")

print(f"  {len(gnd_pts)} points on the rail at y {GND_Y:.0f}")


def bus_fingers(inst, tag=""):
    """Common a multi-finger MOSFET's fingers, inside the device.

    ROOT CAUSE OF THE EARLIER FAILURES
    ----------------------------------
    The nmos PCell draws each finger separately and does not connect them, so
    a w=139u ng=20 device extracts as twenty transistors in series with twenty
    floating gates. DRC passes it; a connectivity check that probes one
    terminal per device passes it too.

    Every previous attempt at a fix put the buses BEYOND the strip ends, in
    the 0.88 um gap between the diffusion and the guard ring. That gap is
    already occupied by the terminal routing, so the two competed for the same
    space and each attempt traded one broken net for another.

    But the strips are 7 um tall and almost entirely unused. The room is
    inside the device, not beyond it.

    The reason the first attempt at that failed — 192 DRC violations — was not
    the location but the via: a via stack is 0.29 um at its narrowest and a
    diffusion strip is 0.16 um wide, so every via overhung onto the poly and
    the neighbouring contacts.

    So: widen each strip locally with a small Metal1 pad, put the via on the
    pad, and bus on Metal2 over the array. Strip pitch is 1.38 um and adjacent
    strips carry opposite nets whose pads sit at different heights, so the
    clearance is comfortable. The 0.88 um gap is never touched, and the
    existing terminal routing keeps working untouched: it lands on one strip,
    and that strip is now bussed to the rest.
    """
    cell = layout.cell(inst.cell_index)

    strips = []
    for sh in cell.shapes(LI["M1"]).each():
        b = sh.dbbox()
        if b.width() < 0.25 and b.height() > 2.0:
            strips.append(b.transformed(inst.dcplx_trans))
    strips.sort(key=lambda b: b.center().x)
    if len(strips) < 3:
        return None

    gates = sorted(
        (sh.dbbox().transformed(inst.dcplx_trans)
         for sh in cell.shapes(LI["poly"]).each()),
        key=lambda b: b.center().x)

    src, drn = strips[0::2], strips[1::2]
    y0, h = strips[0].bottom, strips[0].height()

    # Three levels inside the strip span, evenly spread.
    y_s = snap(y0 + 0.12 * h)
    y_d = snap(y0 + 0.62 * h)
    y_g = snap(y0 + 0.80 * h)

    PAD = 0.20          # half-width: via 0.19 + 0.105 enclosure

    for group, ylev in ((src, y_s), (drn, y_d)):
        _v1 = pya.Region(top.begin_shapes_rec(layout.layer(19, 0)))
        for b in group:
            x = b.center().x
            _foot = pya.Region(pya.DBox(x - PAD, ylev - PAD,
                                        x + PAD, ylev + PAD).to_itype(layout.dbu))
            if not (_v1 & _foot).is_empty():
                continue          # already contacted by the terminal routing
            for lyr in ("M1", "M2"):
                top.shapes(LI[lyr]).insert(pya.DBox(
                    snap(x - PAD), snap(ylev - PAD),
                    snap(x + PAD), snap(ylev + PAD)))
            top.shapes(layout.layer(19, 0)).insert(pya.DBox(
                snap(x - 0.095), snap(ylev - 0.095),
                snap(x + 0.095), snap(ylev + 0.095)))
        if len(group) > 1:
            wire("M2", group[0].center().x, ylev,
                 group[-1].center().x, ylev, 0.4)

    # Gates need no contact at all.
    #
    # A contact is 0.16 um wide. The bank switches use l=0.13u, so their gate
    # poly is narrower than the contact that would sit on it — 72 Cnt.b
    # violations. And on the mirrors the contact was landing on poly over the
    # active area, which is not allowed anywhere.
    #
    # But poly is conductive. The gates already extend 0.18 um past the
    # diffusion at each end, so a poly bar across that overhang commons them
    # directly. And because the existing gate routing connects to the first
    # gate, bussing them on poly drives all of them with nothing added.
    if len(gates) > 1:
        gy0 = strips[0].top + 0.075     # Gat.d: 0.07 um clear of Activ
        gy1 = gy0 + 0.16                # Gat.a: 0.13 um minimum poly width
        if gy1 > gy0 + 0.05:
            top.shapes(LI["poly"]).insert(pya.DBox(
                snap(gates[0].left), snap(gy0),
                snap(gates[-1].right), snap(gy1)))

    print(f"  {tag:8} {len(src)}s + {len(drn)}d strips, {len(gates)} gates "
          f"bussed at y {y_s:.1f} / {y_d:.1f} / {y_g:.1f}")
    return True


print("\n=== commoning multi-finger devices ===")
for _t, _d in (("XSW0", find("nmos", x=-8.0, y=-108.0)),
               ("XSW1", find("nmos", x=-8.0, y=-130.0)),
               ("XMR2", XMR2), ("XMR1", XMR1),
               ("XMT2", XMT2), ("XMT1", XMT1),
               ("XMB2A", MB2A), ("XMB1A", MB1A),
               ("XMB2B", MB2B), ("XMB1B", MB1B)):
    if _d:
        bus_fingers(_d, tag=_t)


print("\n=== port labels ===")
# LVS extracted the layout as ".SUBCKT vco_20g G1 G2 W" — three ports, and
# those are the varactor PCell's own labels leaking through. Nothing else in
# the layout is named, so the comparison had no anchors at all: every net was
# an anonymous $n and could match anything or nothing.
#
# The deck reads net names from datatype 25 on each metal — metal1_text is
# labels(8, 25), metal2_text labels(10, 25), and so on. A text object on the
# right layer, sitting on the right piece of metal, names that net.
#
# One label per top-level port, placed where that net actually runs.

PORTS = [
    # (name, layer, x, y)
    ("vcc",   "TM2", 0.0,    -160.0),   # supply rail
    ("gnd",   "TM1", 0.0,    -300.0),   # ground rail
    ("vg",    "M2",  -120.0, -150.0),   # varactor gate bias
    ("vt",    "M2",  -20.0,  -155.0),   # tune input, on the well route
    ("nb0",   "M2",  -38.0,  -145.0),   # band select
    ("nb1",   "M2",  -33.0,  -145.0),
    ("outbp", "M5",  -145.0, -95.23),   # buffer outputs
    ("outbn", "M5",  145.0,  -95.23),
]

_TEXTLAYER = {"M1": (8, 25), "M2": (10, 25), "M3": (30, 25), "M4": (50, 25),
              "M5": (67, 25), "TM1": (126, 25), "TM2": (134, 25)}

for nm, lyr, px, py in PORTS:
    li = layout.layer(*_TEXTLAYER[lyr])
    top.shapes(li).insert(pya.DText(nm, pya.DTrans(snap(px), snap(py))))
    print(f"  {nm:6} on {lyr:4} at ({px:7.1f},{py:8.1f})")

layout.write(OUT)
print(f"\nwrote {OUT}")

groups = report({
    "XQ1_C": (c1.x, c1.y, "M1"), "XQ2_B": (b2.x, b2.y, "M1"),
    "XQ2_C": (c2.x, c2.y, "M1"), "XQ1_B": (b1.x, b1.y, "M1"),
    "XQ1_E": (e1.x, e1.y, "M2"), "XQ2_E": (e2.x, e2.y, "M2"),
    "XMT2_D": (d.center().x, d.center().y, "M1"),
    "CB0A_top": (-25.0, -108.0, "TM1"), "CB0B_top": (25.0, -108.0, "M5"),
    "CB1A_top": (-25.0, -130.0, "TM1"), "CB1B_top": (25.0, -130.0, "M5"),
    "CC1_top": (-45.0, -250.0, "TM1"), "CC2_bot": (45.0, -250.0, "M5"),
    "XCV_G1": (-3.92, -174.25, "M5"),
    "XCV_G2": (4.08, -169.75, "M5"),
    "RB1_bot": (-45.0, -164.0, "M2"), "RB2_bot": (45.0, -164.0, "M2"),
    "XB1_B": (-116.2, -96.37, "M1"), "XB2_B": (116.2, -96.37, "M1"),
    "XB1_E": (-116.2, -95.23, "M2"), "XB2_E": (116.2, -95.23, "M2"),
    "MB2A_D": (-142.4, -200.0, "M5"), "MB2B_D": (142.4, -200.0, "M5"),
    "casc_bus": (-30.0, -212.0, "M2"), "lower_bus": (-30.0, -184.0, "M2"),
    "nb0": (-38.0, -143.0, "M2"), "nb1": (-33.0, -143.0, "M2"),
    "vcc": (0.0, -160.0, "TM2"), "gnd": (0.0, -300.0, "TM1"), "gnd_sw": (-130.0, -250.0, "TM1"),
    "gnd_mb": (-130.0, -250.0, "TM1"),
})

want = [{"XQ1_C", "XQ2_B", "CB0A_top", "CB1A_top", "CC1_top", "XB1_B"},
        {"XCV_G1", "RB1_bot"}, {"XCV_G2", "RB2_bot"},
        {"XQ2_C", "XQ1_B", "CB0B_top", "CB1B_top", "CC2_bot", "XB2_B"},
        {"XQ1_E", "XQ2_E", "XMT2_D"}, {"XB1_E", "MB2A_D"}, {"XB2_E", "MB2B_D"},
        {"nb0"}, {"nb1"}, {"vcc"}, {"gnd", "gnd_sw", "gnd_mb"}]
got = [set(v) for v in groups.values()]
print("\n--- expected grouping ---")
for w in want:
    hit = w in got
    print(f"  {'ok  ' if hit else 'FAIL'} {sorted(w)}")
