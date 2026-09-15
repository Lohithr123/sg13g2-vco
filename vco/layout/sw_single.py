import pathlib

p = pathlib.Path('build_layout.py')
s = p.read_text()

old = '''    (-108.0, "10f", "8u",  "2"),
    (-130.0, "20f", "16u", "4"),'''

new = '''    # MEASURED: with ng=2 and ng=4 the switch strips sit on a 0.51 um pitch,
    # which leaves 0.300 um between adjacent via stacks. A compliant Metal2
    # track needs 0.21 width plus 0.21 clearance either side = 0.630 um, so
    # nothing can be routed between those strips on any layer. That is what
    # left four irreducible M2.b violations when the fingers were commoned.
    #
    # ng=1 gives one strip per terminal, so there is nothing to common and the
    # commoning adds no metal to these devices at all. The finger is wider and
    # the device grows in x, but the switches sit at x -8 with the bank
    # capacitors at +/-25, so there is room.
    (-108.0, "10f", "8u",  "1"),
    (-130.0, "20f", "16u", "1"),'''

assert s.count(old) == 1, f"matched {s.count(old)}"
s = s.replace(old, new)
p.write_text(s)
print("bank switches now single-finger")
