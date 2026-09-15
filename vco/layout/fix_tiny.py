import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# On the 8 um switch the strips are 0.51 um apart, so half the gap is 0.255 um
# and a 0.3 um stub still overlaps its neighbour. There is no offset that works.
#
# But that device has three strips: two sources and one drain. The drain needs
# no bus, and the two sources are the outer strips — so they can be joined
# below the diffusion with the stubs running down OUTSIDE the array entirely,
# clear of the drain between them.
old = '''                _sx = b.center().x + (_half * 0.5 if ylev == y_d else -_half * 0.5)'''
new = '''                if ylev == y_d:
                    _sx = b.center().x + _half * 0.5
                elif len(group) == 2 and len(strips) == 3:
                    # Outer sources: step away from the drain, not toward it.
                    _sx = b.center().x + (-_half if b is group[0] else _half)
                else:
                    _sx = b.center().x - _half * 0.5'''
assert s.count(old) == 1
s = s.replace(old, new)
s = s.replace('''            _x0 = group[0].center().x + (_half * 0.5 if ylev == y_d else -_half * 0.5)
            _x1 = group[-1].center().x + (_half * 0.5 if ylev == y_d else -_half * 0.5)''',
'''            if ylev == y_s and len(group) == 2 and len(strips) == 3:
                _x0 = group[0].center().x - _half
                _x1 = group[-1].center().x + _half
            else:
                _x0 = group[0].center().x + (_half * 0.5 if ylev == y_d else -_half * 0.5)
                _x1 = group[-1].center().x + (_half * 0.5 if ylev == y_d else -_half * 0.5)''')
p.write_text(s)
print("three-strip devices: sources routed outside the array")
