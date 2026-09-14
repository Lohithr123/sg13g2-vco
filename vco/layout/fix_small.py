import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# On a three-strip device the source bus spans the whole width and passes over
# the single drain strip's pad, merging both buses into one Metal2 polygon —
# drain shorted to source on all four of the tight devices.
#
# A group with one member needs no bus at all: the strip is already the
# terminal. Only bus groups of two or more, and skip the pad too, so nothing
# is added on a layer that has no room.
old = '''    for group, ylev in ((src, y_s), (drn, y_d)):'''
new = '''    for group, ylev in ((src, y_s), (drn, y_d)):
        if len(group) < 2:
            continue          # single strip: already the terminal, no bus needed'''
assert s.count(old) == 1
s = s.replace(old, new)
p.write_text(s)
print("single-strip groups no longer bussed")
