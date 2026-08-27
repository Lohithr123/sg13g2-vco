# Layout generator — 20 GHz VCO, IHP SG13G2
#
# Run headless:
#   klayout -z -nn $PDK_ROOT/ihp-sg13g2/libs.tech/klayout/tech/sg13g2.lyt \
#           -r build_layout.py
#
# WHY SCRIPTED RATHER THAN DRAWN
#
# The tank is differential. Any mismatch between the outp and outn sides shows
# up directly as oscillator imbalance, and hand-placing mirrored devices is
# exactly where that error creeps in. Here every differential pair is placed as
# a true reflection about x = 0, computed rather than eyeballed.
#
# It also makes the layout reproducible and diffable: the GDS is a build
# artefact, this file is the source.
#
# PCELL NOTES (from the library introspection)
#   cmim     Calculate='w&l' — give it a target C and it sizes itself.
#            Wmin/Lmin = 1.14u, so it goes down to ~2 fF. This is the plain
#            MIM: no characterised RF model, but it builds at the sizes the
#            bank needs.
#   rfcmim   has the RF model but Wmin/Lmin = 7u, i.e. 74.8 fF floor — too
#            coarse for a 70 fF tank, so it is not used here.
#   rhigh    Calculate='l' — give it R and it computes the length.
#            Rspec = 1300 ohm/sq (note: cornerRES.lib says 1360; the PCell's
#            own number is the one that matters for what gets drawn).
#   nmos     w, l, ng, m as strings with units.
#   npn13G2  Nx, Ny as integers.

import os
import sys

import pya

# The PDK's PCell library is a Python module. KLayout's batch mode does not
# auto-load it, so import it explicitly to force library registration.
PDK = os.environ.get("PDK_ROOT", "/foss/pdks") + "/ihp-sg13g2"
sys.path.insert(0, PDK + "/libs.tech/klayout/python")
import sg13g2_pycell_lib  # noqa: F401  (imported for its registration side effect)

LIB = "SG13_dev"
TECH = "sg13g2"
IND_GDS = "/foss/designs/inductor_synth/inductor3_snapped.gds"
OUT = "/foss/designs/vco/layout/vco_20g.gds"

# Resolve the library WITH its technology. The three-argument shorthand
# layout.create_cell(name, lib, params) cannot reach a technology-scoped
# library and silently returns None for every device — which looks like a
# parameter problem and is not. add_pcell_variant takes the library handle
# directly, so resolve it once here.
lib = pya.Library.library_by_name(LIB, TECH)
if lib is None:
    raise RuntimeError(f"library {LIB} not found for technology {TECH}")
liblay = lib.layout()

layout = pya.Layout()
layout.dbu = 0.001
top = layout.create_cell("vco_20g")

placed = []


def place(pcell, params, x, y, mirror=False, label="", anchor="c"):
    """Instantiate a PCell with its BOUNDING BOX centred on (x, y).

    PCell origins are not centred — rhigh in particular grows upward from its
    origin, so a 75 um strip placed at y=-100 reached y=-25 and ploughed
    straight through the inductor. Measuring the cell and offsetting by its
    centre makes the coordinates below mean what they say.

    mirror reflects about the vertical axis: every differential partner is a
    reflection, never a translated copy.
    """
    name = label or pcell
    try:
        pid = liblay.pcell_id(pcell)
        if pid is None:
            print(f"  FAIL  {name}: no PCell named {pcell!r}")
            return None
        ci = layout.add_pcell_variant(lib, pid, params)
    except Exception as exc:
        print(f"  FAIL  {name}: {exc}")
        return None

    b = layout.cell(ci).dbbox()
    dx, dy = x - b.center().x, y - b.center().y
    if anchor == "t":          # hang below y
        dy = y - b.top
    elif anchor == "b":        # sit above y
        dy = y - b.bottom
    trans = (pya.DTrans(pya.DTrans.M90, dx, dy) if mirror
             else pya.DTrans(dx, dy))
    top.insert(pya.DCellInstArray(ci, trans))
    placed.append((name, b.width(), b.height()))
    print(f"  ok    {name:14} {b.width():6.2f} x {b.height():5.2f}"
          f"  at ({x:7.1f},{y:7.1f}){'  mir' if mirror else ''}")
    return ci


print("\n=== inductor ===")
# The inductor is the largest object and defines the symmetry line. Everything
# else hangs below it so the tank loop stays short — routing between the
# inductor terminals and the cross-coupled pair is inductance and resistance
# that was never in the design, and it eats the Q directly.
try:
    ind = pya.Layout()
    ind.read(IND_GDS)
    src_top = ind.top_cell()
    dest = layout.create_cell(src_top.name)
    dest.copy_tree(src_top)
    top.insert(pya.DCellInstArray(dest.cell_index(), pya.DTrans(0.0, 0.0)))
    print(f"  ok    {src_top.name} at origin")
except Exception as exc:
    print(f"  FAIL  inductor: {exc}")

print("\n=== cross-coupled pair ===")
place("npn13G2", {"Nx": 1, "Ny": 1}, -40.0, -100.0, label="XQ1")
place("npn13G2", {"Nx": 1, "Ny": 1},  15.0, -100.0, mirror=True, label="XQ2")

