import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

old = '''            _gy = snap(g.dbbox().top - 1.21 + 0.41)
            _x = snap(_polys[0].center().x)'''
new = '''            _gy = snap(g.dbbox().top - 1.21 + 0.41)
            _x = snap(_polys[0].center().x)
            # MEASURED: the commoning's SOURCE bus runs below each device,
            # spanning the source strips in x. The gate stub descending to the
            # gate bus at y -212 passed straight through it — every cascode
            # gate extracted shorted to its own source.
            #
            # Jog left, outside the source bus span, before descending. The
            # guard ring there is Metal1 and the stub is Metal2, so only the
            # source bus has to be cleared: 0.6 um in from the instance's left
            # edge is outside every strip and outside the bus.
            _xj = snap(g.dbbox().left + 0.6)
            JOG[id(g)] = _xj'''
assert s.count(old) == 1, f"contact block matched {s.count(old)}"
s = s.replace(old, new)

old2 = '''            wire(blyr, _x, _gy, _x, ybus, 0.26)'''
new2 = '''            wire(blyr, _x, _gy, _xj, _gy, 0.26)
            wire(blyr, _xj, _gy, _xj, ybus, 0.26)'''
assert s.count(old2) == 1, f"stub matched {s.count(old2)}"
s = s.replace(old2, new2)

# The bus spine must span the jogged stubs, not the gate pins.
old3 = '''        xs = sorted(b.center().x for _, b in gs)'''
new3 = '''        xs = sorted(JOG.get(id(g), b.center().x) for g, b in gs) \\
             if JOG else sorted(b.center().x for _, b in gs)'''
if old3 in s:
    s = s.replace(old3, new3)
    print("bus span updated")
else:
    print("NOTE: xs line not found in expected form")

if 'JOG = {}' not in s:
    s = s.replace('POLYBAR = {}', 'POLYBAR = {}\nJOG = {}', 1)

p.write_text(s)
print("gate stubs jog clear of the source bus before descending")
