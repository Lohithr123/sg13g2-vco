# XSW0 (M$99) is the last shorted device. Its three Metal1 strips all extract
# onto one net. Find the bridge by removing shapes one at a time from the
# connectivity and seeing which removal separates the strips — rather than
# reasoning about which shape looks wrong.
#
# Simpler and decisive: list every shape that touches BOTH the source strip at
# x -8.51 and the drain strip at x -8.00, on any layer.

import pya

ly = pya.Layout()
ly.read("/foss/designs/vco/layout/vco_20g_routed.gds")
top = ly.top_cell()

# The two strips, as regions.
src = pya.Region(pya.DBox(-8.60, -110.0, -8.42, -106.0).to_itype(ly.dbu))
drn = pya.Region(pya.DBox(-8.09, -110.0, -7.91, -106.0).to_itype(ly.dbu))

LAYERS = [(5, 0, "poly"), (6, 0, "Cont"), (8, 0, "M1"), (19, 0, "Via1"),
          (10, 0, "M2"), (29, 0, "Via2"), (30, 0, "M3"), (49, 0, "Via3"),
          (50, 0, "M4"), (66, 0, "Via4"), (67, 0, "M5")]

print("shapes touching BOTH the source strip (x -8.51) and the drain (x -8.00):")
hits = 0
for lay, dt, nm in LAYERS:
    # Top-cell shapes
    for sh in top.shapes(ly.layer(lay, dt)).each():
        r = pya.Region(sh.polygon if sh.is_polygon() else sh.box)
        if not (r & src).is_empty() and not (r & drn).is_empty():
            b = sh.dbbox()
            print(f"  [top] {nm:5} x {b.left:8.3f}..{b.right:8.3f}  "
                  f"y {b.bottom:9.3f}..{b.top:9.3f}")
            hits += 1
    # Instance shapes
    for inst in top.each_inst():
        cell = ly.cell(inst.cell_index)
        for sh in cell.shapes(ly.layer(lay, dt)).each():
            b = sh.dbbox().transformed(inst.dcplx_trans)
            r = pya.Region(b.to_itype(ly.dbu))
            if not (r & src).is_empty() and not (r & drn).is_empty():
                print(f"  [{cell.name}] {nm:5} x {b.left:8.3f}..{b.right:8.3f}  "
                      f"y {b.bottom:9.3f}..{b.top:9.3f}")
                hits += 1

print(f"\n{hits} bridging shape(s)")
