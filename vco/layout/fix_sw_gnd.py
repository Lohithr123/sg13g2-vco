import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The switch guard rings at x -8 are in a clear TopMetal1 column, but the
# detour test caught them on y as well as x, so they ran the full width of the
# die along the channel and collected the tail and both control lines.
# The detour is only needed for points sitting behind a coupling capacitor;
# x -8 is not one of them.
old = '    if CAP_L < gx < CAP_R and gy > -210.0:'
new = '    if -71.0 < gx < 71.0 and gy < -185.0:'
assert old in s
s = s.replace(old, new)
p.write_text(s)
print("detour now applies only to the mirror row behind the caps")
