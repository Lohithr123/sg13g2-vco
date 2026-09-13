import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The band-select gate contact sits at strips.bottom - 0.45 = -110.45, but the
# gate poly only reaches -110.18 and the guard ring's bottom bar starts at
# -110.88. The contact is past the poly, landing on the ring — so nb0 and nb1
# are tied to ground.
#
# The commoning already busses the gates on poly above the diffusion, so the
# contact does not need to be below it at all. Put it on the poly bus instead,
# where there is clear space.
old = '    gy = g.bottom - 0.05'
new = '    gy = g.top + 0.10          # on the poly bus above the diffusion'
assert s.count(old) == 1
s = s.replace(old, new)
p.write_text(s)
print("band-select contact moved to the poly bus")
