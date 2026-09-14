import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The band-select line drops 0.4 um wide from the gate contact straight through
# the gap between the source and drain stacks, which are 0.31 um apart. Its
# edges touch both — the gate line is what shorts drain to source on the
# switches, not the commoning buses.
#
# Leave sideways along the poly bus first, clear of the device, then drop.
old = '''    path("M2", [(g.center().x, gy),
                (g.center().x, yb - 8.0),'''
new = '''    path("M2", [(g.center().x, gy),
                (g.center().x - 3.0, gy),
                (g.center().x - 3.0, yb - 8.0),'''
assert s.count(old) == 1
s = s.replace(old, new)
p.write_text(s)
print("band-select line steps clear before dropping")
