import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
old = s[s.index('    sb = strips[0].bottom'):s.index('    print(f"  {tag:8} {len(src)}')]
new = '''    # The diffusion strips are 0.16 um wide and a via stack is 0.29 um at its
    # narrowest, so a via placed on a strip overhangs onto the poly and the
    # neighbouring contacts — 192 DRC violations across ten devices.
    #
    # But the strips are already Metal1. They only need joining, not a layer
    # change. Extend each one past the array and bus it there: drains upward,
    # sources downward, so the two bars never see each other's fingers.
    #
    # The gates are poly and do need a real contact, but the poly overhangs the
    # diffusion at both ends, so that contact goes where nothing else is.
    src = strips[0::2]
    drn = strips[1::2]

    stop_ = strips[0].top
    sbot_ = strips[0].bottom

    y_dbus = stop_ + 1.6           # clear of the guard ring bar above
    y_sbus = sbot_ - 1.6           # and below

    for b in drn:
        wire("M1", b.center().x, stop_, b.center().x, y_dbus, b.width())
    if len(drn) > 1:
        wire("M1", drn[0].center().x, y_dbus, drn[-1].center().x, y_dbus, 0.4)

    for b in src:
        wire("M1", b.center().x, sbot_, b.center().x, y_sbus, b.width())
    if len(src) > 1:
        wire("M1", src[0].center().x, y_sbus, src[-1].center().x, y_sbus, 0.4)

    # Gates: contact on the poly overhang above the diffusion, bus on Metal2.
    yg = stop_ + 0.4
    for b in gates:
        drop(b.center().x, yg, "M2", cols=1, rows=1, frm="GatPoly")
    if len(gates) > 1:
        wire("M2", gates[0].center().x, yg, gates[-1].center().x, yg, 0.4)

'''
s = s.replace(old, new)
p.write_text(s)
print("buses now drawn on Metal1, no vias on the strips")
