import pathlib
p = pathlib.Path('route_v2.py'); s = p.read_text()

new = '''
print("\\n=== varactor gate bias ===")
# RB1 and RB2 hold G1 and G2 at mid-supply so the varactor sits on the steep
# part of its C-V curve. Without this the gates float at whatever the coupling
# caps leave them at, and the device gives 2.3% tuning instead of 5.4% — that
# was measured, not assumed.
#
# These carry no signal current, only DC, so the routing is unconstrained:
# Metal2 is empty out here and nothing else needs the space.

if RB1 and RB2 and XCV:
    r1 = pins(RB1, 8, 2)
    r2 = pins(RB2, 8, 2)
    # rhigh's two pins are at the ends of the strip, sorted by x in cell frame;
    # for a vertical resistor they differ in y, so take them by y instead.
    r1 = sorted(r1, key=lambda b: b.center().y)
    r2 = sorted(r2, key=lambda b: b.center().y)
    r1_bot, r1_top = r1[0], r1[-1]
    r2_bot, r2_top = r2[0], r2[-1]
    print(f"  RB1 pins y {r1_bot.center().y:.2f} and {r1_top.center().y:.2f}")
    print(f"  RB2 pins y {r2_bot.center().y:.2f} and {r2_top.center().y:.2f}")

    # Bottom of each resistor to its gate, on Metal2.
    drop(r1_bot.center().x, r1_bot.center().y, "M2")
    path("M2", [(r1_bot.center().x, r1_bot.center().y),
                (r1_bot.center().x, g1.y - 6.0),
                (g1.x - 8.0, g1.y - 6.0),
                (g1.x - 8.0, g1.y)])
    drop(g1.x - 8.0, g1.y, "M2")
    wire("M1", g1.x - 8.0, g1.y, g1.x - 4.0, g1.y, 0.27)

    drop(r2_bot.center().x, r2_bot.center().y, "M2")
    path("M2", [(r2_bot.center().x, r2_bot.center().y),
                (r2_bot.center().x, g2.y + 6.0),
                (g2.x + 8.0, g2.y + 6.0),
                (g2.x + 8.0, g2.y)])
    drop(g2.x + 8.0, g2.y, "M2")
    wire("M1", g2.x + 4.0, g2.y, g2.x + 8.0, g2.y, 0.27)

    # The far ends join as the vg rail, brought out on Metal2 above the
    # resistors where nothing else runs.
    drop(r1_top.center().x, r1_top.center().y, "M2")
    drop(r2_top.center().x, r2_top.center().y, "M2")
    path("M2", [(r1_top.center().x, r1_top.center().y),
                (r1_top.center().x, -150.0),
                (r2_top.center().x, -150.0),
                (r2_top.center().x, r2_top.center().y)])
    print(f"  vg rail at y -150")

print("\\n=== varactor well to tune ===")
# The well is the tuning input. It goes to a pad eventually; for now bring it
# out to the left edge on Metal2.
if XCV:
    drop(w_.x, w_.y, "M2")
    path("M2", [(w_.x, w_.y), (-20.0, w_.y), (-20.0, -155.0)])
    print(f"  W ({w_.x:.2f},{w_.y:.2f}) out to x -20")

'''

s = s.replace('layout.write(OUT)', new + 'layout.write(OUT)')

s = s.replace('''    "XCV_G2": (4.08, -169.75, "M5"),
})''',
'''    "XCV_G2": (4.08, -169.75, "M5"),
    "RB1_bot": (-45.0, -164.0, "M2"), "RB2_bot": (45.0, -164.0, "M2"),
})''')

s = s.replace('''        {"XCV_G1"}, {"XCV_G2"},''',
'''        {"XCV_G1", "RB1_bot"}, {"XCV_G2", "RB2_bot"},''')

p.write_text(s)
print("gate bias and tune routing added")
