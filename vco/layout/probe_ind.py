import pya
ly=pya.Layout(); ly.read("/foss/designs/inductor_synth/inductor3_snapped.gds")
c=ly.top_cell()
print("cell:", c.name, " bbox:", c.dbbox().to_s())
NAMES={(8,0):"Metal1",(10,0):"Metal2",(67,0):"Metal5",(126,0):"TopMetal1",
       (134,0):"TopMetal2",(125,0):"TopVia1",(133,0):"TopVia2",
       (8,25):"Metal1.text",(126,25):"TopMetal1.text",(134,25):"TopMetal2.text"}
for (lay,dt),nm in sorted(NAMES.items()):
    li=ly.layer(lay,dt)
    n=0
    for sh in c.shapes(li).each():
        if sh.is_text():
            print(f"  {nm:14} TEXT '{sh.text.string}' at "
                  f"{sh.text.x*ly.dbu:.2f},{sh.text.y*ly.dbu:.2f}")
        else:
            b=sh.dbbox()
            if b.width()<30 and b.height()<30:   # ports, not the spiral itself
                print(f"  {nm:14} box x {b.left:8.2f}..{b.right:8.2f}  "
                      f"y {b.bottom:8.2f}..{b.top:8.2f}")
        n+=1
        if n>40: break
