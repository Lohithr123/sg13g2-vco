import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

old = '''        px = pin.center().x
        path(lyr, [(plate.center().x, plate.center().y),
                   (plate.center().x, ych),
                   (px, ych),
                   (px, pin.center().y + (2.0 if ych > yb else -2.0))],
             w=0.4)'''

new = '''        px = pin.center().x
        if ych == ybot:
            # MEASURED: the B-side capacitor is at x +25 and its switch at
            # x -8, so this horizontal crosses x = 0 — where the tail runs on
            # Metal5 from y -104 to -190. Both bank rows (y -113.5, -135.5)
            # fall inside that span, so S0B and S1B extracted as E: the B-side
            # switch nodes were shorted to the tail.
            #
            # Cross on Metal3 instead. At these heights Metal3 holds nothing
            # between x -8 and +31 (outp is at x -16), and the via corners are
            # clear of outn's Metal4 (at x +16 and along y -103).
            _px0 = plate.center().x
            path("M5", [(_px0, plate.center().y), (_px0, ych)], w=0.4)
            drop(_px0, ych, "M5", cols=2, rows=2, frm="Metal3")
            path("M3", [(_px0, ych), (px, ych)], w=0.4)
            drop(px, ych, "M5", cols=2, rows=2, frm="Metal3")
            path("M5", [(px, ych),
                        (px, pin.center().y - 2.0)], w=0.4)
        else:
            path(lyr, [(plate.center().x, plate.center().y),
                       (plate.center().x, ych),
                       (px, ych),
                       (px, pin.center().y + (2.0 if ych > yb else -2.0))],
                 w=0.4)'''

assert s.count(old) == 1, f"matched {s.count(old)}"
s = s.replace(old, new)
p.write_text(s)
print("B-side bank crossing moved to Metal3")
