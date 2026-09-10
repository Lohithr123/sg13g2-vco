import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# top.shapes() only sees shapes drawn directly in the top cell; the terminal
# via stacks are instances, so the check never fired. begin_shapes_rec walks
# the hierarchy.
old = '        _v1 = pya.Region(top.shapes(layout.layer(19, 0)))'
new = '        _v1 = pya.Region(top.begin_shapes_rec(layout.layer(19, 0)))'
assert old in s
s = s.replace(old, new)
p.write_text(s)
print("via check now walks the hierarchy")
