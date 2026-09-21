import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

block = '''
print("\\n=== RREF to NC ===")
# RREF extracted as "$37 vcc": its upper end reaches the supply, its lower end
# reaches nothing. Without it on NC the reference branch carries no current and
# no mirror in the design is biased.
#
# NC is XMR2's diode-connected node. The gate stub jogged to XMR2's left edge
# (instance.left + 0.6) carries NC vertically from the gate contact down to
# the cascode bus at y -212, so RREF can simply join it.
#
# RREF's lower pin is below XMR2's bbox (-193.71), and XMR2's source bus sits
# at y -192.95 spanning x -56.51..-53.49 — a Metal2 run at the pin's height
# meets the stub 0.79 um clear of it.
if RREF and XMR2:
    _rr = sorted(pins(RREF, 8, 2), key=lambda q: q.center().y)
    _lo = _rr[0]
    _sx = snap(XMR2.dbbox().left + 0.6)
    _ly = snap(_lo.center().y)
    drop(_lo.center().x, _ly, "M2", cols=2, rows=2)
    path("M2", [(_lo.center().x, _ly), (_sx, _ly)], w=0.3)
    print(f"  RREF lower pin ({_lo.center().x:.2f},{_ly:.2f}) -> NC stub at x {_sx:.2f}")

'''

anchor = 'layout.write(OUT)'
assert s.count(anchor) == 1
s = s.replace(anchor, block + anchor)
p.write_text(s)
print("RREF link added")
