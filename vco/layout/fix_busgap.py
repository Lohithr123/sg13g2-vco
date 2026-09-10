import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The guard ring's horizontal bars sit at y -1.18..-0.88 and 7.88..8.18 in cell
# coordinates, i.e. 0.88 um beyond the strips. Extending 1.6 um past the array
# runs straight into them, tying every source to its own guard ring — and the
# guard rings are ground, so the cascode sources shorted to ground.
#
# The gap between strip end and guard ring is only 0.88 um, and Metal1 needs
# 0.21 um spacing, so the bus has to sit within about 0.6 um of the strips.
old = '''    y_dbus = stop_ + 1.6           # clear of the guard ring bar above
    y_sbus = sbot_ - 1.6           # and below'''
new = '''    y_dbus = stop_ + 0.45          # inside the 0.88 um gap to the guard ring
    y_sbus = sbot_ - 0.45'''
assert old in s
s = s.replace(old, new)
p.write_text(s)
print("buses moved inside the guard ring gap")
