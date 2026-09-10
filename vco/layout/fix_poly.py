import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# A stack starting on poly needs GatPoly in both maps: STACK_NAME to name the
# PCell layer, and the start lookup to know where its landing pads begin. Poly
# sits below Metal1, so the pads start at Metal1 and go up.
if '"GatPoly": "GatPoly"' not in s:
    s = s.replace('STACK_NAME = {"M2": "Metal2",',
                  'STACK_NAME = {"GatPoly": "GatPoly", "M2": "Metal2",')
s = s.replace('''    start = order.index({"Metal1": "M1", "Metal2": "M2", "Metal3": "M3",
                         "Metal4": "M4", "Metal5": "M5"}[frm])''',
'''    start = order.index({"Metal1": "M1", "GatPoly": "M1", "Metal2": "M2",
                         "Metal3": "M3", "Metal4": "M4",
                         "Metal5": "M5"}[frm])''')
p.write_text(s)
print("GatPoly added to both maps")
