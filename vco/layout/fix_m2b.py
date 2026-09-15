import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# Measured: the gate contact pad spans x -20.105..-19.895 and the drain stub
# -19.805..-19.505 — 90 nm apart against the 210 nm M2.b minimum. Both are
# mine. The drain stub is offset by half a half-pitch from its strip, which on
# these devices lands it beside the gate contact.
#
# The gates sit midway between strips, so offsetting drain stubs toward the
# gate is what causes this. Offset them the other way instead: away from the
# gate, into the gap on the far side.
old = '''                if ylev == y_d:
                    _sx = b.center().x + _half * 0.5'''
new = '''                if ylev == y_d:
                    _sx = b.center().x - _half * 0.5'''
assert s.count(old) == 1
s = s.replace(old, new)
s = s.replace('''                _x0 = group[0].center().x + (_half * 0.5 if ylev == y_d else -_half * 0.5)
                _x1 = group[-1].center().x + (_half * 0.5 if ylev == y_d else -_half * 0.5)''',
'''                _x0 = group[0].center().x - _half * 0.5
                _x1 = group[-1].center().x - _half * 0.5''')
p.write_text(s)
print("drain stubs offset away from the gate contacts")
