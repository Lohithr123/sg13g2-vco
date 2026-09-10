import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

# ---------------------------------------------------------------- the helper
helper = '''
# Bus positions for each multi-finger device, filled in by bus_fingers() and
# read by every terminal connection afterwards.
BUS = {}


def bus_fingers(inst, tag=""):
    """Common a multi-finger MOSFET and record where its buses are.

    The nmos PCell draws each finger separately and does not connect them: a
    w=139u ng=20 device is twenty diffusion strips and twenty poly gates, and
    joining them is the layout's job. Without it the device extracts as twenty
    transistors in series with twenty floating gates — which DRC passes, and a
    connectivity check that probes one terminal per device passes too.

    The strips alternate source, drain, source... in x, so alternate ones bus
    together. The gap between the strip ends and the guard ring is 0.88 um,
    which holds a 0.3 um bus with the required 0.21 um clearance either side
    and nothing else. So the bus goes there and every terminal connection
    afterwards lands on the BUS, not on a strip — otherwise the two compete
    for the same 0.88 um.
    """
    cell = layout.cell(inst.cell_index)

    strips = []
    for sh in cell.shapes(LI["M1"]).each():
        b = sh.dbbox()
        if b.width() < 0.25 and b.height() > 2.0:
            strips.append(b.transformed(inst.dcplx_trans))
    strips.sort(key=lambda b: b.center().x)

    gates = [sh.dbbox().transformed(inst.dcplx_trans)
             for sh in cell.shapes(LI["poly"]).each()]
    gates.sort(key=lambda b: b.center().x)

    if len(strips) < 3:
        return None

    src, drn = strips[0::2], strips[1::2]
    stop_, sbot_ = strips[0].top, strips[0].bottom
    y_d = snap(stop_ + 0.42)
    y_s = snap(sbot_ - 0.42)

    for b in drn:
        wire("M1", b.center().x, stop_, b.center().x, y_d, b.width())
    wire("M1", drn[0].center().x - 0.2, y_d, drn[-1].center().x + 0.2, y_d, 0.3)

    for b in src:
        wire("M1", b.center().x, sbot_, b.center().x, y_s, b.width())
    wire("M1", src[0].center().x - 0.2, y_s, src[-1].center().x + 0.2, y_s, 0.3)

    # Gates contact on the poly, bussed on Metal2 over the array.
    y_g = snap(sbot_ + 0.5 * strips[0].height())
    for b in gates:
        drop(b.center().x, y_g, "M2", cols=1, rows=1, frm="GatPoly")
    wire("M2", gates[0].center().x, y_g, gates[-1].center().x, y_g, 0.3)

    BUS[tag] = {
        "s": (0.5 * (src[0].center().x + src[-1].center().x), y_s),
        "d": (0.5 * (drn[0].center().x + drn[-1].center().x), y_d),
        "g": (0.5 * (gates[0].center().x + gates[-1].center().x), y_g),
        "sx": (src[0].center().x, src[-1].center().x),
        "dx": (drn[0].center().x, drn[-1].center().x),
    }
    print(f"  {tag:8} {len(src)}s + {len(drn)}d strips, {len(gates)} gates; "
          f"src y {y_s:.2f}, drn y {y_d:.2f}")
    return BUS[tag]


print("\\n=== commoning multi-finger devices ===")
_COMB = [("XSW0", find("nmos", x=-8.0, y=-108.0)),
         ("XSW1", find("nmos", x=-8.0, y=-130.0)),
         ("XMR2", XMR2), ("XMR1", XMR1),
         ("XMT2", XMT2), ("XMT1", XMT1),
         ("XMB2A", MB2A), ("XMB1A", MB1A),
         ("XMB2B", MB2B), ("XMB1B", MB1B)]
for _t, _d in _COMB:
    if _d:
        bus_fingers(_d, tag=_t)


def busbox(tag, term):
    """A small box on a device's bus, for routing to instead of a pin."""
    x, y = BUS[tag][term]
    return pya.DBox(x - 0.15, y - 0.15, x + 0.15, y + 0.15)

'''

# Insert the helper right after the device lookup block, before any routing.
anchor = 'c1, b1, e1 = label(XQ1, "C"), label(XQ1, "B"), label(XQ1, "E")'
s = s.replace(anchor, helper + anchor)

p.write_text(s)
print("bus_fingers rewritten; buses now drawn before any terminal routing")
