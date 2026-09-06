import pya
ly=pya.Layout(); ly.read("vco_20g_routed.gds")
top=ly.top_cell()
print("TopMetal1 shapes below y=-100 (bank region):")
for sh in top.shapes(ly.layer(126,0)).each():
    b=sh.dbbox()
    if b.top > -100: continue
    print(f"  x {b.left:8.2f}..{b.right:8.2f}  y {b.bottom:9.2f}..{b.top:9.2f}")
print("\nMetal3 shapes below y=-100:")
for sh in top.shapes(ly.layer(30,0)).each():
    b=sh.dbbox()
    if b.top > -100: continue
    print(f"  x {b.left:8.2f}..{b.right:8.2f}  y {b.bottom:9.2f}..{b.top:9.2f}")
print("\nMetal4 shapes below y=-100:")
for sh in top.shapes(ly.layer(50,0)).each():
    b=sh.dbbox()
    if b.top > -100: continue
    print(f"  x {b.left:8.2f}..{b.right:8.2f}  y {b.bottom:9.2f}..{b.top:9.2f}")
