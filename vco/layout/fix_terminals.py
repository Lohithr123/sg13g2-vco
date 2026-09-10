import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The gap between the strips and the guard ring is 0.88 um. A 0.4 um bus with
# 0.21 um clearance needs 0.82 of it, so the gap holds the bus OR the terminal
# routing, not both — which is why 0.45 shorted the terminal nets and 1.6 hit
# the ring.
#
# Narrow the bus to 0.3 um. That needs 0.72 um, leaving 0.16 um of margin, and
# the terminal stacks land ON the bus rather than beside it.
s = s.replace('''    y_dbus = stop_ + 0.65          # centred in the gap to the guard ring
    y_sbus = sbot_ - 0.65''',
'''    y_dbus = stop_ + 0.42          # 0.88 um gap: 0.3 um bus + 0.21 either side
    y_sbus = sbot_ - 0.42''')
s = s.replace('        wire("M1", drn[0].center().x, y_dbus, drn[-1].center().x, y_dbus, 0.4)',
              '        wire("M1", drn[0].center().x, y_dbus, drn[-1].center().x, y_dbus, 0.3)')
s = s.replace('        wire("M1", src[0].center().x, y_sbus, src[-1].center().x, y_sbus, 0.4)',
              '        wire("M1", src[0].center().x, y_sbus, src[-1].center().x, y_sbus, 0.3)')
p.write_text(s)
print("bus narrowed to 0.3 um at 0.42 um offset")
