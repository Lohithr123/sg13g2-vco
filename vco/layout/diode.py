import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

block = '''
print("\\n=== reference branch diode connections ===")
# The netlist has MMR2 = NC NC NB and MMR1 = NB NB GND: each reference device
# has its gate tied to its own drain. That connection sets the bias voltage the
# gate buses distribute, and it was never routed — so the buses carried a net
# with nothing driving it.
#
# MEASURED on both devices: three strips, sources outside at +/-1.38 um, drain
# in the middle, strips spanning y -192.5..-187.5. The gate contact sits on the
# poly bar above the strips. Link them on Metal2: a via on the drain strip just
# inside its top end, then up to the contact height and across to the gate.
for _tag, _dev in (("XMR2", XMR2), ("XMR1", XMR1)):
    if not _dev:
        continue
    _c = layout.cell(_dev.cell_index)
    _strips = sorted(
        (sh.dbbox().transformed(_dev.dcplx_trans)
         for sh in _c.shapes(LI["M1"]).each()
         if sh.dbbox().width() < 0.25 and sh.dbbox().height() > 2),
        key=lambda q: q.center().x)
    _polys = sorted(
        (sh.dbbox().transformed(_dev.dcplx_trans)
         for sh in _c.shapes(LI["poly"]).each()),
        key=lambda q: q.center().x)
    if len(_strips) < 3 or not _polys:
        print(f"  {_tag}: geometry not as expected, skipped")
        continue
    _drn = _strips[1]
    _dx = snap(_drn.center().x)
    _dy = snap(_drn.top - 0.5)
    _gx = snap(_polys[0].center().x)
    _gy = snap(_dev.dbbox().top - 1.21 + 0.41)
    for _l in ("M1", "M2"):
        top.shapes(LI[_l]).insert(
            pya.DBox(_dx - 0.15, _dy - 0.15, _dx + 0.15, _dy + 0.15))
    top.shapes(layout.layer(19, 0)).insert(
        pya.DBox(_dx - 0.095, _dy - 0.095, _dx + 0.095, _dy + 0.095))
    wire("M2", _dx, _dy, _dx, _gy, 0.26)
    wire("M2", _dx, _gy, _gx, _gy, 0.26)
    print(f"  {_tag}: drain ({_dx:.2f},{_dy:.2f}) tied to gate ({_gx:.2f},{_gy:.2f})")

'''

anchor = 'layout.write(OUT)'
assert s.count(anchor) == 1
s = s.replace(anchor, block + anchor)
p.write_text(s)
print("diode connections added")
