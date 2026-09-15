import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# Measured: XMB2A's source pin is at x -143.88..-143.72 and its drain at
# -142.50..-142.34 — 1.38 um apart. The buffer bias route lands on the drain
# 2.0 um wide, so it spans -143.42..-141.42 and covers both pins. Drain shorted
# to source, and nothing to do with the finger commoning: this predates it.
#
# 0.6 um lands on the 0.16 um pin with enclosure and stops 0.6 um short of the
# neighbouring pin.
old = '''                    (d2.center().x, d2.center().y)], w=2.0)'''
new = '''                    (d2.center().x, d2.center().y)], w=0.6)'''
assert s.count(old) == 1
s = s.replace(old, new)
p.write_text(s)
print("buffer bias route narrowed to 0.6 um")
