import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# PAD = 0.20 is a constant, but the strip pitch is not: the mirrors are on a
# 1.38 um pitch and the bank switches on 0.51 um. On the switches a 0.4 um pad
# leaves 0.11 um between neighbours, under the 0.21 um Metal2 minimum, and the
# bus connecting them merges all three strips into one polygon — drain shorted
# to source.
#
# Size the pad from the measured pitch: half the gap between adjacent strips,
# less the required clearance, and never more than the 0.20 used on the wide
# devices.
old = '    PAD = 0.20          # half-width: via 0.19 + 0.105 enclosure'
new = ('    _pitch = (strips[1].center().x - strips[0].center().x\n'
       '              if len(strips) > 1 else 1.38)\n'
       '    PAD = min(0.20, max(0.115, 0.5 * (_pitch - 0.22) - 0.02))')
assert s.count(old) == 1
s = s.replace(old, new)
p.write_text(s)
print("pad half-width now derived from the measured strip pitch")
