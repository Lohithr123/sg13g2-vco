import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# Measured: the band-select line spans x -8.455..-8.055, the source pad
# -8.615..-8.405 and the drain pad -8.105..-7.895. The line overlaps both by
# 50 nm on each side — it drops through the 0.31 um gap between the strips
# because the gate contact sits between them.
#
# Leave sideways along the poly pad first, out past the device edge at -9.66,
# then descend where nothing is.
old = '''    path("M2", [(g.center().x, cy),
                (g.center().x, yb - 8.0),'''
new = '''    path("M2", [(g.center().x, cy),
                (g.center().x - 2.5, cy),
                (g.center().x - 2.5, yb - 8.0),'''
assert s.count(old) == 1
s = s.replace(old, new)
# and restore the pad size, which was not the problem
s = s.replace('''    _pitch = (strips[1].center().x - strips[0].center().x
              if len(strips) > 1 else 1.38)
    PAD = min(0.20, max(0.115, 0.5 * (_pitch - 0.22) - 0.02))''',
              '    PAD = 0.20          # half-width: via 0.19 + 0.105 enclosure')
p.write_text(s)
print("band-select line steps clear before descending; pad restored")