print("\n=== switched capacitor bank ===")
# Four branches stacked vertically. Each is a split capacitor pair with its
# switch between them, so the branch stays symmetric about x = 0 — a
# single-ended switch would unbalance the tank.
BANK = [
    # (y, cap value, switch width)
    (-108.0, "4.16f",  "4u",  "1"),
    (-122.0, "8.32f",  "8u",  "2"),
    (-136.0, "16.64f", "16u", "4"),
    (-150.0, "33.28f", "32u", "8"),
]
for i, (y, cval, wsw, ngsw) in enumerate(BANK):
    place("cmim", {"Calculate": "w&l", "C": cval}, -43.0, y, label=f"CB{i}A")
    place("cmim", {"Calculate": "w&l", "C": cval},  18.0, y, mirror=True,
          label=f"CB{i}B")
    place("nmos", {"w": wsw, "l": "0.13u", "ng": ngsw, "m": "1", "guardRingType": "psub"}, 0.0, y,
          label=f"XSW{i}")

print("\n=== fixed tank capacitor ===")
place("cmim", {"Calculate": "w&l", "C": "31.6f"}, 0.0, -113.0, label="CT")

print("\n=== varactor and coupling ===")
place("SVaricap", {"w": "3.74u", "l": "0.3u", "Nx": 2}, 0.0, -172.0, label="XCV")
# 4 pF is 51.6 um square — the second largest object after the inductor.
place("cmim", {"Calculate": "w&l", "C": "4p"}, -100.0, -215.0, label="CC1")
place("cmim", {"Calculate": "w&l", "C": "4p"},  75.0, -215.0, mirror=True,
      label="CC2")

print("\n=== bias resistors ===")
# rhigh computes its own length from R. NumberOfSegments would serpentine it
# if the strip gets unwieldy; left at 1 for now to keep the first pass simple.
place("rhigh", {"Calculate": "l", "R": "10k", "w": "1u"}, -50.0, -185.0,
      label="RB1")
place("rhigh", {"Calculate": "l", "R": "10k", "w": "1u"},  25.0, -185.0,
      mirror=True, label="RB2")

print("\n=== bleed resistors ===")
# Eight 100k strips holding the switch nodes at a defined DC level. No signal
# current, so they can sit anywhere convenient — out to the sides, clear of
# the tank.
# 75 um strips. Eight of them will not fit beside the bank without hitting
# the inductor, so they go in two columns well outside it. They carry no
# signal current, so distance costs nothing.
for i in range(4):
    yb = -225.0 - (i % 2) * 85.0
    xb = 150.0 + (i // 2) * 12.0
    place("rhigh", {"Calculate": "l", "R": "100k", "w": "1u"}, -xb, yb,
          label=f"RBL{i}A")
    place("rhigh", {"Calculate": "l", "R": "100k", "w": "1u"}, xb, yb,
          mirror=True, label=f"RBL{i}B")

print("\n=== output buffers ===")
place("npn13G2", {"Nx": 2, "Ny": 1}, -115.0, -95.0, label="XB1")
place("npn13G2", {"Nx": 2, "Ny": 1},  115.0, -95.0, mirror=True, label="XB2")

print("\n=== cascode mirrors ===")
# DC only, so distance from the tank costs nothing. Placed well below
# everything else.
MY = -295.0
place("nmos", {"w": "10u", "l": "1u", "ng": "2", "m": "1", "guardRingType": "psub"}, -105.0, MY,
      label="XMR2")
place("nmos", {"w": "10u", "l": "1u", "ng": "2", "m": "1", "guardRingType": "psub"},  -95.0, MY,
      label="XMR1")
place("nmos", {"w": "70u", "l": "1u", "ng": "10", "m": "1", "guardRingType": "psub"},  -55.0, MY,
      label="XMT2")
place("nmos", {"w": "70u", "l": "1u", "ng": "10", "m": "1", "guardRingType": "psub"},   30.0, MY,
      label="XMT1")
place("nmos", {"w": "139u", "l": "1u", "ng": "20", "m": "1", "guardRingType": "psub"}, -105.0, MY - 25,
      label="XMB2A")
place("nmos", {"w": "139u", "l": "1u", "ng": "20", "m": "1", "guardRingType": "psub"},  -60.0, MY - 25,
      label="XMB1A")
place("nmos", {"w": "139u", "l": "1u", "ng": "20", "m": "1", "guardRingType": "psub"},   35.0, MY - 25,
      mirror=True, label="XMB2B")
place("nmos", {"w": "139u", "l": "1u", "ng": "20", "m": "1", "guardRingType": "psub"},  105.0, MY - 25,
      mirror=True, label="XMB1B")

print("\n=== reference resistor ===")
place("rhigh", {"Calculate": "l", "R": "10k", "w": "1u"}, -150.0, MY,
      label="RREF")

layout.write(OUT)
print(f"\n{len(placed)} devices placed")
print(f"extent: {top.dbbox().width():.1f} x {top.dbbox().height():.1f} um")
print(f"wrote {OUT}")
print("\nNo routing yet — this is placement only. Run DRC to check the")
print("devices themselves are legal before wiring anything.")
