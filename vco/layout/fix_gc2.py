import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# rows=1 leaves 0.29 x 0.21 = 0.061 um2 of Metal1 against the 0.144 minimum
# (M1.d). rows=2 gives 0.21 x 0.70 = 0.147, over the limit — and the poly bus
# above the diffusion has room for it, unlike the gate itself.
old = '    drop(g.center().x, gy, "M2", cols=1, rows=1, frm="GatPoly")'
new = '    drop(g.center().x, gy + 0.25, "M2", cols=1, rows=2, frm="GatPoly")'
assert s.count(old) == 1
s = s.replace(old, new)
s = s.replace('    path("M2", [(g.center().x, gy),',
              '    path("M2", [(g.center().x, gy + 0.25),')
p.write_text(s)
print("contact enlarged to rows=2 and lifted clear")
