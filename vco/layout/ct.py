import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

block = '''
print("\\n=== CT to the tank ===")
# CT extracted floating: neither plate touched the tank. It is 31.6 fF of the
# tank capacitance, so floating it shifts the oscillation frequency.
#
# MEASURED:
#   CT top plate TopMetal1  x 18.11..21.89  y -96.89..-93.11
#   CT bottom plate Metal5  x 17.13..22.86  y -97.86..-92.14
#   outn on Metal4 spans x 5..30 with its top edge at y -98.59
#   outp on Metal3 at XQ2's base, x 9.2..10.2, y -104..-101.24
#   and outn's collector stack crosses Metal3 at x 9.40..10.00, y -99.2..-99.0
#
# Same plate discipline as the rest of the tank: outn takes the bottom plate,
# outp the top.
CT = find("cmim", x=20.0, y=-95.0)
if CT:
    # outn: a short Metal4 stub up from its column into the bottom plate,
    # then Metal4 -> Metal5. The via lands on the bottom plate only.
    path("M4", [(20.0, -98.8), (20.0, -97.4)], w=0.6)
    drop(20.0, -97.4, "M5", cols=2, rows=2, frm="Metal4")

    # outp: TopMetal1 extended left out of the plate, dropped at x 12 — outside
    # the bottom plate, so the stack cannot bridge the two plates. Reach it on
    # Metal3 by stepping right from XQ2's base region first, clear of outn's
    # collector stack at x 9.4..10.0.
    wire("TM1", 20.0, -95.0, 12.0, -95.0, 1.64)
    drop(12.0, -95.0, "TM1", cols=2, rows=2, frm="Metal3")
    path("M3", [(10.0, -102.5), (12.0, -102.5), (12.0, -95.0)], w=0.4)
    print("  CT bottom plate -> outn (M4), top plate -> outp (M3 via x 12)")

'''

anchor = 'layout.write(OUT)'
assert s.count(anchor) == 1
s = s.replace(anchor, block + anchor)
p.write_text(s)
print("CT connections added")
