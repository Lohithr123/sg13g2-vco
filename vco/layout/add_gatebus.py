import pathlib
p = pathlib.Path('route_v2.py'); s = p.read_text()

new = '''
print("\\n=== mirror gate buses ===")
# One reference branch biases every mirror in the design: XMR2's gate drives
# all the cascode gates, XMR1's drives all the lower gates. Six devices on two
# buses.
#
# Poly is resistive, so each gate gets a via up to Metal5 immediately and the
# run happens there. These are DC nodes with no signal on them, but they still
# must not cross Metal3 or Metal4 — those carry the tank.
#
# The two buses run at different y so they never meet: cascodes at y -215,
# lower gates at y -220, both below the mirror row at -190 and above the
# buffer mirrors at -200... which they are not. Use -172 and -178 instead,
# in the gap between the varactor row and the mirror row.

XMR2 = find("nmos", x=-55.0, y=-190.0)
XMR1 = find("nmos", x=-42.0, y=-190.0)
for nm, o in [("XMR2", XMR2), ("XMR1", XMR1)]:
    print(f"  {nm:6} {'ok' if o else 'NOT FOUND'}")

if XMR2 and XMR1 and XMT2 and XMT1 and all([MB2A, MB1A, MB2B, MB1B]):
    def gate(inst):
        g = pins(inst, 5, 2)
        return g[0] if g else None

    casc = [XMR2, XMT2, XMT1, MB2A, MB2B]      # upper devices
    lower = [XMR1, XMT1, XMT2, MB1A, MB1B]     # lower devices

    # The tail cascode pair is XMT2 over XMT1, and the buffer pairs XMB2 over
    # XMB1, so the cascode bus takes XMT2/MB2A/MB2B and the lower bus takes
    # XMT1/MB1A/MB1B.
    casc = [XMR2, XMT2, MB2A, MB2B]
    lower = [XMR1, XMT1, MB1A, MB1B]

    for tag, group, ybus in (("cascode", casc, -172.0),
                             ("lower", lower, -178.0)):
        gs = [(g, gate(g)) for g in group]
        gs = [(g, b) for g, b in gs if b is not None]
        if len(gs) < 2:
            print(f"  {tag} bus: too few gates found, skipped")
            continue
        xs = sorted(b.center().x for _, b in gs)
        # Spine across the full span, then a stub down or up to each gate.
        wire("M5", xs[0], ybus, xs[-1], ybus, 1.0)
        for g, b in gs:
            drop(b.center().x, b.center().y, "M5", cols=1, rows=2, frm="Metal2")
            wire("M2", b.center().x, b.center().y, b.center().x,
                 b.center().y + 0.5, 0.4)
            wire("M5", b.center().x, b.center().y, b.center().x, ybus, 0.6)
        print(f"  {tag} bus at y {ybus}: {len(gs)} gates from "
              f"x {xs[0]:.1f} to {xs[-1]:.1f}")

'''

s = s.replace('layout.write(OUT)', new + 'layout.write(OUT)')

s = s.replace('''    "MB2A_D": (-143.8, -200.0, "M5"), "MB2B_D": (143.8, -200.0, "M5"),
})''',
'''    "MB2A_D": (-143.8, -200.0, "M5"), "MB2B_D": (143.8, -200.0, "M5"),
    "casc_bus": (-30.0, -172.0, "M5"), "lower_bus": (-30.0, -178.0, "M5"),
})''')

p.write_text(s)
print("gate buses added")
