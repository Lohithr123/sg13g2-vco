import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The band-select line drops 0.4 um wide from the gate straight through the
# 0.31 um gap between the source stack (ending x -8.410) and the drain stack
# (starting x -8.100). Its edges at -8.455 and -8.055 touch both, shorting
# drain to source. That is the fault on both bank switches, and the same
# pattern on the two buffer cascodes.
#
# Step sideways along the poly bus before dropping.
old = '''    path("M2", [(g.center().x, gy - 0.45),
                (g.center().x, yb - 8.0),'''
new = '''    path("M2", [(g.center().x, gy - 0.45),
                (g.center().x - 3.0, gy - 0.45),
                (g.center().x - 3.0, yb - 8.0),'''
assert s.count(old) == 1, f"matched {s.count(old)}"
s = s.replace(old, new)
p.write_text(s)
print("band-select line steps 3 um clear before dropping")
