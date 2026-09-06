import pathlib
p = pathlib.Path('route_v2.py'); s = p.read_text()

new = '''
print("\\n=== buffer bias mirrors ===")
# Each buffer emitter is pulled by its own cascode pair: XMB2 on top, XMB1
# below. Same arrangement as the tail mirror, which routed cleanly, so the
# same approach applies.
#
# These are DC nodes and the devices sit at x +/-95 and +/-130 with clear space
# around them, so the routing is unconstrained — the only rule that matters is
# not crossing the tank layers, which live on Metal3 and Metal4.

MB2A = find("nmos", x=-130.0, y=-200.0, wmin=20)
MB1A = find("nmos", x=-95.0, y=-200.0, wmin=20)
MB2B = find("nmos", x=95.0, y=-200.0, wmin=20)
MB1B = find("nmos", x=130.0, y=-200.0, wmin=20)
for nm, o in [("XMB2A", MB2A), ("XMB1A", MB1A),
              ("XMB2B", MB2B), ("XMB1B", MB1B)]:
    print(f"  {nm:6} {'ok' if o else 'NOT FOUND'}")

if all([MB2A, MB1A, MB2B, MB1B]) and XB1 and XB2:
    for tag, mb2, mb1, be, sgn in (("A", MB2A, MB1A, be1, -1.0),
                                   ("B", MB2B, MB1B, be2, 1.0)):
        d2 = pins(mb2, 8, 2)[1]        # cascode drain -> buffer emitter
        s2 = pins(mb2, 8, 2)[0]        # cascode source -> lower drain
        d1 = pins(mb1, 8, 2)[1]

        # Emitter down to the cascode drain, on Metal5.
        xlane = sgn * 145.0
        path("M5", [(xlane, be.y), (xlane, d2.center().y),
                    (d2.center().x, d2.center().y)], w=2.0)
        drop(d2.center().x, d2.center().y, "M5", cols=1, rows=8)

        # Cascode source to the lower device's drain, below both.
        ylink = -207.0
        path("M5", [(s2.center().x, s2.center().y), (s2.center().x, ylink),
                    (d1.center().x, ylink), (d1.center().x, d1.center().y)])
        drop(s2.center().x, s2.center().y, "M5", cols=1, rows=8)
        drop(d1.center().x, d1.center().y, "M5", cols=1, rows=8)
        print(f"  side {tag}: emitter -> XMB2 drain at "
              f"({d2.center().x:.1f},{d2.center().y:.1f})")

'''

s = s.replace('layout.write(OUT)', new + 'layout.write(OUT)')

s = s.replace('''    "XB1_E": (-116.2, -95.23, "M2"), "XB2_E": (116.2, -95.23, "M2"),
})''',
'''    "XB1_E": (-116.2, -95.23, "M2"), "XB2_E": (116.2, -95.23, "M2"),
    "MB2A_D": (-127.0, -200.0, "M5"), "MB2B_D": (127.0, -200.0, "M5"),
})''')

s = s.replace('''{"XB1_E"}, {"XB2_E"}]''',
              '''{"XB1_E", "MB2A_D"}, {"XB2_E", "MB2B_D"}]''')

p.write_text(s)
print("buffer bias added")
