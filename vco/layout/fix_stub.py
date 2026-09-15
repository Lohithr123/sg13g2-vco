import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The stubs run from each pad straight out of the array, so a source stub
# passes every drain strip below it and vice versa. On the 0.51 um pitch
# switches a 0.3 um stub touches its neighbours.
#
# Offset each stub into the middle of the gap next to its own strip, away from
# the opposite net: sources step toward the outside, drains toward the inside.
old = '''            for b in group:
                wire("M2", b.center().x, ylev, b.center().x, _yb, 0.3)
            wire("M2", group[0].center().x, _yb,
                 group[-1].center().x, _yb, 0.3)'''
new = '''            _half = 0.5 * (strips[1].center().x - strips[0].center().x) \\
                    if len(strips) > 1 else 0.69
            _off = _dir * 0.0            # placeholder, set per strip below
            for b in group:
                # Step into the gap beside this strip before leaving the array.
                _sx = b.center().x + (_half * 0.5 if ylev == y_d else -_half * 0.5)
                wire("M2", b.center().x, ylev, _sx, ylev, 0.3)
                wire("M2", _sx, ylev, _sx, _yb, 0.3)
            _x0 = group[0].center().x + (_half * 0.5 if ylev == y_d else -_half * 0.5)
            _x1 = group[-1].center().x + (_half * 0.5 if ylev == y_d else -_half * 0.5)
            wire("M2", _x0, _yb, _x1, _yb, 0.3)'''
assert s.count(old) == 1
s = s.replace(old, new)
p.write_text(s)
print("stubs offset into the gap beside each strip")
