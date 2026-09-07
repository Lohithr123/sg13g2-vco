import pathlib
p = pathlib.Path('route_v2.py'); s = p.read_text()

new = '''
print("\\n=== supply and ground ===")
# Vcc reaches the inductor centre tap, both buffer collectors and RREF.
# Ground reaches every mirror source, every guard ring and the bleed resistors.
#
# Layer choice, given what is already taken: Metal3 is outp, Metal4 is outn,
# Metal2 carries both gate buses and the band-select lines, Metal5 has the tail
# and the buffer bias. TopMetal2 is used only by the inductor's own centre tap
# at x +/-3, so it is effectively free — and it is the thickest metal, which is
# what a supply rail wants anyway.
#
# Vcc on TopMetal2, ground on TopMetal1 outside the inductor's footprint.
# TopMetal1 minimum width is 1.64 um, so both rails are drawn at 4 um.

VCC_Y = -60.0        # above the devices, below the inductor's -85.3 edge... it
                     # is not: the inductor spans to -85.3, so the rail must be
                     # clear of that. Use -160, in the gap between the varactor
                     # row and the mirror row.
VCC_Y = -160.0
GND_Y = -240.0       # below the mirror rows, above the coupling caps at -224
GND_Y = -300.0       # ...which they are not; -300 is below everything

RREF = find("rhigh", x=-75.0, y=-190.0)
print(f"  RREF   {'ok' if RREF else 'NOT FOUND'}")

# --- Vcc rail ---
wire("TM2", -150.0, VCC_Y, 150.0, VCC_Y, 4.0)

# Inductor centre tap LC is TopMetal2 at x -3..3, y -85.3..-82.3. Bring it down
# on TopMetal2 -- same layer, so no via needed.
wire("TM2", 0.0, -85.3, 0.0, VCC_Y, 4.0)

# Buffer collectors.
if XB1 and XB2:
    for bc in (bc1, bc2):
        drop(bc.x, bc.y, "TM2")
        xside = -150.0 if bc.x < 0 else 150.0
        path("TM2", [(bc.x, bc.y), (xside, bc.y), (xside, VCC_Y)], w=4.0)
    print(f"  Vcc rail at y {VCC_Y}, collectors at "
          f"({bc1.x:.0f},{bc1.y:.0f}) and ({bc2.x:.0f},{bc2.y:.0f})")

# RREF's top end.
if RREF:
    rr = sorted(pins(RREF, 8, 2), key=lambda b: b.center().y)
    drop(rr[-1].center().x, rr[-1].center().y, "TM2")
    path("TM2", [(rr[-1].center().x, rr[-1].center().y),
                 (rr[-1].center().x, VCC_Y)], w=4.0)

# --- ground rail ---
wire("TM1", -150.0, GND_Y, 150.0, GND_Y, 4.0)
print(f"  ground rail at y {GND_Y}")

'''

s = s.replace('layout.write(OUT)', new + 'layout.write(OUT)')

s = s.replace('''    "nb0": (-38.0, -143.0, "M2"), "nb1": (-33.0, -143.0, "M2"),
})''',
'''    "nb0": (-38.0, -143.0, "M2"), "nb1": (-33.0, -143.0, "M2"),
    "vcc": (0.0, -160.0, "TM2"), "gnd": (0.0, -300.0, "TM1"),
})''')

s = s.replace('''        {"nb0"}, {"nb1"}]''',
              '''        {"nb0"}, {"nb1"}, {"vcc"}, {"gnd"}]''')

p.write_text(s)
print("supply and ground added")
