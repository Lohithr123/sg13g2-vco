import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# Two violations left, both at the bank switches: my Metal2 bus at x -7.69 sits
# 205 nm from the terminal stack's Metal2 at -7.895, and M2.b wants 210 nm.
# Five nanometres short. Narrow the bus from 0.3 to 0.24 um — still above the
# 0.21 um minimum width — which opens 30 nm on each side.
s = s.replace('''            wire("M2", group[0].center().x, ylev,
                 group[-1].center().x, ylev, 0.3)''',
'''            wire("M2", group[0].center().x, ylev,
                 group[-1].center().x, ylev, 0.24)''')
p.write_text(s)
print("bus narrowed to 0.24 um")
