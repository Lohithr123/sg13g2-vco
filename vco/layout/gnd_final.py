import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

start = s.index('# --- ground rail ---')
end = s.index('layout.write(OUT)')

new = '''# --- ground ---
#
# Ground touches ten scattered points: four lower-mirror sources and six psub
# guard rings. Three earlier attempts each freed one net and caught another —
# the tail, then the band-select lines, then the cascode bus, then Vcc — because
# every route between those points crossed a layer somebody else owned.
#
# The way through is to find the layer that is free in each COLUMN rather than
# picking one layer for the whole net:
#
#   Metal2   gate buses at y -184 and -212 span the full width; blocked
#   Metal3   outp runs x -16 down to y -230, then across to x -75; blocked
#   Metal4   outn mirrors that on the right; blocked
#   Metal5   the tail at x 0 and the buffer lanes at x +/-137..143; blocked
#   TopMetal2  Vcc rail at y -160 spans x +/-150; blocked
#   TopMetal1  only the capacitor plates and the inductor — and those sit at
#              x +/-19..71 (coupling), x +/-25 (bank) and above y -85 — so
#              the columns at x -8, +/-95 and +/-130 are clear all the way down
#
# So TopMetal1 it is, with the rail at y -300 below the coupling caps. Points
# in a clear column drop straight to it. The four that sit behind a coupling
# capacitor step out first along y -215, the gap between the mirror row at
# -205 and the caps at -224.

GND_Y = -300.0
wire("TM1", -160.0, GND_Y, 160.0, GND_Y, 4.0)

RREF2 = find("rhigh", x=-75.0, y=-190.0)

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

CAP_L, CAP_R = -75.0, 75.0        # coupling capacitors, with margin
CHAN_Y = -215.0                   # the gap between the mirror row and the caps

for nm, gx, gy in gnd_pts:
    try:
        drop(gx, gy, "TM1", cols=1, rows=2)
    except Exception as exc:
        print(f"  {nm}: {exc}")
        continue
    if CAP_L < gx < CAP_R and gy > -210.0:
        # Behind a coupling capacitor: out along the channel first.
        xdet = -85.0 if gx < 0 else 85.0
        path("TM1", [(gx, gy), (gx, CHAN_Y), (xdet, CHAN_Y),
                     (xdet, GND_Y)], w=2.0)
        route = f"via x {xdet:.0f}"
    else:
        path("TM1", [(gx, gy), (gx, GND_Y)], w=2.0)
        route = "direct"
    print(f"  {nm:12} ({gx:7.1f},{gy:7.1f})  {route}")

print(f"  {len(gnd_pts)} points on the rail at y {GND_Y:.0f}")

'''

s = s[:start] + new + s[end:]
s = s.replace('"gnd": (0.0, -300.0, "TM1"),',
              '"gnd": (0.0, -300.0, "TM1"), "gnd_sw": (-8.0, -250.0, "TM1"),\n'
              '    "gnd_mb": (-130.0, -250.0, "TM1"),')
s = s.replace('{"vcc"}, {"gnd"}]', '{"vcc"}, {"gnd", "gnd_sw", "gnd_mb"}]')

p.write_text(s)
print("ground rewritten: per-column layer choice on TopMetal1")
