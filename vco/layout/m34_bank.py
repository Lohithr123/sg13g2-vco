import pya
ly=pya.Layout(); ly.read("vco_20g_routed.gds")
top=ly.top_cell()
for lay,nm in [(30,"Metal3"),(50,"Metal4")]:
    print(f"\n{nm} shapes in the bank region (y -100 to -140):")
    for sh in top.shapes(ly.layer(lay,0)).each():
        b=sh.dbbox()
        if b.top > -100 or b.bottom < -140: continue
        print(f"  x {b.left:8.2f}..{b.right:8.2f}  y {b.bottom:9.2f}..{b.top:9.2f}")
