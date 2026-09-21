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
XMR2 = find("nmos", x=-55.0, y=-190.0)
XMR1 = find("nmos", x=-42.0, y=-190.0)
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
path("M4", [(c2.x + 0.7, c2.y), (16.0, c2.y), (16.0, -103.0),
            (b1.x - 0.7, -103.0), (b1.x - 0.7, b1.y)])
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
            (d.center().x, d.center().y)], w=0.6)
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
    _tax = ta.center().x - 6.0
    wire("TM1", ta.center().x, ta.center().y, _tax, ta.center().y, 1.64)
    path("M3", [(-16.0, -105.0), (-16.0, ta.center().y),
                (_tax, ta.center().y)])
    drop(_tax, ta.center().y, "TM1", frm="Metal3")

    # MEASURED: this route drew Metal4 at y -109.5..-108.5 running from
    # x -9.700 to +16.000, straight across XSW0 whose strips span y -110..-106
    # at x -8.51 and -8.00. Both switch stacks reach Metal4 on their way to
    # Metal5, so the route shorted the switch's source to its drain — the last
    # of the four drain-source shorts, and present since the bank was first
    # wired, long before any finger commoning.
    #
    # The capacitors sit at x +/-25 and the switch at x -8, so the horizontal
    # leg has to pass the switch's column. Move it out of the device's row
    # instead: the strips end at y -106.0, so routing at the capacitor's own y
    # minus a clear 6 um puts it below the device entirely.
    _ybr = tb.center().y - 6.0
    path("M4", [(16.0, -103.0), (16.0, _ybr),
                (bb_.center().x, _ybr),
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
        if ych == ybot:
            # MEASURED: the B-side capacitor is at x +25 and its switch at
            # x -8, so this horizontal crosses x = 0 — where the tail runs on
            # Metal5 from y -104 to -190. Both bank rows (y -113.5, -135.5)
            # fall inside that span, so S0B and S1B extracted as E: the B-side
            # switch nodes were shorted to the tail.
            #
            # Cross on Metal3 instead. At these heights Metal3 holds nothing
            # between x -8 and +31 (outp is at x -16), and the via corners are
            # clear of outn's Metal4 (at x +16 and along y -103).
            _px0 = plate.center().x
            path("M5", [(_px0, plate.center().y), (_px0, ych)], w=0.4)
            drop(_px0, ych, "M5", cols=2, rows=2, frm="Metal3")
            path("M3", [(_px0, ych), (px, ych)], w=0.4)
            drop(px, ych, "M5", cols=2, rows=2, frm="Metal3")
            path("M5", [(px, ych),
                        (px, pin.center().y - 1.4)], w=0.3)
        else:
            path(lyr, [(plate.center().x, plate.center().y),
                       (plate.center().x, ych),
                       (px, ych),
                       (px, pin.center().y + 1.4)],
                 w=0.3)
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
    path("M4", [(16.0, -103.0), (16.0, -234.0),
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
    path("M4", [(16.0, -103.0), (40.0, -103.0), (40.0, bb2.y),
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

    _pitch = (strips[1].center().x - strips[0].center().x
              if len(strips) > 1 else 1.38)
    PAD = 0.16 if _pitch < 0.75 else 0.20

    for group, ylev in ((src, y_s), (drn, y_d)):
        # A terminal with a single strip needs nothing: the strip IS the
        # terminal and the existing routing already lands on it. Drawing a pad
        # and via there adds metal beside the opposite terminal for no gain —
        # on XSW1 the drain is one strip, and its stray pad is what tied the
        # device to its own gate net.
        if len(group) < 2:
            continue
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
            # MEASURED on XSW0: the strips span y -110.00..-106.00, so a bus
            # at y_s = y0 + 0.12h sits at -109.52 and, 0.4 um wide, spans
            # -109.72..-109.32. The DRAIN strip's Metal2 runs -109.440..
            # -106.560. They overlap by 0.12 um, which is what shorts drain to
            # source on every device where the two levels are close enough.
            #
            # A bus drawn across the array always crosses the opposite net,
            # because the strips interdigitate. So the bus goes OUTSIDE the
            # strip span, and each strip reaches it by a stub at its own x —
            # and a stub at a source x never overlaps a drain strip's x, so
            # nothing crosses.
            #
            # Space available (measured): strip ends at -110.00, guard ring
            # Metal1 starts at -110.88, and Metal2 is empty in that 0.88 um
            # band. Same above, between -106.00 and -105.12.
            _out = (snap(strips[0].bottom - 0.70) if ylev == y_s
                    else snap(strips[0].top + 0.30))
            # MEASURED on XSW1: the drain bus runs up to strips.top + 0.45,
            # and the band-select gate contact sits at the same height with a
            # poly pad spanning x -9.115..-8.415. The drain stub at x -8.51
            # spans -8.64..-8.38 and overlaps it, tying the drain to nb1.
            #
            # The gate sits on the low side of the first drain strip, so
            # offsetting the drain stubs the other way clears it. Sources go
            # down and need no offset: nothing is below them but the ring.
            _mir = -1.0 if inst.dcplx_trans.is_mirror() else 1.0
            _dx = _mir * 0.25 if ylev == y_d else 0.0
            for b in group:
                wire("M2", b.center().x, ylev,
                     b.center().x + _dx + 0.13, ylev, 0.26)
                wire("M2", b.center().x + _dx, ylev,
                     b.center().x + _dx, _out, 0.26)
                # At the switches' 0.51 um pitch the stub and its own strip's
                # stack are joined only by the jog, leaving a 15 nm slit beside
                # the stack (drains) or an 0.08 um gap above it (sources) -
                # same-net slots that M2.b flags. Fill between stack and stub,
                # reaching 0.1 um into the stack; the outer edge stays the
                # stub's, so nothing moves toward the neighbouring strip.
                _pt = (strips[1].center().x - strips[0].center().x
                       if len(strips) > 1 else 9.9)
                if _pt < 0.75:
                    _ylo, _yhi = sorted((ylev, _out))
                    if _out < ylev:
                        _yhi += 0.1
                    else:
                        _ylo -= 0.1
                        # The slit is beside the stack only; stop at the strip
                        # top. Carried up to the drain bus it reached within
                        # 0.045 um of the band-select gate contact.
                        _yhi = min(_yhi, b.top - 0.3)
                    _sx = b.center().x + _dx
                    top.shapes(LI["M2"]).insert(pya.DBox(
                        min(b.center().x - 0.105, _sx - 0.13), _ylo,
                        max(b.center().x + 0.105, _sx + 0.13), _yhi))
            wire("M2", group[0].center().x + _dx - 0.13, _out,
                 group[-1].center().x + _dx + 0.13, _out, 0.26)

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
        gy1 = strips[0].top + 0.750     # tall enough to hold a contact
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

# The gate bus runs AFTER the commoning: it contacts the poly bar that
# bus_fingers draws and reads what the commoning records. Running it
# before — as the file originally did — placed the contact before the bar
# existed, which is why all eight mirror gates extracted as isolated nets
# and the tail and buffer current sources had no bias at all.

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
        # The spine must reach every jogged stub, and it is drawn before the
        # stubs, so compute the jog position directly from each instance.
        xs = sorted(snap(g.dbbox().left + 0.6) for g, _ in gs)
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
            # MEASURED on XMT2: the commoning's drain bar spans x -25.400 to
            # -14.100, and the contact at the marked gate pin (x -20) lands on
            # it — which is why every cascode gate extracted shorted to its own
            # drain.
            #
            # But the leftmost gate is at x -26.36, outside the drain bar's
            # span: the bar runs between the inner strips while the first gate
            # sits left of them. The poly bar commons every gate, so contacting
            # the leftmost one carries the whole gate and touches nothing.
            _polys = sorted(
                (sh.dbbox().transformed(g.dcplx_trans)
                 for sh in layout.cell(g.cell_index).shapes(LI["poly"]).each()),
                key=lambda q: q.center().x)
            if not _polys:
                continue
            _gy = snap(g.dbbox().top - 1.21 + 0.41)
            # 0.1 um left of the gate centre, still on the 1 um gate: clears
            # the mirrored devices' drain bar (measured 0.16 um -> 0.26 um).
            _x = snap(_polys[0].center().x - 0.1)
            # MEASURED: the commoning's SOURCE bus runs below each device,
            # spanning the source strips in x. The gate stub descending to the
            # gate bus at y -212 passed straight through it — every cascode
            # gate extracted shorted to its own source.
            #
            # Jog left, outside the source bus span, before descending. The
            # guard ring there is Metal1 and the stub is Metal2, so only the
            # source bus has to be cleared: 0.6 um in from the instance's left
            # edge is outside every strip and outside the bus.
            _xj = snap(g.dbbox().left + 0.6)
            top.shapes(layout.layer(6, 0)).insert(
                pya.DBox(_x - 0.08, _gy - 0.08, _x + 0.08, _gy + 0.08))
            for _l in ("M1", "M2"):
                top.shapes(LI[_l]).insert(
                    pya.DBox(_x - 0.15, _gy - 0.15, _x + 0.15, _gy + 0.15))
            top.shapes(layout.layer(19, 0)).insert(
                pya.DBox(_x - 0.095, _gy - 0.095, _x + 0.095, _gy + 0.095))
            wire(blyr, _x, _gy, _xj, _gy, 0.26)
            wire(blyr, _xj, _gy, _xj, ybus, 0.26)
            top.shapes(LI[blyr]).insert(
                pya.DBox(_xj - 0.13, _gy - 0.13, _xj + 0.13, _gy + 0.13))
        print(f"  {tag} bus at y {ybus}: {len(gs)} gates from "
              f"x {xs[0]:.1f} to {xs[-1]:.1f}")




print("\n=== reference branch diode connections ===")
# The netlist has MMR2 = NC NC NB and MMR1 = NB NB GND: each reference device
# has its gate tied to its own drain. That connection sets the bias voltage the
# gate buses distribute, and it was never routed — so the buses carried a net
# with nothing driving it.
#
# MEASURED on both devices: three strips, sources outside at +/-1.38 um, drain
# in the middle, strips spanning y -192.5..-187.5. The gate contact sits on the
# poly bar above the strips. Link them on Metal2: a via on the drain strip just
# inside its top end, then up to the contact height and across to the gate.
for _tag, _dev in (("XMR2", XMR2), ("XMR1", XMR1)):
    if not _dev:
        continue
    _c = layout.cell(_dev.cell_index)
    _strips = sorted(
        (sh.dbbox().transformed(_dev.dcplx_trans)
         for sh in _c.shapes(LI["M1"]).each()
         if sh.dbbox().width() < 0.25 and sh.dbbox().height() > 2),
        key=lambda q: q.center().x)
    _polys = sorted(
        (sh.dbbox().transformed(_dev.dcplx_trans)
         for sh in _c.shapes(LI["poly"]).each()),
        key=lambda q: q.center().x)
    if len(_strips) < 3 or not _polys:
        print(f"  {_tag}: geometry not as expected, skipped")
        continue
    _drn = _strips[1]
    _dx = snap(_drn.center().x)
    _dy = snap(_drn.top - 0.5)
    _gx = snap(_polys[0].center().x)
    _gy = snap(_dev.dbbox().top - 1.21 + 0.41)
    for _l in ("M1", "M2"):
        top.shapes(LI[_l]).insert(
            pya.DBox(_dx - 0.15, _dy - 0.15, _dx + 0.15, _dy + 0.15))
    top.shapes(layout.layer(19, 0)).insert(
        pya.DBox(_dx - 0.095, _dy - 0.095, _dx + 0.095, _dy + 0.095))
    # The Metal2 above XMR2's drain at y -186.80..-186.08 is the guard ring's
    # GROUND stack, not the drain's own - a link at the contact height ran
    # 0.16 um below it, and extending into it tied NC to ground. Run the
    # horizontal 0.3 um lower (0.46 um clear) and step up to the contact.
    _gl = _gy - 0.3
    wire("M2", _dx, _dy, _dx, _gl, 0.26)
    wire("M2", _dx, _gl, _gx, _gl, 0.26)
    wire("M2", _gx, _gl, _gx, _gy, 0.26)
    for _cx in (_dx, _gx):
        top.shapes(LI["M2"]).insert(
            pya.DBox(_cx - 0.13, _gl - 0.13, _cx + 0.13, _gl + 0.13))
    # On XMR1 the Metal3 link lands on this same drain via, and its pad leaves
    # a 0.175 um slot below the lowered horizontal. Both are this drain's own
    # metal (NB), so fill between them.
    top.shapes(LI["M2"]).insert(
        pya.DBox(_dx - 0.35, _dy, _dx + 0.13, _gl + 0.13))
    print(f"  {_tag}: drain ({_dx:.2f},{_dy:.2f}) tied to gate ({_gx:.2f},{_gy:.2f})")


print("\n=== XMR2 source to NB ===")
# The netlist has MMR2 = NC NC NB: XMR2's source is the NB node, which is
# XMR1's drain and gate. After the diode connections XMR2 extracts as
# "$44 $17 $17" — its source on a net of its own.
#
# A Metal2 link from XMR2's source bus to XMR1 would cross XMR1's own source
# strip at x -43.38, which is ground. MEASURED: Metal3 between the two devices
# holds only two via-stack pieces, at y -186.8..-186.1 near x -55 and at
# y -190.4..-189.6 near x -43.4. A Metal3 path up from XMR2's source bus at
# x -53.62, across at y -187.5, and down onto XMR1's diode link at x -42.00
# touches neither.
if XMR2 and XMR1:
    def _strips(d):
        return sorted(
            (sh.dbbox().transformed(d.dcplx_trans)
             for sh in layout.cell(d.cell_index).shapes(LI["M1"]).each()
             if sh.dbbox().width() < 0.25 and sh.dbbox().height() > 2),
            key=lambda q: q.center().x)
    _s2 = _strips(XMR2)
    _s1 = _strips(XMR1)
    _xa = snap(_s2[-1].center().x)            # XMR2 rightmost source strip
    _ya = snap(_s2[-1].bottom - 0.45)          # its source bus, below
    _xb = snap(_s1[1].center().x)              # XMR1 drain strip
    _yb = snap(_s1[1].top - 0.5)               # the diode link pad
    _yr = snap(_s1[1].top)                     # route height on Metal3
    drop(_xa, _ya, "M3", cols=2, rows=2, frm="Metal2")
    drop(_xb, _yb, "M3", cols=2, rows=2, frm="Metal2")
    path("M3", [(_xa, _ya), (_xa, _yb), (_xb, _yb)], w=0.3)
    print(f"  XMR2 source ({_xa:.2f},{_ya:.2f}) -> XMR1 drain ({_xb:.2f},{_yb:.2f}) on Metal3")


print("\n=== tail cascode link (NTX) ===")
# Netlist: MMT2 = E NC NTX and MMT1 = NTX NB GND — XMT2's source must be XMT1's
# drain. Extraction showed them on separate nets: the cascode was never stacked.
#
# MEASURED:
#   XMT2 (not mirrored): the tail lands on its odd strips, so its EVEN strips,
#     bussed below at strips.bottom - 0.45, are NTX.
#   XMT1 (mirrored): ground lands on its even strips, so its ODD strips,
#     bussed above at strips.top + 0.30, are NTX.
#   Metal3 is empty across the whole gap between them; Metal2 carries the lower
#     gate bus at y -184 and Metal5 carries the tail.
#
# Route on Metal3: up from XMT2's source bus at its rightmost strip, across
# below both devices, and up into XMT1's drain bus at its SECOND drain strip —
# the first sits within 0.2 um of XMT1's gate contact.
if XMT2 and XMT1:
    def _st(d):
        return sorted(
            (sh.dbbox().transformed(d.dcplx_trans)
             for sh in layout.cell(d.cell_index).shapes(LI["M1"]).each()
             if sh.dbbox().width() < 0.25 and sh.dbbox().height() > 2),
            key=lambda q: q.center().x)
    _t2 = _st(XMT2)
    _t1 = _st(XMT1)
    _xa = snap(_t2[0::2][-1].center().x)      # XMT2 rightmost even strip
    _ya = snap(_t2[0].bottom - 0.45)          # XMT2 source bus
    _xb = snap(_t1[1::2][1].center().x)       # XMT1 second odd strip
    _yb = snap(_t1[0].top + 0.30)             # XMT1 drain bus
    drop(_xa, _ya, "M3", cols=2, rows=2, frm="Metal2")
    drop(_xb, _yb, "M3", cols=2, rows=2, frm="Metal2")
    path("M3", [(_xa, _ya), (_xb, _ya), (_xb, _yb)], w=0.3)
    print(f"  XMT2 source ({_xa:.2f},{_ya:.2f}) -> XMT1 drain ({_xb:.2f},{_yb:.2f}) on Metal3")


print("\n=== RREF to NC ===")
# RREF extracted as "$37 vcc": its upper end reaches the supply, its lower end
# reaches nothing. Without it on NC the reference branch carries no current and
# no mirror in the design is biased.
#
# NC is XMR2's diode-connected node. The gate stub jogged to XMR2's left edge
# (instance.left + 0.6) carries NC vertically from the gate contact down to
# the cascode bus at y -212, so RREF can simply join it.
#
# RREF's lower pin is below XMR2's bbox (-193.71), and XMR2's source bus sits
# at y -192.95 spanning x -56.51..-53.49 — a Metal2 run at the pin's height
# meets the stub 0.79 um clear of it.
if RREF and XMR2:
    _rr = sorted(pins(RREF, 8, 2), key=lambda q: q.center().y)
    _lo = _rr[0]
    _sx = snap(XMR2.dbbox().left + 0.6)
    _ly = snap(_lo.center().y)
    drop(_lo.center().x, _ly, "M2", cols=2, rows=2)
    path("M2", [(_lo.center().x, _ly), (_sx, _ly)], w=0.3)
    print(f"  RREF lower pin ({_lo.center().x:.2f},{_ly:.2f}) -> NC stub at x {_sx:.2f}")


print("\n=== CT to the tank ===")
# CT extracted floating: neither plate touched the tank. It is 31.6 fF of the
# tank capacitance, so floating it shifts the oscillation frequency.
#
# MEASURED:
#   CT top plate TopMetal1  x 18.11..21.89  y -96.89..-93.11
#   CT bottom plate Metal5  x 17.13..22.86  y -97.86..-92.14
#   outn on Metal4 spans x 5..30 with its top edge at y -98.59
#   outp on Metal3 at XQ2's base, x 9.2..10.2, y -104..-101.24
#   and outn's collector stack crosses Metal3 at x 9.40..10.00, y -99.2..-99.0
#
# Same plate discipline as the rest of the tank: outn takes the bottom plate,
# outp the top.
CT = find("cmim", x=20.0, y=-95.0)
if CT:
    # outn: a short Metal4 stub up from its column into the bottom plate,
    # then Metal4 -> Metal5. The via lands on the bottom plate only.
    path("M4", [(20.0, -103.0), (20.0, -97.4)], w=0.6)
    drop(20.0, -97.4, "M5", cols=2, rows=2, frm="Metal4")

    # outp: TopMetal1 extended left out of the plate, dropped at x 12 — outside
    # the bottom plate, so the stack cannot bridge the two plates. Reach it on
    # Metal3 by stepping right from XQ2's base region first, clear of outn's
    # collector stack at x 9.4..10.0.
    wire("TM1", 20.0, -95.0, 12.0, -95.0, 1.64)
    drop(12.0, -95.0, "TM1", cols=2, rows=2, frm="Metal3")
    path("M3", [(10.0, -102.5), (12.0, -102.5), (12.0, -95.0)], w=0.4)
    print("  CT bottom plate -> outn (M4), top plate -> outp (M3 via x 12)")


print("\n=== bleed resistors ===")
# Netlist: RBL0A S0A GND, RBL0B S0B GND, RBL1A S1A GND, RBL1B S1B GND. All four
# extracted floating — they were placed at the die edge and never routed.
#
# MEASURED: bleeds at (+/-150, -225) with pins at y -262.14 / -187.86, and at
# (+/-150, -310) with pins at y -347.14 / -272.86. Ground on TopMetal1 spans the
# width with its rail at y -300.
#
# Each upper pin goes to its switch node: a vertical at the bleed's column,
# then a horizontal at the node's height to the capacitor plate that carries
# it. Each lower pin goes straight to the ground rail on TopMetal1.
#
# Every segment is checked against the metal already drawn, on its layer,
# before it is placed. Endpoints are excluded from the check, since they are
# meant to touch. A segment that would touch anything else is refused and
# reported rather than drawn.
_LN = {"M2": (10, 0), "M3": (30, 0), "M4": (50, 0), "M5": (67, 0),
       "TM1": (126, 0), "TM2": (134, 0)}
_STK = {"M2": "Metal2", "M3": "Metal3", "M4": "Metal4", "M5": "Metal5"}

def _occupied(lyr):
    return pya.Region(top.begin_shapes_rec(layout.layer(*_LN[lyr]))).merged()

def _seg_clear(lyr, x0, y0, x1, y1, w, keep):
    reg = _occupied(lyr)
    h = w / 2 + 0.25                      # track half-width plus clearance
    box = pya.DBox(min(x0, x1) - h, min(y0, y1) - h,
                   max(x0, x1) + h, max(y0, y1) + h)
    hit = reg & pya.Region(box.to_itype(layout.dbu))
    for kx, ky in keep:                   # endpoints are meant to touch
        hit -= pya.Region(pya.DBox(kx - 1.2, ky - 1.2,
                                   kx + 1.2, ky + 1.2).to_itype(layout.dbu))
    return hit.is_empty()

def _bleed(tag, rinst, tap_x, tap_y, tap_layer):
    if not rinst:
        print(f"  {tag}: resistor not found")
        return
    pp = sorted(pins(rinst, 8, 2), key=lambda q: q.center().y)
    lo, hi = pp[0], pp[-1]
    bx = snap(hi.center().x)
    hy = snap(hi.center().y)
    for lyr in ("M4", "M3", "M2"):
        ok_v = _seg_clear(lyr, bx, hy, bx, tap_y, 0.4, [(bx, hy)])
        ok_h = _seg_clear(lyr, bx, tap_y, tap_x, tap_y, 0.4, [(tap_x, tap_y)])
        if ok_v and ok_h:
            drop(bx, hy, lyr, cols=2, rows=2)
            path(lyr, [(bx, hy), (bx, tap_y), (tap_x, tap_y)], w=0.4)
            drop(tap_x, tap_y, tap_layer, cols=2, rows=2, frm=_STK[lyr])
            print(f"  {tag}: upper pin -> node on {lyr} at y {tap_y}")
            break
    else:
        print(f"  {tag}: NO CLEAR LAYER for the node route - not drawn")
    # lower pin to the ground rail on TopMetal1
    ly_ = snap(lo.center().y)
    drop(bx, ly_, "TM1", cols=2, rows=2)
    path("TM1", [(bx, ly_), (bx, -300.0)], w=1.64)
    print(f"  {tag}: lower pin -> ground rail on TM1")

RBL = {}
for _nm, _x, _y in (("RBL0A", -150.0, -225.0), ("RBL0B", 150.0, -225.0),
                    ("RBL1A", -150.0, -310.0), ("RBL1B", 150.0, -310.0)):
    RBL[_nm] = find("rhigh", x=_x, y=_y)

# Switch-node taps: A side on the bottom plate (Metal5) just inside its lower
# edge; B side on the TopMetal1 extension's Metal5 drop at tx = +31.
_bleed("RBL0A", RBL["RBL0A"], -25.0, -109.6, "M5")
_bleed("RBL0B", RBL["RBL0B"],  31.0, -108.0, "M5")
_bleed("RBL1A", RBL["RBL1A"], -25.0, -131.6, "M5")
_bleed("RBL1B", RBL["RBL1B"],  31.0, -130.0, "M5")


print("\n=== bleeds, bit 1 ===")
# The single-layer route was refused for bit 1: its upper pins are at
# y -272.86 and a vertical to the node at -130 crosses the gate buses and the
# buffer mirror region. MEASURED: TopMetal2 is clear below y -163 on both
# sides (the Vcc rail is at -160). So rise on TopMetal2 to y -170, drop to a
# lower layer there, and finish as before.
#
# The drop at the transition crosses every layer between, so its footprint is
# checked on each of them, not just the path segments.
_ORDER = ["M2", "M3", "M4", "M5", "TM1", "TM2"]

def _via_clear(x, y, lo, hi):
    a, b = _ORDER.index(lo), _ORDER.index(hi)
    for L in _ORDER[a:b + 1]:
        reg = _occupied(L)
        box = pya.DBox(x - 0.6, y - 0.6, x + 0.6, y + 0.6)
        if not (reg & pya.Region(box.to_itype(layout.dbu))).is_empty():
            return L
    return None

def _bleed_hi(tag, rinst, tap_x, tap_y, tap_layer, ymid=-170.0):
    if not rinst:
        return
    hi = sorted(pins(rinst, 8, 2), key=lambda q: q.center().y)[-1]
    hy = snap(hi.center().y)
    _in = -1.0 if hi.center().x > 0 else 1.0
    for dx in (4.0 * _in, 6.0 * _in):
        bx = snap(hi.center().x + dx)
        if not _seg_clear("TM2", bx, hy, bx, ymid, 2.0, [(bx, hy)]):
            continue
        for lyr in ("M4", "M3", "M2"):
            blk = _via_clear(bx, ymid, lyr, "TM2")
            if blk:
                continue
            if not _seg_clear(lyr, bx, ymid, bx, tap_y, 0.4, [(bx, ymid)]):
                continue
            if not _seg_clear(lyr, bx, tap_y, tap_x, tap_y, 0.4, [(tap_x, tap_y)]):
                continue
            # pin up to TopMetal2 (offset horizontally on M2 if dx != 0)
            drop(hi.center().x, hy, "M2", cols=2, rows=2)
            if dx:
                path("M2", [(hi.center().x, hy), (bx, hy)], w=0.4)
            drop(bx, hy, "TM2", cols=2, rows=2, frm="Metal2")
            path("TM2", [(bx, hy), (bx, ymid)], w=2.0)
            drop(bx, ymid, "TM2", cols=2, rows=2, frm=_STK[lyr])
            path(lyr, [(bx, ymid), (bx, tap_y), (tap_x, tap_y)], w=0.4)
            drop(tap_x, tap_y, tap_layer, cols=2, rows=2, frm=_STK[lyr])
            print(f"  {tag}: TM2 to y {ymid}, then {lyr} to node at y {tap_y} (x offset {dx})")
            return
    print(f"  {tag}: NO CLEAR ROUTE - not drawn")

_bleed_hi("RBL1A", RBL["RBL1A"], -25.0, -131.6, "M5")
_bleed_hi("RBL1B", RBL["RBL1B"],  31.0, -130.0, "M5")

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
