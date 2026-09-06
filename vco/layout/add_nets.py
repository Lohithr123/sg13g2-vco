import pathlib
p = pathlib.Path('route_all.py'); s = p.read_text()

new = '''
print("\\n=== net: cross-coupling (each base to the opposite collector) ===")
# This is what makes it an oscillator. XQ1's base is driven by XQ2's collector
# and vice versa, so the two paths must cross.
#
# They cannot cross on the same layer. The left-to-right path goes on Metal2
# and the right-to-left on Metal1, with via stacks where each leaves and
# rejoins its device. Both paths are the same length by construction — a
# differential pair with mismatched feedback delays is not symmetric no matter
# how carefully the devices are placed.
b1 = label_pos(XQ1, "B")
b2 = label_pos(XQ2, "B")
c1 = label_pos(XQ1, "C")
c2 = label_pos(XQ2, "C")
print(f"  bases  ({b1.x:.2f},{b1.y:.2f}) ({b2.x:.2f},{b2.y:.2f})")
print(f"  colls  ({c1.x:.2f},{c1.y:.2f}) ({c2.x:.2f},{c2.y:.2f})")

# Route below the devices, clear of the tank metal above.
YX = -106.0

# XQ2 collector -> XQ1 base, on Metal2.
via(c2.x, c2.y, b="Metal1", t="Metal2")
wire("M2", c2.x, c2.y, c2.x, YX, 1.0)
wire("M2", c2.x, YX, b1.x, YX, 1.0)
wire("M2", b1.x, YX, b1.x, b1.y, 1.0)
via(b1.x, b1.y, b="Metal1", t="Metal2")

# XQ1 collector -> XQ2 base, on Metal1, one micron lower so the two do not
# touch where they cross.
YX2 = YX - 2.0
wire("M1", c1.x, c1.y, c1.x - 3.0, c1.y, 1.0)
wire("M1", c1.x - 3.0, c1.y, c1.x - 3.0, YX2, 1.0)
wire("M1", c1.x - 3.0, YX2, b2.x + 3.0, YX2, 1.0)
wire("M1", b2.x + 3.0, YX2, b2.x + 3.0, b2.y, 1.0)
wire("M1", b2.x + 3.0, b2.y, b2.x, b2.y, 1.0)

check("xcouple M2", "M2", -12.0, -107.0, 12.0, -98.0)
check("xcouple M1", "M1", -13.0, -109.0, 13.0, -98.5, expect=3)

print("\\n=== net: tail cascode (XMT2 source to XMT1 drain) ===")
# Cascode pair: the upper device's source feeds the lower device's drain.
s2 = pin_boxes(XMT2, 8, 2)[0]
d1 = pin_boxes(XMT1, 8, 2)[1]
ym = -196.0
wire("M1", s2.center().x, s2.center().y, s2.center().x, ym, 1.0)
wire("M1", s2.center().x, ym, d1.center().x, ym, 1.0)
wire("M1", d1.center().x, ym, d1.center().x, d1.center().y, 1.0)
print(f"  XMT2 source ({s2.center().x:.2f},{s2.center().y:.2f}) -> "
      f"XMT1 drain ({d1.center().x:.2f},{d1.center().y:.2f})")
check("cascode", "M1", -30.0, -197.0, 30.0, -185.0, expect=4)

print("\\n=== net: mirror gates ===")
# XMR2 gate drives both cascode gates; XMR1 gate drives both lower gates.
g_r2 = pin_boxes(XMR2, 5, 2)[0]
g_r1 = pin_boxes(XMR1, 5, 2)[0]
g_t2 = pin_boxes(XMT2, 5, 2)[0]
g_t1 = pin_boxes(XMT1, 5, 2)[0]
# Poly is resistive; get onto Metal1 immediately and route there.
for g in (g_r2, g_r1, g_t2, g_t1):
    via(g.center().x, g.center().y, b="Metal1", t="Metal2")
yg = -182.0
wire("M2", g_r2.center().x, g_r2.center().y, g_r2.center().x, yg, 1.0)
wire("M2", g_r2.center().x, yg, g_t2.center().x, yg, 1.0)
wire("M2", g_t2.center().x, yg, g_t2.center().x, g_t2.center().y, 1.0)
yg2 = -179.0
wire("M2", g_r1.center().x, g_r1.center().y, g_r1.center().x, yg2, 1.0)
wire("M2", g_r1.center().x, yg2, g_t1.center().x, yg2, 1.0)
wire("M2", g_t1.center().x, yg2, g_t1.center().x, g_t1.center().y, 1.0)
print(f"  cascode gate bus at y {yg}, mirror gate bus at y {yg2}")
check("gate bus", "M2", -60.0, -196.0, 30.0, -178.0, expect=3)

'''

s = s.replace('layout.write(OUT)', new + 'layout.write(OUT)')
p.write_text(s)
print("added cross-coupling, cascode and gate nets")
