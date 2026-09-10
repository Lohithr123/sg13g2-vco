import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The commoning block now runs before the mirror devices are found. Look them
# all up in one place, before anything uses them.
old = '''print("\\n=== commoning multi-finger devices ===")
_COMB = ['''
new = '''XMT2 = find("nmos", x=-20.0, y=-190.0, wmin=10)
XMT1 = find("nmos", x=20.0, y=-190.0, wmin=10)
XMR2 = find("nmos", x=-55.0, y=-190.0)
XMR1 = find("nmos", x=-42.0, y=-190.0)
MB2A = find("nmos", x=-130.0, y=-200.0, wmin=20)
MB1A = find("nmos", x=-95.0, y=-200.0, wmin=20)
MB2B = find("nmos", x=130.0, y=-200.0, wmin=20)
MB1B = find("nmos", x=95.0, y=-200.0, wmin=20)

print("\\n=== commoning multi-finger devices ===")
_COMB = ['''
assert old in s
s = s.replace(old, new)
p.write_text(s)
print("device lookups moved before the commoning block")
