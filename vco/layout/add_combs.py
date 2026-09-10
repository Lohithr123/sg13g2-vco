import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

helper = '''
def bus_fingers(inst, y_src=1.0, y_drn=3.5, y_gate=6.0, tag=""):
    """Common a multi-finger MOSFET's sources, drains and gates.

    The nmos PCell draws each finger separately and does NOT connect them:
    a w=139u ng=20 device extracts as twenty 6.95 um transistors in series
    with twenty floating gates. DRC passes it, and a connectivity check that
    only probes one terminal passes it too. LVS is what catches it.

    Diffusion strips alternate source, drain, source... in x, so the even
    ones bus together and the odd ones bus together. Each bus runs on Metal2
    at its own y, with vias only onto its own strips, so the three buses can
    cross over each other's fingers without touching.
    """
    cell = layout.cell(inst.cell_index)

    # Diffusion strips: narrow and tall. The guard ring pieces are either
    # much wider (the horizontal bars) or sit outside the active area.
    strips = []
    for sh in cell.shapes(LI["M1"]).each():
        b = sh.dbbox()
        if b.width() < 0.5 and b.height() > 2.0:
            strips.append(b.transformed(inst.dcplx_trans))
    strips.sort(key=lambda b: b.center().x)

    gates = [sh.dbbox().transformed(inst.dcplx_trans)
             for sh in cell.shapes(LI["poly"]).each()]
    gates.sort(key=lambda b: b.center().x)

    if len(strips) < 3:
        return 0, 0

    ybase = inst.dbbox().bottom
    ys, yd, yg = ybase + y_src, ybase + y_drn, ybase + y_gate

    src = strips[0::2]
    drn = strips[1::2]

    for group, ylev in ((src, ys), (drn, yd)):
        for b in group:
            drop(b.center().x, ylev, "M2", cols=1, rows=1)
        if len(group) > 1:
            wire("M2", group[0].center().x, ylev,
                 group[-1].center().x, ylev, 0.4)

    for b in gates:
        drop(b.center().x, yg, "M2", cols=1, rows=1, frm="GatPoly")
    if len(gates) > 1:
        wire("M2", gates[0].center().x, yg, gates[-1].center().x, yg, 0.4)

    print(f"  {tag:8} {len(src)} source + {len(drn)} drain strips, "
          f"{len(gates)} gates bussed")
    return len(strips), len(gates)


print("\\n=== commoning multi-finger devices ===")
for tag, dev in (("XSW0", find("nmos", x=-8.0, y=-108.0)),
                 ("XSW1", find("nmos", x=-8.0, y=-130.0)),
                 ("XMR2", XMR2), ("XMR1", XMR1),
                 ("XMT2", XMT2), ("XMT1", XMT1),
                 ("XMB2A", MB2A), ("XMB1A", MB1A),
                 ("XMB2B", MB2B), ("XMB1B", MB1B)):
    if dev:
        bus_fingers(dev, tag=tag)

'''

s = s.replace('layout.write(OUT)', helper + 'layout.write(OUT)')
s = s.replace('STACK_NAME = {"M2": "Metal2",',
              'STACK_NAME = {"GatPoly": "GatPoly", "M2": "Metal2",')
s = s.replace('    start = order.index({"Metal1": "M1", "Metal2": "M2", "Metal3": "M3",\n'
              '                         "Metal4": "M4", "Metal5": "M5"}[frm])',
              '    start = order.index({"Metal1": "M1", "GatPoly": "M1", "Metal2": "M2",\n'
              '                         "Metal3": "M3", "Metal4": "M4",\n'
              '                         "Metal5": "M5"}[frm])')

p.write_text(s)
print("finger commoning added")
