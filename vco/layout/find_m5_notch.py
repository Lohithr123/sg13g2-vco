# Where is the 0.12 um Metal5 notch, and what produced it?
#
# The top cell has no under-width Metal5 shapes, so the violation is inside a
# subcell — but which one, and is it a via_stack or something else? Flatten the
# hierarchy and look at every Metal5 shape near the reported coordinates,
# together with which cell each came from.

import pya

ly = pya.Layout()
ly.read("vco_20g_routed.gds")
top = ly.top_cell()
m5 = ly.layer(67, 0)

print("=== instances near x -143.8, y -200 ===")
W = pya.DBox(-146.0, -203.0, -140.0, -197.0)
for inst in top.each_inst():
    b = inst.dbbox()
    if not b.overlaps(W):
        continue
    print(f"  {ly.cell(inst.cell_index).name:24} {b.to_s()}")

print("\n=== flattened Metal5 in that window ===")
flat = ly.create_cell("_f")
flat.copy_tree(top)
r = pya.Region(flat.begin_shapes_rec(m5)) & pya.Region(W.to_itype(ly.dbu))
for p in r.each():
    b = p.bbox().to_dtype(ly.dbu)
    print(f"  x {b.left:9.3f}..{b.right:9.3f}  y {b.bottom:9.3f}..{b.top:9.3f}"
          f"   {b.width():.3f} x {b.height():.3f}")

print("\n=== merged ===")
for p in r.merged().each():
    b = p.bbox().to_dtype(ly.dbu)
    print(f"  x {b.left:9.3f}..{b.right:9.3f}  y {b.bottom:9.3f}..{b.top:9.3f}"
          f"   {b.width():.3f} x {b.height():.3f}  {p.num_points()} pts")
