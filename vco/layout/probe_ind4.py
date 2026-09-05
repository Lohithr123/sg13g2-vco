import pya
ly=pya.Layout(); ly.read("/foss/designs/inductor_synth/inductor3_snapped.gds")
c=ly.top_cell()
for lay,dt,nm in [(126,2,"TopMetal1.pin"),(134,2,"TopMetal2.pin"),
                  (126,0,"TopMetal1"),(134,0,"TopMetal2")]:
    li=ly.layer(lay,dt)
    print(f"\n{nm}:")
    for sh in c.shapes(li).each():
        b=sh.dbbox()
        print(f"   x {b.left:8.2f}..{b.right:8.2f}   y {b.bottom:8.2f}..{b.top:8.2f}")
