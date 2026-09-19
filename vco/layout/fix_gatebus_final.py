import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

# ---- 1. make the commoning poly bar tall enough to hold a contact ----
old_bar = '''        gy0 = strips[0].top + 0.075     # Gat.d: 0.07 um clear of Activ
        gy1 = gy0 + 0.16                # Gat.a: 0.13 um minimum poly width'''
new_bar = '''        # MEASURED: the gate poly overhangs the diffusion by only 0.18 um, and
        # a contact needs 0.16 um plus ~0.07 um poly enclosure either side =
        # 0.30 um. It cannot sit on the overhang, which is why every attempt to
        # contact the gate there either connected nothing or broke Cnt.g2.
        #
        # But there is 0.88 um between the strip ends and the guard ring, and
        # Gat.d needs only 0.07 um of that. A 0.675 um tall bar fits with room
        # to spare, and a contact fits in the bar.
        gy0 = strips[0].top + 0.075     # Gat.d: 0.07 um clear of Activ
        gy1 = strips[0].top + 0.750     # tall enough for a contact
        POLYBAR[tag] = (gy0, gy1)'''
assert s.count(old_bar) == 1, "poly bar block not found"
s = s.replace(old_bar, new_bar)

# ---- 2. record the bar so the gate bus can find it ----
s = s.replace('BUS = {}', 'BUS = {}\nPOLYBAR = {}', 1) if 'BUS = {}' in s \
    else s.replace('def bus_fingers(', 'POLYBAR = {}\n\n\ndef bus_fingers(', 1)

# ---- 3. gate bus: explicit contact stack onto the bar ----
old_stub = '''            _gy = g.dbbox().bottom - 0.4
            wire(blyr, b.center().x, _gy, b.center().x, ybus, 0.21)'''
new_stub = '''            # Contact the commoning poly bar, drawn explicitly so every
            # layer is the right size: Cont 0.16, Metal1 0.30 (enclosure),
            # Via1 0.19 exactly, Metal2 0.30.
            _bar = POLYBAR.get(tag2(g))
            if _bar is None:
                continue
            _gy = snap(0.5 * (_bar[0] + _bar[1]))
            _x = snap(b.center().x)
            top.shapes(layout.layer(6, 0)).insert(
                pya.DBox(_x - 0.08, _gy - 0.08, _x + 0.08, _gy + 0.08))
            for _l in ("M1", "M2"):
                top.shapes(LI[_l]).insert(
                    pya.DBox(_x - 0.15, _gy - 0.15, _x + 0.15, _gy + 0.15))
            top.shapes(layout.layer(19, 0)).insert(
                pya.DBox(_x - 0.095, _gy - 0.095, _x + 0.095, _gy + 0.095))
            wire(blyr, _x, _gy, _x, ybus, 0.26)'''
assert s.count(old_stub) == 1, "gate stub not found"
s = s.replace(old_stub, new_stub)

# ---- 4. a way to map an instance back to its tag ----
s = s.replace('print("\\n=== mirror gate buses ===")',
'''def tag2(inst):
    """Map a device instance back to the tag bus_fingers recorded it under."""
    b = inst.dbbox()
    for _t, _d in _COMB:
        if _d and _d.dbbox() == b:
            return _t
    return None


print("\\n=== mirror gate buses ===")''')

p.write_text(s)
print("poly bar widened; gate stubs contact it explicitly")
