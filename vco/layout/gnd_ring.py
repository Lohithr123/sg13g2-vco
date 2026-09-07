import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

start = s.index('print("\\n=== ground connections ===")')
end = s.index('layout.write(OUT)')

new = '''print("\\n=== ground ring ===")
# Ground is not a net like the others. It touches ten scattered points — four
# mirror sources and six guard rings — and any route between them crosses
# whatever else occupies that space. Three attempts at point-to-point wiring
# each freed one net and caught another: first the tail, then the control
# lines, then the cascode bus.
#
# The fix is structural. Ground gets a ring around the die perimeter on
# TopMetal1, outside every device and every other route, and each point
# reaches it by the shortest radial stub. Nothing crosses the interior.
#
# The perimeter is genuinely empty: no device sits beyond x +/-146 or below
# y -215, and the only TopMetal1 in that region is this ring.

RX, RY0, RY1 = 165.0, -60.0, -320.0

# The ring itself: four sides, 5 um wide.
wire("TM1", -RX, RY0, RX, RY0, 5.0)          # top
wire("TM1", -RX, RY1, RX, RY1, 5.0)          # bottom
wire("TM1", -RX, RY0, -RX, RY1, 5.0)         # left
wire("TM1", RX, RY0, RX, RY1, 5.0)           # right
print(f"  ring x +/-{RX:.0f}, y {RY0:.0f} to {RY1:.0f}")

gnd_pts = []
for nm, dev in (("XMR1", XMR1), ("XMT1", XMT1),
                ("XMB1A", MB1A), ("XMB1B", MB1B)):
    if dev:
        src = pins(dev, 8, 2)[0]
        gnd_pts.append((nm, src.center().x, src.center().y))
for nm, dev in (("XSW0", find("nmos", x=-8.0, y=-108.0)),
                ("XSW1", find("nmos", x=-8.0, y=-130.0)),
                ("XMR2", XMR2), ("XMT2", XMT2),
                ("XMB2A", MB2A), ("XMB2B", MB2B)):
    if dev:
        b = dev.dbbox()
        gnd_pts.append((nm + "_ring", b.center().x, b.bottom + 0.15))

# Each point rises to TopMetal1 immediately, directly above itself, and runs
# straight out to the nearest ring side. A vertical drop then a horizontal run
# on TopMetal1 only — the layer nothing else uses out here.
for nm, gx, gy in gnd_pts:
    try:
        drop(gx, gy, "TM1", cols=1, rows=2)
    except Exception as exc:
        print(f"  {nm}: {exc}")
        continue
    xside = -RX if gx < 0 else RX
    wire("TM1", gx, gy, xside, gy, 2.0)

print(f"  {len(gnd_pts)} points tied radially to the ring")

'''

s = s[:start] + new + s[end:]

s = s.replace('"gnd": (0.0, -300.0, "TM1"),', '"gnd": (0.0, -320.0, "TM1"),')
s = s.replace('"gnd_xmt1": (-155.0, -300.0, "TM1"), "gnd_ring": (155.0, -300.0, "TM1"),',
              '"gnd_xmt1": (-165.0, -200.0, "TM1"), "gnd_ring": (165.0, -200.0, "TM1"),')

p.write_text(s)
print("ground rewritten as a perimeter ring")
