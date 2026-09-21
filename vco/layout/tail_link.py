import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

block = '''
print("\\n=== tail cascode link (NTX) ===")
# Netlist: MMT2 = E NC NTX and MMT1 = NTX NB GND — XMT2's source must be XMT1's
# drain. Extraction showed them on separate nets: the cascode was never stacked.
#
# MEASURED:
#   XMT2 (not mirrored): the tail lands on its odd strips, so its EVEN strips,
#     bussed below at strips.bottom - 0.45, are NTX.
#   XMT1 (mirrored): ground lands on its even strips, so its ODD strips,
#     bussed above at strips.top + 0.30, are NTX.
#   Metal3 is empty across the whole gap between them; Metal2 carries the lower
#     gate bus at y -184 and Metal5 carries the tail.
#
# Route on Metal3: up from XMT2's source bus at its rightmost strip, across
# below both devices, and up into XMT1's drain bus at its SECOND drain strip —
# the first sits within 0.2 um of XMT1's gate contact.
if XMT2 and XMT1:
    def _st(d):
        return sorted(
            (sh.dbbox().transformed(d.dcplx_trans)
             for sh in layout.cell(d.cell_index).shapes(LI["M1"]).each()
             if sh.dbbox().width() < 0.25 and sh.dbbox().height() > 2),
            key=lambda q: q.center().x)
    _t2 = _st(XMT2)
    _t1 = _st(XMT1)
    _xa = snap(_t2[0::2][-1].center().x)      # XMT2 rightmost even strip
    _ya = snap(_t2[0].bottom - 0.45)          # XMT2 source bus
    _xb = snap(_t1[1::2][1].center().x)       # XMT1 second odd strip
    _yb = snap(_t1[0].top + 0.30)             # XMT1 drain bus
    drop(_xa, _ya, "M3", cols=2, rows=2, frm="Metal2")
    drop(_xb, _yb, "M3", cols=2, rows=2, frm="Metal2")
    path("M3", [(_xa, _ya), (_xb, _ya), (_xb, _yb)], w=0.3)
    print(f"  XMT2 source ({_xa:.2f},{_ya:.2f}) -> XMT1 drain ({_xb:.2f},{_yb:.2f}) on Metal3")

'''

anchor = 'layout.write(OUT)'
assert s.count(anchor) == 1
s = s.replace(anchor, block + anchor)
p.write_text(s)
print("tail cascode link added")
