import pathlib, re
p = pathlib.Path('build_layout.py'); s = p.read_text()

# --- bank: capacitors out, switches off the centre line ---------------------
old = s[s.index('for i, (y, cval, wsw, ngsw) in enumerate(BANK):'):
        s.index('print("\\n=== fixed tank capacitor ===")')]
new = '''for i, (y, cval, wsw, ngsw) in enumerate(BANK):
    # Capacitors at +/-25 rather than +/-14, and the switch offset from x = 0.
    #
    # The first floorplan put both bank switches on the centre line with their
    # source and drain pins 0.35 um apart — a gap fixed by gate length and
    # contact spacing, not by device size. The tail net also has to pass from
    # the emitters at +/-9 down to the mirror at x -25, through the same strip.
    # Every route into that region collided with another: nine attempts, nine
    # different shorts.
    #
    # Moving the switch to x = -8 gives the tail a clear corridor at x = 0, and
    # widening the capacitor spacing leaves room to approach each switch pin
    # from opposite sides without the two branches converging.
    place("cmim", {"Calculate": "w&l", "C": cval}, -25.0, y, label=f"CB{i}A")
    place("cmim", {"Calculate": "w&l", "C": cval},  25.0, y, mirror=True,
          label=f"CB{i}B")
    place("nmos", {"w": wsw, "l": "0.13u", "ng": ngsw, "m": "1",
                   "guardRingType": "psub"}, -8.0, y, label=f"XSW{i}")

'''
s = s.replace(old, new)

# --- fixed tank cap and varactor off the centre too -------------------------
s = s.replace('"C": "31.6f"}, 0.0, -95.0, label="CT")',
              '"C": "31.6f"}, 8.0, -95.0, label="CT")')
s = s.replace('"Nx": 4}, 0.0, -172.0, label="XCV")',
              '"Nx": 4}, 8.0, -172.0, label="XCV")')

p.write_text(s)
print("floorplan widened")
