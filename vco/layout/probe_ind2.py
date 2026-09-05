import pya
ly=pya.Layout(); ly.read("/foss/designs/inductor_synth/inductor3_snapped.gds")
c=ly.top_cell()
for lay,dt,nm in [(126,0,"TopMetal1"),(134,0,"TopMetal2"),(126,25,"TM1.text"),
                  (134,25,"TM2.text"),(8,25,"M1.text"),(63,0,"ind_drw"),(63,25,"ind.text"),
                  (63,2,"ind_pin")]:
    li=ly.layer(lay,dt)
    shs=list(c.shapes(li).each())
    if not shs: continue
    print(f"\n{nm} ({lay}/{dt}): {len(shs)} shapes")
    for sh in shs:
        if sh.is_text():
            print(f"   TEXT '{sh.text.string}' at {sh.text.x*ly.dbu:.2f},{sh.text.y*ly.dbu:.2f}")
        else:
            b=sh.dbbox()
            if b.width()<40 and b.height()<40:
                print(f"   box x {b.left:8.2f}..{b.right:8.2f}  y {b.bottom:8.2f}..{b.top:8.2f}")
