import pya
ly=pya.Layout(); ly.read("vco_20g_routed.gds")
top=ly.top_cell()
# XMT2 at x -20, y -190. Where is my gate contact, and where is the drain?
W=pya.DBox(-29,-187,-11,-184)
r=pya.Region(top.shapes(ly.layer(10,0))) & pya.Region(W.to_itype(ly.dbu))
print("Metal2 above XMT2:")
for p in sorted(r.each(), key=lambda q:q.bbox().left)[:10]:
    b=p.bbox().to_dtype(ly.dbu)
    print(f"   x {b.left:8.3f}..{b.right:8.3f}  y {b.bottom:9.3f}..{b.top:9.3f}")
for inst in top.each_inst():
    bb=inst.dbbox()
    if abs(bb.center().x+20)<3 and abs(bb.center().y+190)<3:
        print(f"\ninstance top y {bb.top:.3f}")
        for sh in ly.cell(inst.cell_index).shapes(ly.layer(8,2)).each():
            sb=sh.dbbox().transformed(inst.dcplx_trans)
            print(f"   pin x {sb.left:8.3f}..{sb.right:8.3f} y {sb.bottom:9.3f}..{sb.top:9.3f}")
        break
