import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# Two problems, one cause. The gate bus sits at 85% of the strip height, over
# the diffusion — on a 4.36 um tall switch the three buses are only 1.5 um
# apart and the gate bus shorts to the source and drain buses. And on the
# 139 um mirrors the source bus reaches far enough to merge two devices.
#
# The gate poly extends past the diffusion at both ends (y -0.18 to 7.18 on a
# 0..7 strip), so contact the gates ABOVE the active area where nothing else
# is, rather than over it.
old = '''    ys = sb + 0.20 * sh_
    yd = sb + 0.55 * sh_
    yg = sb + 0.85 * sh_'''
new = '''    ys = sb + 0.25 * sh_
    yd = sb + 0.70 * sh_
    yg = strips[0].top + 0.45          # above the diffusion, on the poly overhang'''
assert old in s
s = s.replace(old, new)
p.write_text(s)
print("gate bus moved above the active area")
