import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
for r in ("r1_bot", "r2_bot"):
    old = f'    drop({r}.center().x, {r}.center().y, "M2", cols=2, rows=2)'
    new = (old + "\n"
           f'    wire("M2", {r}.center().x - 0.4, {r}.center().y,\n'
           f'         {r}.center().x + 0.4, {r}.center().y, 0.4)')
    s = s.replace(old, new)
p.write_text(s)
print("pin patches added")
