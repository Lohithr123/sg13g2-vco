import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# All 28 remaining violations are at the two bank switches, x -7.7..-9.1. Their
# terminal stacks from the earlier routing sit at the same heights as the new
# pads — 15 nm and 90 nm gaps.
#
# The switch strips are 4 um tall, so the pads can move vertically clear of the
# terminal stacks instead of competing with them in x. Push the source and
# drain levels apart: 0.12 and 0.62 of the strip height rather than 0.20 / 0.50.
old = '''    y_s = snap(y0 + 0.20 * h)
    y_d = snap(y0 + 0.50 * h)'''
new = '''    y_s = snap(y0 + 0.12 * h)
    y_d = snap(y0 + 0.62 * h)'''
assert old in s
s = s.replace(old, new)
p.write_text(s)
print("source and drain levels moved apart")
