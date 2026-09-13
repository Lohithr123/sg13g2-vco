import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The cascode gate stub runs Metal2 from each gate down to the bus at y -212,
# and the finger commoning now puts a drain bus on Metal2 at 50% of the strip
# height — directly in its path. At the buffer mirrors the stub crosses it,
# tying the cascode bias to the buffer output.
#
# The commoning already busses every gate on poly, so the stub only has to
# reach ONE gate, and it can leave from below the device where the drain bus
# is not. Start it at the device's bottom edge rather than at the gate centre.
old = '            wire(blyr, b.center().x, b.center().y, b.center().x, ybus, 0.21)'
new = ('            _gy = g.dbbox().bottom - 0.4\n'
       '            wire(blyr, b.center().x, _gy, b.center().x, ybus, 0.21)')
assert s.count(old) == 1
s = s.replace(old, new)
p.write_text(s)
print("gate stubs now leave from below the device")
