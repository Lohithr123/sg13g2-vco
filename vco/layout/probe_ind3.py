import pya
ly=pya.Layout(); ly.read("/foss/designs/inductor_synth/inductor3_snapped.gds")
c=ly.top_cell()
print("all layers with shapes:")
for li in ly.layer_indexes():
    i=ly.get_info(li)
    n=len(list(c.shapes(li).each()))
    if n: print(f"  {i.layer:4d}/{i.datatype:<3d}  {n:4d} shapes")
print("\nall text anywhere:")
for li in ly.layer_indexes():
    i=ly.get_info(li)
    for sh in c.shapes(li).each():
        if sh.is_text():
            t=sh.text.string.replace("\n"," ")[:40]
            print(f"  {i.layer}/{i.datatype}  '{t}' at "
                  f"{sh.text.x*ly.dbu:.2f},{sh.text.y*ly.dbu:.2f}")
