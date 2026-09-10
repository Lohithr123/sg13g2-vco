import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# All 120 new vias are exactly 0.19 um, so the commoning geometry is right.
# The remaining violations are collisions between the 0.6 um pads and the
# terminal routing already present — a 15 nm gap at the tail mirror, and
# Metal1/Metal2 spacing at the switches.
#
# The via needs 0.19 um plus enclosure; a 0.4 um pad still gives 0.105 um of
# Metal1 around it and opens 0.1 um of clearance on every side.
s = s.replace('    PAD = 0.30          # half-width of the local Metal1 widening',
              '    PAD = 0.20          # half-width: via 0.19 + 0.105 enclosure')
p.write_text(s)
print("pads reduced to 0.4 um square")
