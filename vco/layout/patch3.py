import pathlib
p = pathlib.Path('route_v2.py'); s = p.read_text()
# A 1.0 x 0.16 um Metal2 shape sits at RB2's bottom pin, under the 0.21 um
# minimum. It comes from the via_stack PCell's own Metal2 at this pin, not from
# any route. Overlap it with a legal rectangle so the merged shape is compliant.
old = '    drop(r2_bot.center().x, r2_bot.center().y, "M2", cols=2, rows=2)'
new = (old + "\n"
       '    top.shapes(LI["M2"]).insert(pya.DBox(\n'
       '        snap(r2_bot.center().x - 0.5), snap(r2_bot.center().y - 0.3),\n'
       '        snap(r2_bot.center().x + 0.5), snap(r2_bot.center().y + 0.3)))')
assert old in s
s = s.replace(old, new)
p.write_text(s); print("legal Metal2 patch over RB2's pin")
