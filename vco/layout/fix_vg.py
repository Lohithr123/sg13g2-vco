import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# LVS found ONE resistor between G1 and G2 at l=14.54u — RB1 and RB2 in series.
# The vg rail joins their far ends to each other and goes nowhere else, so the
# midpoint floats and vg is never driven. The gates then sit wherever the
# coupling capacitors leave them, which is the fault that gave 2.3% tuning
# before the DC blocking was added.
#
# Bring the rail out to a bias input, the way vt and the band-select lines come
# out. Then the midpoint is a real node and the two resistors are distinct.
old = '''    path("M2", [(r1_top.center().x, r1_top.center().y),
                (r1_top.center().x, -150.0),
                (r2_top.center().x, -150.0),
                (r2_top.center().x, r2_top.center().y)])
    print(f"  vg rail at y -150")'''
new = '''    path("M2", [(r1_top.center().x, r1_top.center().y),
                (r1_top.center().x, -150.0),
                (r2_top.center().x, -150.0),
                (r2_top.center().x, r2_top.center().y)])
    # Out to a bias input on the left edge, so vg is a driven node rather than
    # a link between the two resistors.
    path("M2", [(r1_top.center().x, -150.0), (-120.0, -150.0)], w=1.0)
    print(f"  vg rail at y -150, brought out to x -120")'''
assert old in s
s = s.replace(old, new)
p.write_text(s)
print("vg rail brought out")
