import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# Measured: the source bus runs x -8.510..-7.490 at y -109.5, and the drain
# strip's Metal2 sits at -8.105..-7.895 — directly under it. The two source
# strips are the outer ones, the drain is between them, so a straight bus
# between sources always crosses the drain.
#
# Route the source bus below the strips instead. Measured on this device: the
# strips end at y -110.00 and the guard ring's inner edge is at -110.88, so
# there is 0.88 um, and a 0.3 um bus at -110.45 clears both by 0.29 um.
old = '''        if len(group) > 1:
            wire("M2", group[0].center().x, ylev,
                 group[-1].center().x, ylev, 0.4)'''
new = '''        if len(group) > 1:
            # Sources are the outer strips with the drain between them, so a
            # straight bus at strip level would cross the opposite net. Drop
            # below the diffusion, where only the guard ring is, and come back
            # up to each strip.
            if ylev == y_s:
                _yb = snap(strips[0].bottom - 0.45)
                for b in group:
                    wire("M2", b.center().x, ylev, b.center().x, _yb, 0.3)
                wire("M2", group[0].center().x, _yb,
                     group[-1].center().x, _yb, 0.3)
            else:
                wire("M2", group[0].center().x, ylev,
                     group[-1].center().x, ylev, 0.4)'''
assert s.count(old) == 1
s = s.replace(old, new)
p.write_text(s)
print("source bus routed below the diffusion")
