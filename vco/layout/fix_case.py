import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The SPICE reader folds the netlist to uppercase — the cross-reference shows
# VCC, GND, VG, OUTP against the layout's lowercase gnd. No net name matches,
# so LVS has no anchor to start from and NOTHING pairs, which is why every
# cross-reference entry has one side empty despite identical device counts.
old = '    top.shapes(li).insert(pya.DText(nm, pya.DTrans(snap(px), snap(py))))'
new = '    top.shapes(li).insert(pya.DText(nm.upper(), pya.DTrans(snap(px), snap(py))))'
assert s.count(old) == 1
s = s.replace(old, new)
p.write_text(s)
print("port labels uppercased to match the SPICE reader")
