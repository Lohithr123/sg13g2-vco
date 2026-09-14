import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The guard ring's bottom bar reaches y -203.00 while the strips end at -203.47
# on the 139 um devices — it overlaps the strip region rather than sitting
# 0.88 um clear as it does on the 70 um device. The source bar at -204.18 is
# therefore inside the ring, tying every source to ground.
#
# Measure the ring instead of assuming a fixed gap, and put both bars where
# there is real clearance.
old = '''    ybar_s = snap(strips[0].bottom - 0.55)  # bars run outside the array
    ybar_d = snap(strips[0].top + 0.55)'''
new = '''    # Find the guard ring bars (wide Metal1) and place outside them.
    _wide = [sh.dbbox().transformed(inst.dcplx_trans)
             for sh in cell.shapes(LI["M1"]).each()
             if sh.dbbox().width() > 5.0]
    _below = [b.top for b in _wide if b.top < strips[0].bottom + 0.6]
    _above = [b.bottom for b in _wide if b.bottom > strips[0].top - 0.6]
    ybar_s = snap((max(_below) if _below else strips[0].bottom) - 0.75)
    ybar_d = snap((min(_above) if _above else strips[0].top) + 0.75)'''
assert s.count(old) == 1
s = s.replace(old, new)
p.write_text(s)
print("bars placed relative to the measured guard ring")
