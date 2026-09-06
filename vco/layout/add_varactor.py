import pathlib
p = pathlib.Path('route_v2.py'); s = p.read_text()

new = '''
print("\\n=== varactor and coupling caps ===")
# outp -> CC1 -> varactor G1, outn -> CC2 -> varactor G2, with the two bias
# resistors holding both gates at mid-supply and the well driven by Vtune.
#
# The varactor sits on the centre line and the coupling caps are symmetric at
# +/-45, so the two gate paths are the same length. On a differential tank an
# imbalance here shows up directly as amplitude mismatch, which is why the
# varactor was moved from x = +8 to x = 0 before routing.
#
# Layer discipline is the same as the bank, and for the same reason: a via
# stack spanning Metal3 to TopMetal1 passes through Metal4, so if both tank
# nets terminated on TopMetal1 plates every stack would bridge them. outp
# takes the top plate, outn the bottom.

XCV = find("SVaricap", x=0.0, y=-172.0)
CC1 = find("cmim", x=-45.0, y=-250.0)
CC2 = find("cmim", x=45.0, y=-250.0)
RB1 = find("rhigh", x=-45.0, y=-160.0)
RB2 = find("rhigh", x=45.0, y=-160.0)
for nm, o in [("XCV", XCV), ("CC1", CC1), ("CC2", CC2),
              ("RB1", RB1), ("RB2", RB2)]:
    print(f"  {nm:5} {'ok' if o else 'NOT FOUND'}")

if XCV and CC1 and CC2:
    g1 = label(XCV, "G1")
    g2 = label(XCV, "G2")
    w_ = label(XCV, "W")
    t1, b1c = cap_plates(CC1)
    t2, b2c = cap_plates(CC2)

    # outp (Metal3) down to CC1's top plate.
    path("M3", [(-16.0, -105.0), (-16.0, -230.0),
                (t1.center().x, -230.0), (t1.center().x, t1.center().y)])
    drop(t1.center().x, t1.center().y, "TM1", frm="Metal3")

    # outn (Metal4) down to CC2's bottom plate.
    path("M4", [(16.0, -109.0), (16.0, -234.0),
                (b2c.center().x, -234.0), (b2c.center().x, b2c.center().y)])
    drop(b2c.center().x, b2c.center().y, "M5", frm="Metal4")

    # CC1's bottom plate (Metal5) across to G1.
    path("M5", [(b1c.center().x, b1c.center().y),
                (b1c.center().x, -200.0),
                (g1.x - 4.0, -200.0),
                (g1.x - 4.0, g1.y)])
    drop(g1.x - 4.0, g1.y, "M5")
    wire("M1", g1.x - 4.0, g1.y, g1.x, g1.y, 0.27)

    # CC2's top plate: out on TopMetal1 at 1.64 um to meet TM1.a, then down to
    # Metal5 clear of the plate, and across to G2.
    tx2 = t2.center().x + 30.0
    wire("TM1", t2.center().x, t2.center().y, tx2, t2.center().y, 1.64)
    drop(tx2, t2.center().y, "TM1", frm="Metal5")
    path("M5", [(tx2, t2.center().y), (tx2, -196.0),
                (g2.x + 4.0, -196.0), (g2.x + 4.0, g2.y)])
    drop(g2.x + 4.0, g2.y, "M5")
    wire("M1", g2.x, g2.y, g2.x + 4.0, g2.y, 0.27)

    print(f"  G1 ({g1.x:.2f},{g1.y:.2f})  G2 ({g2.x:.2f},{g2.y:.2f})  "
          f"W ({w_.x:.2f},{w_.y:.2f})")

'''

s = s.replace('layout.write(OUT)', new + 'layout.write(OUT)')

s = s.replace('''    "CB1A_top": (-25.0, -130.0, "TM1"), "CB1B_top": (25.0, -130.0, "M5"),
})''',
'''    "CB1A_top": (-25.0, -130.0, "TM1"), "CB1B_top": (25.0, -130.0, "M5"),
    "CC1_top": (-45.0, -250.0, "TM1"), "CC2_bot": (45.0, -250.0, "M5"),
    "XCV_G1": (-4.0 + 8.08, -174.25, "M5"),
    "XCV_G2": (4.0 + 8.08, -169.75, "M5"),
})''')

s = s.replace('''want = [{"XQ1_C", "XQ2_B", "CB0A_top", "CB1A_top"},
        {"XQ2_C", "XQ1_B", "CB0B_top", "CB1B_top"},
        {"XQ1_E", "XQ2_E", "XMT2_D"}]''',
'''want = [{"XQ1_C", "XQ2_B", "CB0A_top", "CB1A_top", "CC1_top"},
        {"XQ2_C", "XQ1_B", "CB0B_top", "CB1B_top", "CC2_bot"},
        {"XQ1_E", "XQ2_E", "XMT2_D"}]''')

p.write_text(s)
print("varactor branch added")
