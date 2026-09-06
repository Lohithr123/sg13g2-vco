import pya
ly=pya.Layout(); ly.read("vco_20g.gds")
top=ly.top_cell()
for inst in top.each_inst():
    if ly.cell(inst.cell_index).name!="npn13G2": continue
    if abs(inst.dbbox().center().x+9)>2: continue
    print("XQ1 internal geometry:")
    for lay,dt,nm in [(8,0,"M1"),(6,0,"Cont"),(19,0,"Via1"),(10,0,"M2")]:
        for sh in ly.cell(inst.cell_index).shapes(ly.layer(lay,dt)).each():
            b=sh.dbbox().transformed(inst.dcplx_trans)
            print(f"  {nm:5} x {b.left:7.3f}..{b.right:7.3f}  y {b.bottom:9.3f}..{b.top:9.3f}")
    break
