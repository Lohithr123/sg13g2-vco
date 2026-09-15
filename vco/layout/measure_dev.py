# Measure a device completely before placing anything on it.
#
# Every failure so far came from sizing a contact or a bus by arithmetic from
# one device and applying it to another. The bank switches use l=0.13u and the
# mirrors l=1u; their internals are not the same shape. So: read the geometry,
# do not assume it.
#
# In particular — does the PCell already provide a gate contact? If it does,
# the band-select line only has to land on it, and no new contact is needed at
# all. That is the thing I never checked.

import os
import sys
import pya

sys.path.insert(0, os.environ.get("PDK_ROOT", "/foss/pdks")
                + "/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib

lib = pya.Library.library_by_name("SG13_dev", "sg13g2")
L = lib.layout()

LAYERS = [(1, 0, "Activ"), (5, 0, "GatPoly"), (6, 0, "Cont"),
          (8, 0, "Metal1"), (10, 0, "Metal2"), (19, 0, "Via1"),
          (5, 2, "GatPoly.pin"), (8, 2, "Metal1.pin")]

CASES = [
    ("bank switch  w=8u l=0.13u ng=2",
     {"w": "8u", "l": "0.13u", "ng": "2", "m": "1", "guardRingType": "psub"}),
    ("tail mirror  w=70u l=1u ng=10",
     {"w": "70u", "l": "1u", "ng": "10", "m": "1", "guardRingType": "psub"}),
]

for title, params in CASES:
    ly = pya.Layout()
    ly.dbu = 0.001
    ci = ly.add_pcell_variant(lib, L.pcell_id("nmos"), params)
    cell = ly.cell(ci)
    print(f"\n{'=' * 64}\n{title}\n{'=' * 64}")
    for lay, dt, nm in LAYERS:
        shs = list(cell.shapes(ly.layer(lay, dt)).each())
        if not shs:
            continue
        boxes = [s.dbbox() for s in shs if not s.is_text()]
        if not boxes:
            continue
        print(f"\n  {nm} ({lay}/{dt}): {len(boxes)} shapes")
        # Group by identical size so the output stays readable.
        from collections import defaultdict
        groups = defaultdict(list)
        for b in boxes:
            groups[(round(b.width(), 3), round(b.height(), 3))].append(b)
        for (w, h), bs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            xs = sorted(b.center().x for b in bs)
            ys = sorted(b.center().y for b in bs)
            print(f"     {len(bs):3d} x  {w:6.3f} x {h:6.3f}   "
                  f"x {xs[0]:7.3f}..{xs[-1]:7.3f}  y {ys[0]:7.3f}..{ys[-1]:7.3f}")
