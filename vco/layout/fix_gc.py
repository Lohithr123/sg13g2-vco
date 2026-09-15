import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# gy is g.top + 0.10 — on the poly bus above the diffusion, which is clear.
# But the contact is placed at gy - 0.45, i.e. g.top - 0.35, back inside the
# active area beside the source strip at x -8.59..-8.43. That is both the
# M1.b spacing (70 nm) and the V1.b via spacing (65 nm).
#
# The commoning busses these gates on poly, so the contact belongs on that bus.
old = '''    drop(g.center().x, gy - 0.45, "M2", cols=1, rows=2)
    path("M2", [(g.center().x, gy - 0.45),'''
new = '''    drop(g.center().x, gy, "M2", cols=1, rows=1, frm="GatPoly")
    path("M2", [(g.center().x, gy),'''
assert s.count(old) == 1
s = s.replace(old, new)
p.write_text(s)
print("band-select contact moved onto the poly bus")
