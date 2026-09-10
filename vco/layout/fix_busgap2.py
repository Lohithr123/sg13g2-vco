import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# 1.6 um hit the guard ring; 0.45 um sits where the terminal routing lands.
# The usable window is between them, and the guard ring bar starts 0.88 um out,
# so 0.65 um centres the bus in the gap with clearance both ways.
old = '''    y_dbus = stop_ + 0.45          # inside the 0.88 um gap to the guard ring
    y_sbus = sbot_ - 0.45'''
new = '''    y_dbus = stop_ + 0.65          # centred in the gap to the guard ring
    y_sbus = sbot_ - 0.65'''
assert old in s
s = s.replace(old, new)
p.write_text(s)
print("buses at 0.65 um")
