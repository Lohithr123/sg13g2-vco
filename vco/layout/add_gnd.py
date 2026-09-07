import pathlib
p = pathlib.Path('route_v2.py'); s = p.read_text()

new = '''
print("\\n=== ground connections ===")
# The rail at y -300 was a bare wire. Ground actually has to reach: the source
# of every lower mirror device, every psub guard ring, and the far end of each
# bleed resistor.
#
# The guard rings are the reason this net is different in kind from the others.
# Each MOSFET's ring is a psub tap around the device, and its Metal1 sits on
# the ring itself — so ground is not a tree of point-to-point routes but a mesh
# that has to touch a dozen scattered places.
#
# TopMetal1 for the rail and the vertical drops, since Metal5 has the tail and
# buffer bias, and the tank owns Metal3 and Metal4.

gnd_pts = []

# Lower mirror sources.
for nm, dev in (("XMR1", XMR1), ("XMT1", XMT1),
                ("XMB1A", MB1A), ("XMB1B", MB1B)):
    if not dev:
        print(f"  {nm}: not found")
        continue
    src = pins(dev, 8, 2)[0]
    gnd_pts.append((nm, src.center().x, src.center().y))

# Guard rings: the ring's Metal1 is the outermost shape on the device, so take
# the bounding box edge rather than a pin.
for nm, dev in (("XSW0", find("nmos", x=-8.0, y=-108.0)),
                ("XSW1", find("nmos", x=-8.0, y=-130.0)),
                ("XMR2", XMR2), ("XMT2", XMT2),
                ("XMB2A", MB2A), ("XMB2B", MB2B)):
    if not dev:
        continue
    b = dev.dbbox()
    gnd_pts.append((nm + "_ring", b.center().x, b.bottom + 0.15))

print(f"  {len(gnd_pts)} ground points")

# Drop each to TopMetal1 and run down to the rail. Points above y -250 route
# down the outside to avoid the device field.
for nm, gx, gy in gnd_pts:
    try:
        drop(gx, gy, "TM1", cols=1, rows=2)
    except Exception as exc:
        print(f"  {nm}: stack failed ({exc})")
        continue
    xout = -155.0 if gx < 0 else 155.0
    path("TM1", [(gx, gy), (gx, gy - 6.0), (xout, gy - 6.0),
                 (xout, GND_Y)], w=4.0)

print(f"  all tied to the rail at y {GND_Y}")

'''

s = s.replace('layout.write(OUT)', new + 'layout.write(OUT)')

s = s.replace('''    "vcc": (0.0, -160.0, "TM2"), "gnd": (0.0, -300.0, "TM1"),
})''',
'''    "vcc": (0.0, -160.0, "TM2"), "gnd": (0.0, -300.0, "TM1"),
    "gnd_xmt1": (-155.0, -300.0, "TM1"), "gnd_ring": (155.0, -300.0, "TM1"),
})''')

s = s.replace('''{"vcc"}, {"gnd"}]''',
              '''{"vcc"}, {"gnd", "gnd_xmt1", "gnd_ring"}]''')

p.write_text(s)
print("ground connections added")
