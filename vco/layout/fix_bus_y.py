import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The bus heights were measured from the instance bbox, which includes the
# guard ring extending 1.21 um below the diffusion — so the source bus at
# +1.0 landed in the gap between the ring and the strips and contacted
# nothing. Measure from the strips themselves.
old = '''    ybase = inst.dbbox().bottom
    ys, yd, yg = ybase + y_src, ybase + y_drn, ybase + y_gate'''
new = '''    sb = strips[0].bottom
    sh_ = strips[0].height()
    ys = sb + 0.20 * sh_
    yd = sb + 0.55 * sh_
    yg = sb + 0.85 * sh_'''
assert old in s
s = s.replace(old, new)
p.write_text(s)
print("bus heights now derived from the diffusion strips")
