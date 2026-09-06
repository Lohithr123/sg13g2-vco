import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# A 1.0 x 0.16 um Metal2 sliver sits at the resistor pins — under the 0.21 um
# minimum width. Cover it with a patch tall enough to be legal: the pin is
# 0.26 um tall and the resistor body 0.96 um wide, so 0.9 x 0.5 fits.
for r in ("r1_bot", "r2_bot", "r1_top", "r2_top"):
    old = f'    drop({r}.center().x, {r}.center().y, "M2", cols=2, rows=2)'
    new = (old + "\n"
           f'    top.shapes(LI["M2"]).insert(pya.DBox(\n'
           f'        snap({r}.center().x - 0.45), snap({r}.center().y - 0.25),\n'
           f'        snap({r}.center().x + 0.45), snap({r}.center().y + 0.25)))')
    s = s.replace(old, new)
p.write_text(s)
print("resistor pin patches widened")
