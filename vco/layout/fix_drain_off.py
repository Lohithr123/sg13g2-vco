import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

old = '''            for b in group:
                wire("M2", b.center().x, ylev, b.center().x, _out, 0.26)
            wire("M2", group[0].center().x, _out,
                 group[-1].center().x, _out, 0.26)'''

new = '''            # MEASURED on XSW1: the drain bus runs up to strips.top + 0.45,
            # and the band-select gate contact sits at the same height with a
            # poly pad spanning x -9.115..-8.415. The drain stub at x -8.51
            # spans -8.64..-8.38 and overlaps it, tying the drain to nb1.
            #
            # The gate sits on the low side of the first drain strip, so
            # offsetting the drain stubs the other way clears it. Sources go
            # down and need no offset: nothing is below them but the ring.
            _dx = 0.25 if ylev == y_d else 0.0
            for b in group:
                wire("M2", b.center().x, ylev, b.center().x + _dx, ylev, 0.26)
                wire("M2", b.center().x + _dx, ylev,
                     b.center().x + _dx, _out, 0.26)
            wire("M2", group[0].center().x + _dx, _out,
                 group[-1].center().x + _dx, _out, 0.26)'''

assert s.count(old) == 1, f"matched {s.count(old)}"
s = s.replace(old, new)
p.write_text(s)
print("drain stubs offset 0.25 um clear of the gate contact")
