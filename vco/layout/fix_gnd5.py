import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The tail is still on ground. XMT2 is the tail mirror: its drain carries the
# tail net and its guard ring must go to ground, and the two are a few microns
# apart on the same device. The ring contact at the right edge sits beside the
# drain stack.
#
# XMT2 spans x -28.1..-11.9, its drain is at -25.5 and its source at -26.9 —
# both toward the left. So the RIGHT edge is the clear one here, which is where
# the contact already is... so try the top edge instead: the device is 9.4 um
# tall and everything else approaches it horizontally.
old = '        gnd_pts.append((nm + "_ring", b.right - 0.15, b.center().y))'
new = '        gnd_pts.append((nm + "_ring", b.center().x, b.top - 0.15))'
assert old in s
s = s.replace(old, new)
p.write_text(s)
print("guard rings contacted at their top edge")
