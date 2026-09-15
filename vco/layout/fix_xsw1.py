import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

old = '''    strips = []
    for sh in cell.shapes(LI["M1"]).each():
        b = sh.dbbox()
        if b.width() < 0.25 and b.height() > 2.0:
            strips.append(b.transformed(inst.dcplx_trans))
    strips.sort(key=lambda b: b.center().x)
    if len(strips) < 3:
        return None'''

new = '''    strips = []
    for sh in cell.shapes(LI["M1"]).each():
        b = sh.dbbox()
        if b.width() < 0.25 and b.height() > 2.0:
            strips.append(b.transformed(inst.dcplx_trans))
    strips.sort(key=lambda b: b.center().x)
    if len(strips) < 3:
        return None

    # MEASURED on XSW1: the device has strips the geometry filter finds, but
    # only TWO diffusion pins — at x -9.100..-8.940 and -8.590..-8.430. The
    # strips the filter returns do not all correspond to pins, so src/drn taken
    # by index put a "source" stub at -8.51, which is where the DRAIN pin's
    # Metal2 sits (-8.615..-8.405). The stub landed on the drain and shorted
    # the device.
    #
    # Use the PCell's own pin shapes to decide which strips are source and
    # which are drain, rather than inferring it from position. Where a strip
    # does not align with a pin it is not a terminal and must not be bussed.
    _pins = sorted((sh.dbbox().transformed(inst.dcplx_trans)
                    for sh in cell.shapes(layout.layer(8, 2)).each()),
                   key=lambda b: b.center().x)
    if len(_pins) >= 2:
        _keep = []
        for b in strips:
            # A strip is a terminal only if it overlaps one of the pins in x.
            if any(abs(b.center().x - q.center().x) < 0.15 for q in _pins):
                _keep.append(b)
        # Every other strip belongs to the same terminal as the nearest pin,
        # which the PCell wires internally, so bussing them is unnecessary.
        if len(_keep) >= 2:
            strips = _keep'''

assert s.count(old) == 1, f"matched {s.count(old)}"
s = s.replace(old, new)
p.write_text(s)
print("strips now identified from the PCell's own pin shapes")
