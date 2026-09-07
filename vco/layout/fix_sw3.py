import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# Left edge puts the stack where the band-select lines run — they all leave to
# the left. The right edge of each device is clear: outn's bank connection
# comes in on Metal5 from x +25, well past it.
old = '        gnd_pts.append((nm + "_ring", b.left + 0.15, b.center().y))'
new = '        gnd_pts.append((nm + "_ring", b.right - 0.15, b.center().y))'
assert old in s
s = s.replace(old, new)
p.write_text(s)
print("guard rings contacted at their right edge")
