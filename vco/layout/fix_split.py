import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The loop used one y for the pad, the via and the bar. Moving the bar below
# the device moved the pads with it, off the strips entirely, so nothing
# commoned — 66 devices again.
#
# The pad must sit ON the strip (that is where the via contacts it) and the bar
# OUTSIDE the array (so it does not cross the opposite net's strips), with a
# short Metal2 stub joining them.
old = '''    y_s = snap(strips[0].bottom - 0.55)
    for group, ylev in ((src, y_s), (drn, y_d)):'''
new = '''    y_s = snap(y0 + 0.12 * h)              # pads sit on the strips
    ybar_s = snap(strips[0].bottom - 0.55)  # bars run outside the array
    ybar_d = snap(strips[0].top + 0.55)
    for group, ylev, ybar in ((src, y_s, ybar_s), (drn, y_d, ybar_d)):'''
assert s.count(old) == 1
s = s.replace(old, new)

old2 = '''        if len(group) > 1:
            wire("M2", group[0].center().x, ylev,
                 group[-1].center().x, ylev, 0.4)'''
new2 = '''        if len(group) > 1:
            # Stub from each pad out to the bar, then the bar itself.
            for b in group:
                wire("M2", b.center().x, ylev, b.center().x, ybar, 0.3)
            wire("M2", group[0].center().x, ybar,
                 group[-1].center().x, ybar, 0.3)'''
assert s.count(old2) == 1
s = s.replace(old2, new2)
p.write_text(s)
print("pads on the strips, bars outside the array")
