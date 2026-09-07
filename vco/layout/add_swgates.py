import pathlib
p = pathlib.Path('route_v2.py'); s = p.read_text()

new = '''
print("\\n=== bank switch gates ===")
# Two control inputs, one per bank bit. These select the band, so they are
# static logic levels — no signal, no timing constraint, and the only thing
# that matters is not disturbing the tank.
#
# The switches sit at x -8 with their gate between source and drain, 0.35 um
# either side. Same geometry as the mirror gates, so the same approach: a via
# straight up on the gate, then a stub on a layer nothing else uses here.
# Metal2 carries the mirror gate buses but only below y -200; up here at
# y -108 and -130 it is free.

for i, yb in enumerate(BANKY):
    sw = find("nmos", x=-8.0, y=yb, wmin=None)
    if not sw:
        print(f"  bit {i}: switch not found")
        continue
    gp = pins(sw, 5, 2)
    if not gp:
        print(f"  bit {i}: no gate pin")
        continue
    g = gp[0]
    # Out to the left edge, clear of the bank capacitors at x -25 and the
    # tail's Metal5 lane at x 0.
    drop(g.center().x, g.center().y, "M2", cols=1, rows=2)
    path("M2", [(g.center().x, g.center().y),
                (g.center().x, yb - 9.0),
                (-60.0, yb - 9.0)], w=0.4)
    print(f"  bit {i}: gate at ({g.center().x:.2f},{g.center().y:.2f}) "
          f"out to x -60")

'''

s = s.replace('layout.write(OUT)', new + 'layout.write(OUT)')

s = s.replace('''    "casc_bus": (-30.0, -212.0, "M2"), "lower_bus": (-30.0, -218.0, "M2"),
})''',
'''    "casc_bus": (-30.0, -212.0, "M2"), "lower_bus": (-30.0, -218.0, "M2"),
    "nb0": (-60.0, -117.0, "M2"), "nb1": (-60.0, -139.0, "M2"),
})''')

s = s.replace('''{"XB1_E", "MB2A_D"}, {"XB2_E", "MB2B_D"}]''',
              '''{"XB1_E", "MB2A_D"}, {"XB2_E", "MB2B_D"},
        {"nb0"}, {"nb1"}]''')

p.write_text(s)
print("switch gate routing added")
