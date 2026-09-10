import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
old = '''    ys = sb + 0.25 * sh_
    yd = sb + 0.70 * sh_
    yg = strips[0].top + 0.45          # above the diffusion, on the poly overhang'''
new = '''    ys = sb + 0.20 * sh_
    yd = sb + 0.55 * sh_
    yg = sb + 0.85 * sh_'''
assert old in s
s = s.replace(old, new)
p.write_text(s)
print("reverted to the working bus heights")
