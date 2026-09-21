import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

block = '''
print("\\n=== XMR2 source to NB ===")
# The netlist has MMR2 = NC NC NB: XMR2's source is the NB node, which is
# XMR1's drain and gate. After the diode connections XMR2 extracts as
# "$44 $17 $17" — its source on a net of its own.
#
# A Metal2 link from XMR2's source bus to XMR1 would cross XMR1's own source
# strip at x -43.38, which is ground. MEASURED: Metal3 between the two devices
# holds only two via-stack pieces, at y -186.8..-186.1 near x -55 and at
# y -190.4..-189.6 near x -43.4. A Metal3 path up from XMR2's source bus at
# x -53.62, across at y -187.5, and down onto XMR1's diode link at x -42.00
# touches neither.
if XMR2 and XMR1:
    def _strips(d):
        return sorted(
            (sh.dbbox().transformed(d.dcplx_trans)
             for sh in layout.cell(d.cell_index).shapes(LI["M1"]).each()
             if sh.dbbox().width() < 0.25 and sh.dbbox().height() > 2),
            key=lambda q: q.center().x)
    _s2 = _strips(XMR2)
    _s1 = _strips(XMR1)
    _xa = snap(_s2[-1].center().x)            # XMR2 rightmost source strip
    _ya = snap(_s2[-1].bottom - 0.45)          # its source bus, below
    _xb = snap(_s1[1].center().x)              # XMR1 drain strip
    _yb = snap(_s1[1].top - 0.5)               # the diode link pad
    _yr = snap(_s1[1].top)                     # route height on Metal3
    drop(_xa, _ya, "M3", cols=2, rows=2, frm="Metal2")
    drop(_xb, _yb, "M3", cols=2, rows=2, frm="Metal2")
    path("M3", [(_xa, _ya), (_xa, _yr), (_xb, _yr), (_xb, _yb)], w=0.3)
    print(f"  XMR2 source ({_xa:.2f},{_ya:.2f}) -> XMR1 drain ({_xb:.2f},{_yb:.2f}) on Metal3")

'''

anchor = 'layout.write(OUT)'
assert s.count(anchor) == 1
s = s.replace(anchor, block + anchor)
p.write_text(s)
print("XMR2 source link added")
