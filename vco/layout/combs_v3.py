import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

helper = '''
def bus_fingers(inst, tag=""):
    """Common a multi-finger MOSFET's fingers, inside the device.

    ROOT CAUSE OF THE EARLIER FAILURES
    ----------------------------------
    The nmos PCell draws each finger separately and does not connect them, so
    a w=139u ng=20 device extracts as twenty transistors in series with twenty
    floating gates. DRC passes it; a connectivity check that probes one
    terminal per device passes it too.

    Every previous attempt at a fix put the buses BEYOND the strip ends, in
    the 0.88 um gap between the diffusion and the guard ring. That gap is
    already occupied by the terminal routing, so the two competed for the same
    space and each attempt traded one broken net for another.

    But the strips are 7 um tall and almost entirely unused. The room is
    inside the device, not beyond it.

    The reason the first attempt at that failed — 192 DRC violations — was not
    the location but the via: a via stack is 0.29 um at its narrowest and a
    diffusion strip is 0.16 um wide, so every via overhung onto the poly and
    the neighbouring contacts.

    So: widen each strip locally with a small Metal1 pad, put the via on the
    pad, and bus on Metal2 over the array. Strip pitch is 1.38 um and adjacent
    strips carry opposite nets whose pads sit at different heights, so the
    clearance is comfortable. The 0.88 um gap is never touched, and the
    existing terminal routing keeps working untouched: it lands on one strip,
    and that strip is now bussed to the rest.
    """
    cell = layout.cell(inst.cell_index)

    strips = []
    for sh in cell.shapes(LI["M1"]).each():
        b = sh.dbbox()
        if b.width() < 0.25 and b.height() > 2.0:
            strips.append(b.transformed(inst.dcplx_trans))
    strips.sort(key=lambda b: b.center().x)
    if len(strips) < 3:
        return None

    gates = sorted(
        (sh.dbbox().transformed(inst.dcplx_trans)
         for sh in cell.shapes(LI["poly"]).each()),
        key=lambda b: b.center().x)

    src, drn = strips[0::2], strips[1::2]
    y0, h = strips[0].bottom, strips[0].height()

    # Three levels inside the strip span, evenly spread.
    y_s = snap(y0 + 0.20 * h)
    y_d = snap(y0 + 0.50 * h)
    y_g = snap(y0 + 0.80 * h)

    PAD = 0.30          # half-width of the local Metal1 widening

    for group, ylev in ((src, y_s), (drn, y_d)):
        for b in group:
            x = b.center().x
            top.shapes(LI["M1"]).insert(pya.DBox(
                snap(x - PAD), snap(ylev - PAD),
                snap(x + PAD), snap(ylev + PAD)))
            drop(x, ylev, "M2", cols=1, rows=1)
        if len(group) > 1:
            wire("M2", group[0].center().x, ylev,
                 group[-1].center().x, ylev, 0.3)

    for b in gates:
        drop(b.center().x, y_g, "M2", cols=1, rows=1, frm="GatPoly")
    if len(gates) > 1:
        wire("M2", gates[0].center().x, y_g, gates[-1].center().x, y_g, 0.3)

    print(f"  {tag:8} {len(src)}s + {len(drn)}d strips, {len(gates)} gates "
          f"bussed at y {y_s:.1f} / {y_d:.1f} / {y_g:.1f}")
    return True


print("\\n=== commoning multi-finger devices ===")
for _t, _d in (("XSW0", find("nmos", x=-8.0, y=-108.0)),
               ("XSW1", find("nmos", x=-8.0, y=-130.0)),
               ("XMR2", XMR2), ("XMR1", XMR1),
               ("XMT2", XMT2), ("XMT1", XMT1),
               ("XMB2A", MB2A), ("XMB1A", MB1A),
               ("XMB2B", MB2B), ("XMB1B", MB1B)):
    if _d:
        bus_fingers(_d, tag=_t)

'''

s = s.replace('layout.write(OUT)', helper + 'layout.write(OUT)')

if '"GatPoly": "GatPoly"' not in s:
    s = s.replace('STACK_NAME = {"M2": "Metal2",',
                  'STACK_NAME = {"GatPoly": "GatPoly", "M2": "Metal2",')
s = s.replace('''    start = order.index({"Metal1": "M1", "Metal2": "M2", "Metal3": "M3",
                         "Metal4": "M4", "Metal5": "M5"}[frm])''',
'''    start = order.index({"Metal1": "M1", "GatPoly": "M1", "Metal2": "M2",
                         "Metal3": "M3", "Metal4": "M4",
                         "Metal5": "M5"}[frm])''')

p.write_text(s)
print("commoning rewritten: pads inside the device, gap left alone")
