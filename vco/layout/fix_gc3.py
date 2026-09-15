import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The poly bus is 0.16 um tall and a contact needs ~0.30 um of poly around it,
# so it cannot sit on the bus as drawn — Cnt.b, Cnt.e, Cnt.f and Gat.d.
# Widen the poly locally at the contact, the same way the diffusion strips are
# widened for their vias.
old = '    drop(g.center().x, gy + 0.25, "M2", cols=1, rows=2, frm="GatPoly")'
new = ('    top.shapes(LI["poly"]).insert(pya.DBox(\n'
       '        snap(g.center().x - 0.35), snap(gy - 0.05),\n'
       '        snap(g.center().x + 0.35), snap(gy + 0.55)))\n'
       '    drop(g.center().x, gy + 0.25, "M2", cols=1, rows=2, frm="GatPoly")')
assert s.count(old) == 1
s = s.replace(old, new)
p.write_text(s)
print("poly widened locally under the contact")
