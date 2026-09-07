import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# TopMetal1 needs 1.64 um width, and path() draws each segment separately, so a
# corner between two 2 um wires leaves a 1.3 um notch on the inside. Widen the
# ground detour to 2.5 um: the corner notch then exceeds the minimum.
old = '''        path("TM1", [(gx, gy), (gx, CHAN_Y), (xdet, CHAN_Y),
                     (xdet, GND_Y)], w=2.0)'''
new = '''        path("TM1", [(gx, gy), (gx, CHAN_Y), (xdet, CHAN_Y),
                     (xdet, GND_Y)], w=2.5)'''
assert old in s
s = s.replace(old, new)
s = s.replace('        path("TM1", [(gx, gy), (gx, GND_Y)], w=2.0)',
              '        path("TM1", [(gx, gy), (gx, GND_Y)], w=2.5)')
p.write_text(s)
print("ground routes widened to 2.5 um")
