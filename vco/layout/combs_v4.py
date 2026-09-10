import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

old = s[s.index('    for b in gates:\n        drop(b.center().x, y_g'):
        s.index('    print(f"  {tag:8} {len(src)}s + {len(drn)}d strips')]

new = '''    # Gates need no contact at all.
    #
    # A contact is 0.16 um wide. The bank switches use l=0.13u, so their gate
    # poly is narrower than the contact that would sit on it — 72 Cnt.b
    # violations. And on the mirrors the contact was landing on poly over the
    # active area, which is not allowed anywhere.
    #
    # But poly is conductive. The gates already extend 0.18 um past the
    # diffusion at each end, so a poly bar across that overhang commons them
    # directly. And because the existing gate routing connects to the first
    # gate, bussing them on poly drives all of them with nothing added.
    if len(gates) > 1:
        gy0 = strips[0].top
        gy1 = min(g.top for g in gates)
        if gy1 > gy0 + 0.05:
            top.shapes(LI["poly"]).insert(pya.DBox(
                snap(gates[0].left), snap(gy0),
                snap(gates[-1].right), snap(gy1)))

'''

s = s.replace(old, new)
p.write_text(s)
print("gates bussed on poly, no contacts")
