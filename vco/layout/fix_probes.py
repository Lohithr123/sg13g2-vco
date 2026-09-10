import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The buffer emitter nets were reported as failing, but extraction says the
# emitter and its mirror drain are both on net $8 — connected. The probe
# coordinates were stale: the drain moved from x -143.8 to -142.4 when the
# commoning changed which strip carries the connection.
s = s.replace('"MB2A_D": (-143.8, -200.0, "M5"), "MB2B_D": (143.8, -200.0, "M5"),',
              '"MB2A_D": (-142.4, -200.0, "M5"), "MB2B_D": (142.4, -200.0, "M5"),')
p.write_text(s)
print("probes moved to the real drain positions")
