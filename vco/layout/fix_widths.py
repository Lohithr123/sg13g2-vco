import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# Gat.a: minimum poly width is 0.13 um and the bar came out 0.105. The gates
# overhang the diffusion by 0.18 um and the guard ring is 0.88 um away, so the
# bar can extend past the gate tops with room to spare.
old = '''        gy0 = strips[0].top + 0.075     # Gat.d: 0.07 um clear of Activ
        gy1 = min(g.top for g in gates)'''
new = '''        gy0 = strips[0].top + 0.075     # Gat.d: 0.07 um clear of Activ
        gy1 = gy0 + 0.16                # Gat.a: 0.13 um minimum poly width'''
assert old in s
s = s.replace(old, new)
p.write_text(s)
print("poly bar widened to 0.16 um")
