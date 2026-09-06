import pathlib
p = pathlib.Path('route_v2.py'); s = p.read_text()
# The drain via stack leaves a 0.12 um Metal5 sliver, under minimum width.
# The mirror's diffusion strips are 7 um tall, so a tall patch fits easily and
# swallows the sliver when merged.
old = '        drop(d2.center().x, d2.center().y, "M5", cols=1, rows=8)'
new = (old + "\n"
       '        top.shapes(LI["M5"]).insert(pya.DBox(\n'
       '            snap(d2.center().x - 0.3), snap(d2.center().y - 1.6),\n'
       '            snap(d2.center().x + 0.3), snap(d2.center().y + 1.6)))')
assert old in s
s = s.replace(old, new)
p.write_text(s)
print("Metal5 patch over the drain stack")
