import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

block = r'''
print("\n=== bleeds, bit 1 ===")
# The single-layer route was refused for bit 1: its upper pins are at
# y -272.86 and a vertical to the node at -130 crosses the gate buses and the
# buffer mirror region. MEASURED: TopMetal2 is clear below y -163 on both
# sides (the Vcc rail is at -160). So rise on TopMetal2 to y -170, drop to a
# lower layer there, and finish as before.
#
# The drop at the transition crosses every layer between, so its footprint is
# checked on each of them, not just the path segments.
_ORDER = ["M2", "M3", "M4", "M5", "TM1", "TM2"]

def _via_clear(x, y, lo, hi):
    a, b = _ORDER.index(lo), _ORDER.index(hi)
    for L in _ORDER[a:b + 1]:
        reg = _occupied(L)
        box = pya.DBox(x - 0.6, y - 0.6, x + 0.6, y + 0.6)
        if not (reg & pya.Region(box.to_itype(layout.dbu))).is_empty():
            return L
    return None

def _bleed_hi(tag, rinst, tap_x, tap_y, tap_layer, ymid=-170.0):
    if not rinst:
        return
    hi = sorted(pins(rinst, 8, 2), key=lambda q: q.center().y)[-1]
    hy = snap(hi.center().y)
    for dx in (0.0, 2.0, -2.0, 4.0, -4.0):
        bx = snap(hi.center().x + dx)
        if not _seg_clear("TM2", bx, hy, bx, ymid, 1.64, [(bx, hy)]):
            continue
        for lyr in ("M4", "M3", "M2"):
            blk = _via_clear(bx, ymid, lyr, "TM2")
            if blk:
                continue
            if not _seg_clear(lyr, bx, ymid, bx, tap_y, 0.4, [(bx, ymid)]):
                continue
            if not _seg_clear(lyr, bx, tap_y, tap_x, tap_y, 0.4, [(tap_x, tap_y)]):
                continue
            # pin up to TopMetal2 (offset horizontally on M2 if dx != 0)
            drop(hi.center().x, hy, "M2", cols=2, rows=2)
            if dx:
                path("M2", [(hi.center().x, hy), (bx, hy)], w=0.4)
            drop(bx, hy, "TM2", cols=2, rows=2, frm="Metal2")
            path("TM2", [(bx, hy), (bx, ymid)], w=1.64)
            drop(bx, ymid, "TM2", cols=2, rows=2, frm=_STK[lyr])
            path(lyr, [(bx, ymid), (bx, tap_y), (tap_x, tap_y)], w=0.4)
            drop(tap_x, tap_y, tap_layer, cols=2, rows=2, frm=_STK[lyr])
            print(f"  {tag}: TM2 to y {ymid}, then {lyr} to node at y {tap_y} (x offset {dx})")
            return
    print(f"  {tag}: NO CLEAR ROUTE - not drawn")

_bleed_hi("RBL1A", RBL["RBL1A"], -25.0, -131.6, "M5")
_bleed_hi("RBL1B", RBL["RBL1B"],  31.0, -130.0, "M5")

'''

anchor = 'layout.write(OUT)'
assert s.count(anchor) == 1
s = s.replace(anchor, block + anchor)
p.write_text(s)
print("bit-1 bleed routing added")
