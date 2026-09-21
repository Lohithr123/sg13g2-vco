import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
done = []

def rep(old, new, tag, count=1):
    global s
    n = s.count(old)
    if n != count:
        print(f"  !! {tag}: expected {count}, found {n} - skipped")
        return
    s = s.replace(old, new)
    done.append(tag)

# TM2.a: TopMetal2 minimum width is 1.8 um, not TopMetal1's 1.64.
rep('_seg_clear("TM2", bx, hy, bx, ymid, 1.64, [(bx, hy)])',
    '_seg_clear("TM2", bx, hy, bx, ymid, 2.0, [(bx, hy)])', "TM2 check width")
rep('path("TM2", [(bx, hy), (bx, ymid)], w=1.64)',
    'path("TM2", [(bx, hy), (bx, ymid)], w=2.0)', "TM2 route width")

# TM1.b: step bit-1 inward by 4 um, clear of the bit-0 ground run at x +/-150.
rep('    for dx in (0.0, 2.0, -2.0, 4.0, -4.0):',
    '    _in = -1.0 if hi.center().x > 0 else 1.0\n'
    '    for dx in (4.0 * _in, 6.0 * _in):', "bleed inward offset")

# M5.b/e: end the bank routes inside the stack (reaches +/-1.58) rather than at
# its centre, so the A and B ends no longer meet in y; and narrow them to 0.3
# so each clears the neighbouring pin's 0.21 stack.
rep('(px, pin.center().y)], w=0.4)',
    '(px, pin.center().y - 1.4)], w=0.3)', "bank B end")
rep('(px, pin.center().y)],\n                 w=0.4)',
    '(px, pin.center().y + 1.4)],\n                 w=0.3)', "bank A end")

# M2.b on mirrored devices: contact the gate on the far side from the drain
# bar's offset, and jog out on that side. Mirrors the unmirrored geometry.
rep('            _x = snap(_polys[0].center().x)',
    '            _mirg = g.dcplx_trans.is_mirror()\n'
    '            _x = snap((_polys[-1] if _mirg else _polys[0]).center().x)',
    "mirrored gate contact")
rep('            _xj = snap(g.dbbox().left + 0.6)',
    '            _xj = snap(g.dbbox().right - 0.6) if _mirg \\\n'
    '                else snap(g.dbbox().left + 0.6)', "mirrored jog side")
rep('        xs = sorted(snap(g.dbbox().left + 0.6) for g, _ in gs)',
    '        xs = sorted(snap(g.dbbox().right - 0.6) if g.dcplx_trans.is_mirror()\n'
    '                    else snap(g.dbbox().left + 0.6) for g, _ in gs)',
    "spine follows jog side")

# M2.a: fill the outside corner of each gate jog.
rep('            wire(blyr, _xj, _gy, _xj, ybus, 0.26)',
    '            wire(blyr, _xj, _gy, _xj, ybus, 0.26)\n'
    '            top.shapes(LI[blyr]).insert(\n'
    '                pya.DBox(_xj - 0.13, _gy - 0.13, _xj + 0.13, _gy + 0.13))',
    "gate jog corner")

# M2.a + M2.b at the diode links: fill the corner, and carry the vertical up
# into the drain's own stack so the same-net slot closes.
rep('    wire("M2", _dx, _dy, _dx, _gy, 0.26)\n    wire("M2", _dx, _gy, _gx, _gy, 0.26)',
    '    wire("M2", _dx, _dy, _dx, _gy + 0.8, 0.26)\n'
    '    wire("M2", _dx, _gy, _gx, _gy, 0.26)\n'
    '    top.shapes(LI["M2"]).insert(\n'
    '        pya.DBox(_dx - 0.13, _gy - 0.13, _dx + 0.13, _gy + 0.13))',
    "diode link corner")

# M3.b: run the XMR link at the landing via's height, not beside it.
rep('    path("M3", [(_xa, _ya), (_xa, _yr), (_xb, _yr), (_xb, _yb)], w=0.3)',
    '    path("M3", [(_xa, _ya), (_xa, _yb), (_xb, _yb)], w=0.3)', "XMR link height")

p.write_text(s)
print(f"applied {len(done)}: " + ", ".join(done))
