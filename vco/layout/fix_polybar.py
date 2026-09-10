import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# Gat.d: minimum GatPoly space to Activ is 0.07 um, and the bar started exactly
# at the diffusion edge — 100 violations. The gates overhang the active area by
# 0.18 um, so starting the bar 0.07 um clear still leaves 0.11 um of overlap
# with each gate, which is what commons them.
old = '''        gy0 = strips[0].top
        gy1 = min(g.top for g in gates)'''
new = '''        gy0 = strips[0].top + 0.075     # Gat.d: 0.07 um clear of Activ
        gy1 = min(g.top for g in gates)'''
assert old in s
s = s.replace(old, new)
p.write_text(s)
print("poly bar moved 0.075 um clear of the active area")
