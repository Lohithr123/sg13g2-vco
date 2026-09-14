import pya

ly = pya.Layout()
ly.read("vco_20g_routed.gds")
top = ly.top_cell()
li = ly.layer(27, 25)

n = 0
it = top.begin_shapes_rec(li)
while not it.at_end():
    sh = it.shape()
    if sh.is_text():
        t = it.trans() * sh.text
        print(f"  routed: '{t.string}' at {t.x*ly.dbu:.2f},{t.y*ly.dbu:.2f}")
        n += 1
    it.next()
print(f"{n} label(s) in the routed layout, searched recursively")

src = pya.Layout()
src.read("/foss/designs/inductor_synth/inductor3_snapped.gds")
c = src.top_cell()
m = sum(1 for sh in c.shapes(src.layer(27, 25)).each() if sh.is_text())
print(f"{m} label(s) in the source inductor GDS")
