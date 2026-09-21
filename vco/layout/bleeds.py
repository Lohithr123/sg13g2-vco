import pya
ly = pya.Layout(); ly.read("vco_20g_routed.gds")
top = ly.top_cell()
print("bleed resistors:")
for inst in top.each_inst():
    c = ly.cell(inst.cell_index)
    if not c.name.startswith("rhigh"):
        continue
    b = inst.dbbox()
    if b.height() < 50:
        continue
    pins = sorted((sh.dbbox().transformed(inst.dcplx_trans)
                   for sh in c.shapes(ly.layer(8, 2)).each()),
                  key=lambda q: q.center().y)
    print(f"  at ({b.center().x:+7.1f},{b.center().y:7.1f})  "
          f"lower pin y {pins[0].center().y:7.2f}  upper pin y {pins[-1].center().y:7.2f}")

print("\nground on TopMetal1 near the edges:")
r = pya.Region(top.shapes(ly.layer(126, 0)))
for p in r.merged().each():
    bb = p.bbox().to_dtype(ly.dbu)
    if abs(bb.left) > 140 or abs(bb.right) > 140:
        print(f"   x {bb.left:8.2f}..{bb.right:8.2f}  y {bb.bottom:8.2f}..{bb.top:8.2f}")
