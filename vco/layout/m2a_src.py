# 282 M2.a violations survived widening the stubs to 0.26 um, so the
# under-width shapes are not the stubs. Find them directly: every Metal2
# polygon in the layout narrower than 0.21 um, with where it came from.

import pya
from collections import Counter

ly = pya.Layout()
ly.read("/foss/designs/vco/layout/vco_20g_routed.gds")
top = ly.top_cell()
m2 = ly.layer(10, 0)

print("=== under-width Metal2 drawn in the TOP CELL (mine) ===")
mine = Counter()
examples = {}
for sh in top.shapes(m2).each():
    b = sh.dbbox()
    w = min(b.width(), b.height())
    if w < 0.209:
        key = (round(b.width(), 3), round(b.height(), 3))
        mine[key] += 1
        examples.setdefault(key, b)
for k, n in mine.most_common(8):
    b = examples[k]
    print(f"  {n:4d} x  {k[0]:.3f} x {k[1]:.3f}   e.g. x {b.left:.3f}..{b.right:.3f}"
          f"  y {b.bottom:.3f}..{b.top:.3f}")
if not mine:
    print("  none")

print("\n=== under-width Metal2 inside INSTANCES (PCells) ===")
inst_c = Counter()
for inst in top.each_inst():
    cell = ly.cell(inst.cell_index)
    for sh in cell.shapes(m2).each():
        b = sh.dbbox()
        if min(b.width(), b.height()) < 0.209:
            inst_c[(cell.name, round(b.width(), 3), round(b.height(), 3))] += 1
for k, n in inst_c.most_common(8):
    print(f"  {n:4d} x  [{k[0]}]  {k[1]:.3f} x {k[2]:.3f}")
if not inst_c:
    print("  none")
