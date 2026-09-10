import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The shape at x -7.69 is a landing pad from the terminal routing, 205 nm from
# the switch's terminal stack at -7.895 — same net, but neither overlapping nor
# clear, so M2.b flags the gap.
#
# The bus already runs between them at x -8.51..-7.49. Widening it to 0.4 um
# makes it tall enough to overlap both, merging the three shapes into one.
s = s.replace('''            wire("M2", group[0].center().x, ylev,
                 group[-1].center().x, ylev, 0.24)''',
'''            wire("M2", group[0].center().x, ylev,
                 group[-1].center().x, ylev, 0.4)''')
p.write_text(s)
print("bus widened to 0.4 um to merge with the terminal pads")
