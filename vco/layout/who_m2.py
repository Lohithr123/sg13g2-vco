import pya

ly = pya.Layout(); ly.read("vco_20g_routed.gds")
top = ly.top_cell()
m2 = ly.layer(10, 0)

# Every Metal2 shape overlapping XSW0, UNMERGED and with its source: whether it
# is drawn in the top cell (my routing) or inside an instance (a PCell).
W = pya.DBox(-11.0, -112.0, -5.0, -104.0)
wr = pya.Region(W.to_itype(ly.dbu))

print("drawn directly in the top cell:")
for sh in top.shapes(m2).each():
    b = sh.dbbox()
    if not b.overlaps(W):
        continue
    print(f"   x {b.left:8.3f}..{b.right:8.3f}  y {b.bottom:9.3f}..{b.top:9.3f}"
          f"   {b.width():.3f} x {b.height():.3f}")

print("\nfrom instances:")
for inst in top.each_inst():
    ib = inst.dbbox()
    if not ib.overlaps(W):
        continue
    cell = ly.cell(inst.cell_index)
    for sh in cell.shapes(m2).each():
        b = sh.dbbox().transformed(inst.dcplx_trans)
        if not b.overlaps(W):
            continue
        print(f"   {cell.name:16} x {b.left:8.3f}..{b.right:8.3f}  "
              f"y {b.bottom:9.3f}..{b.top:9.3f}")
