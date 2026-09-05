# Tank routing — inductor ports to the cross-coupled pair
#
# Appended to the placement build. Run after build_layout.py has produced
# vco_20g.gds, or import the same library handles and extend it.
#
# WHAT CONNECTS TO WHAT
#
#   LA  TopMetal1  x -12.00..-6.00  y -85.30..-82.30   -> XQ1 collector
#   LB  TopMetal1  x   6.00..12.00  y -85.30..-82.30   -> XQ2 collector
#   LC  TopMetal2  x  -3.00.. 3.00  y -85.30..-82.30   -> Vcc (later)
#
# The npn13G2 collector is the Metal1 shape at y +1.01..+1.25 within its own
# cell, x -0.93..+0.93. With XQ1 placed bbox-centred at (-9, -100) and the
# cell bbox running y -3.33..+3.78, the cell origin sits at
#   y_origin = -100 - ((-3.33 + 3.78)/2) = -100.225
# so the collector metal lands at y -99.2..-98.98, x -9.93..-8.07.
#
# THE PROBLEM: six layers between them
#
# Ports are TopMetal1, collectors are Metal1. A via_stack PCell spans
# b_layer..t_layer, so one instance per side does the whole descent. Placing
# it under the port and running Metal1 across to the collector keeps the
# tank loop to about 15 um per side — every micron here is series resistance
# and inductance that was never in the 0.901 nH / Q 9.68 extraction.

import os, sys
import pya

PDK = os.environ.get("PDK_ROOT", "/foss/pdks") + "/ihp-sg13g2"
sys.path.insert(0, PDK + "/libs.tech/klayout/python")
import sg13g2_pycell_lib  # noqa: F401

LIB, TECH = "SG13_dev", "sg13g2"
GDS = "/foss/designs/vco/layout/vco_20g.gds"
OUT = "/foss/designs/vco/layout/vco_20g_routed.gds"

lib = pya.Library.library_by_name(LIB, TECH)
liblay = lib.layout()

layout = pya.Layout()
layout.dbu = 0.001
layout.read(GDS)
top = layout.top_cell()

M1  = layout.layer(8, 0)
TM1 = layout.layer(126, 0)

def box(layer, x1, y1, x2, y2):
    top.shapes(layer).insert(
        pya.DBox(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)))

def via(x, y, b="Metal1", t="TopMetal1", cols=2, rows=2):
    """Via stack centred on (x, y), spanning b_layer to t_layer."""
    pid = liblay.pcell_id("via_stack")
    ci = layout.add_pcell_variant(lib, pid, {
        "b_layer": b, "t_layer": t,
        "vn_columns": cols, "vn_rows": rows,
    })
    bb = layout.cell(ci).dbbox()
    top.insert(pya.DCellInstArray(
        ci, pya.DTrans(x - bb.center().x, y - bb.center().y)))
    return bb

print("=== tank routing ===")

# Port and collector geometry, from the probes.
PORT_Y_BOT, PORT_Y_TOP = -85.30, -82.30
COLL_Y_BOT, COLL_Y_TOP = -99.20, -98.98

for side, xc in (("LA -> XQ1", -9.0), ("LB -> XQ2", 9.0)):
    # Via stack just below the port, clear of the inductor's -85.3 edge.
    vy = -88.0
    bb = via(xc, vy)
    print(f"  {side}: via stack {bb.width():.2f} x {bb.height():.2f} "
          f"at ({xc}, {vy})")

    # TopMetal1 from the port down to the via stack. 6 um wide, matching the
    # port, so no width discontinuity.
    box(TM1, xc - 3.0, PORT_Y_BOT, xc + 3.0, vy + bb.height() / 2)

    # Metal1 from the via stack down to the collector. The collector metal is
    # 1.86 um wide; keep the run at least that.
    # Run Metal1 THROUGH the via stack rather than up to its bounding box.
    # The stack's bbox includes TopMetal1, which is wider than its Metal1 pad,
    # so ending at the bbox edge left a 0.5 um gap that DRC does not flag —
    # it is an open circuit, not a rule violation.
    box(M1, xc - 0.93, vy + bb.height() / 2, xc + 0.93, COLL_Y_TOP)
    print(f"           TM1 {PORT_Y_BOT:.1f} -> {vy:.1f}, "
          f"M1 {vy:.1f} -> {COLL_Y_TOP:.1f}")

layout.write(OUT)
print(f"\nwrote {OUT}")
print("tank loop is about 15 um per side — check DRC before adding more")
