import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

old = '''    for group, ylev in ((src, y_s), (drn, y_d)):
        _v1 = pya.Region(top.begin_shapes_rec(layout.layer(19, 0)))'''

new = '''    for group, ylev in ((src, y_s), (drn, y_d)):
        # A terminal with a single strip needs nothing: the strip IS the
        # terminal and the existing routing already lands on it. Drawing a pad
        # and via there adds metal beside the opposite terminal for no gain —
        # on XSW1 the drain is one strip, and its stray pad is what tied the
        # device to its own gate net.
        if len(group) < 2:
            continue
        _v1 = pya.Region(top.begin_shapes_rec(layout.layer(19, 0)))'''

assert s.count(old) == 1, f"matched {s.count(old)}"
s = s.replace(old, new)

# The bus/stub block is now unconditionally reached for groups of 2+, so its
# own len check is redundant but harmless; leave it.
p.write_text(s)
print("single-strip terminals no longer get a pad or via")
