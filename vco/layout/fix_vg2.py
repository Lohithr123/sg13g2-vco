import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# vg is a link between RB1 and RB2 rather than a driven node: the rail joins
# their far ends and goes nowhere, so LVS extracts one 14.54u resistor between
# the gates instead of two 7.27u ones to a bias point. Bring it out.
old = '''                (r2_top.center().x, r2_top.center().y)])'''
new = '''                (r2_top.center().x, r2_top.center().y)])
    # Out to a bias input on the left, so vg is a node rather than a link.
    path("M2", [(r1_top.center().x, -150.0), (-120.0, -150.0)], w=1.0)'''
assert s.count(old) == 1, f"matched {s.count(old)} times"
s = s.replace(old, new)
p.write_text(s)
print("vg rail brought out to x -120")
