import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

block = r'''
print("\n=== bleed resistors ===")
# Netlist: RBL0A S0A GND, RBL0B S0B GND, RBL1A S1A GND, RBL1B S1B GND. All four
# extracted floating — they were placed at the die edge and never routed.
#
# MEASURED: bleeds at (+/-150, -225) with pins at y -262.14 / -187.86, and at
# (+/-150, -310) with pins at y -347.14 / -272.86. Ground on TopMetal1 spans the
# width with its rail at y -300.
#
# Each upper pin goes to its switch node: a vertical at the bleed's column,
# then a horizontal at the node's height to the capacitor plate that carries
# it. Each lower pin goes straight to the ground rail on TopMetal1.
#
# Every segment is checked against the metal already drawn, on its layer,
# before it is placed. Endpoints are excluded from the check, since they are
# meant to touch. A segment that would touch anything else is refused and
# reported rather than drawn.
_LN = {"M2": (10, 0), "M3": (30, 0), "M4": (50, 0), "M5": (67, 0),
       "TM1": (126, 0), "TM2": (134, 0)}
_STK = {"M2": "Metal2", "M3": "Metal3", "M4": "Metal4", "M5": "Metal5"}

def _occupied(lyr):
    return pya.Region(top.begin_shapes_rec(layout.layer(*_LN[lyr]))).merged()

def _seg_clear(lyr, x0, y0, x1, y1, w, keep):
    reg = _occupied(lyr)
    h = w / 2 + 0.25                      # track half-width plus clearance
    box = pya.DBox(min(x0, x1) - h, min(y0, y1) - h,
                   max(x0, x1) + h, max(y0, y1) + h)
    hit = reg & pya.Region(box.to_itype(layout.dbu))
    for kx, ky in keep:                   # endpoints are meant to touch
        hit -= pya.Region(pya.DBox(kx - 1.2, ky - 1.2,
                                   kx + 1.2, ky + 1.2).to_itype(layout.dbu))
    return hit.is_empty()

def _bleed(tag, rinst, tap_x, tap_y, tap_layer):
    if not rinst:
        print(f"  {tag}: resistor not found")
        return
    pp = sorted(pins(rinst, 8, 2), key=lambda q: q.center().y)
    lo, hi = pp[0], pp[-1]
    bx = snap(hi.center().x)
    hy = snap(hi.center().y)
    for lyr in ("M4", "M3", "M2"):
        ok_v = _seg_clear(lyr, bx, hy, bx, tap_y, 0.4, [(bx, hy)])
        ok_h = _seg_clear(lyr, bx, tap_y, tap_x, tap_y, 0.4, [(tap_x, tap_y)])
        if ok_v and ok_h:
            drop(bx, hy, lyr, cols=2, rows=2)
            path(lyr, [(bx, hy), (bx, tap_y), (tap_x, tap_y)], w=0.4)
            drop(tap_x, tap_y, tap_layer, cols=2, rows=2, frm=_STK[lyr])
            print(f"  {tag}: upper pin -> node on {lyr} at y {tap_y}")
            break
    else:
        print(f"  {tag}: NO CLEAR LAYER for the node route - not drawn")
    # lower pin to the ground rail on TopMetal1
    ly_ = snap(lo.center().y)
    drop(bx, ly_, "TM1", cols=2, rows=2)
    path("TM1", [(bx, ly_), (bx, -300.0)], w=1.64)
    print(f"  {tag}: lower pin -> ground rail on TM1")

RBL = {}
for _nm, _x, _y in (("RBL0A", -150.0, -225.0), ("RBL0B", 150.0, -225.0),
                    ("RBL1A", -150.0, -310.0), ("RBL1B", 150.0, -310.0)):
    RBL[_nm] = find("rhigh", x=_x, y=_y)

# Switch-node taps: A side on the bottom plate (Metal5) just inside its lower
# edge; B side on the TopMetal1 extension's Metal5 drop at tx = +31.
_bleed("RBL0A", RBL["RBL0A"], -25.0, -109.6, "M5")
_bleed("RBL0B", RBL["RBL0B"],  31.0, -108.0, "M5")
_bleed("RBL1A", RBL["RBL1A"], -25.0, -131.6, "M5")
_bleed("RBL1B", RBL["RBL1B"],  31.0, -130.0, "M5")

'''

anchor = 'layout.write(OUT)'
assert s.count(anchor) == 1
s = s.replace(anchor, block + anchor)
p.write_text(s)
print("bleed routing added")
