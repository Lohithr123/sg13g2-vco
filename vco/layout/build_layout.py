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
    # DTrans(M90, dx, dy) mirrors FIRST, then translates: a cell whose bbox
    # centre sits at cx lands at -cx + dx. So the offset that puts it at x is
    # x + cx when mirrored, x - cx otherwise. Getting this wrong only shows up
    # on cells whose bbox is not centred on their origin, which is why the
    # bipolars looked fine and the capacitors did not.
    dx = (x + b.center().x) if mirror else (x - b.center().x)
    dy = y - b.center().y
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
place("npn13G2", {"Nx": 1, "Ny": 1}, -9.0, -100.0, label="XQ1")
place("npn13G2", {"Nx": 1, "Ny": 1},  9.0, -100.0, mirror=True, label="XQ2")

print("\n=== switched capacitor bank ===")
# Four branches stacked vertically. Each is a split capacitor pair with its
# switch between them, so the branch stays symmetric about x = 0 — a
# single-ended switch would unbalance the tank.
BANK = [
    # (y, per-side cap value, switch width, switch fingers)
    #
    # 10 fF is the smallest cmim that passes DRC — below that the TopMetal1
    # top plate falls under minimum width (TM1.a). The designed 4-bit bank
    # wanted 4.16 and 8.32 fF caps, which cannot be built.
    #
    # The split-capacitor topology rescues it: two caps in series either side
    # of the switch, so a 10 fF pair gives a 5 fF branch. A 2-bit bank at
    # 5 fF LSB spans 15 fF and gives ~13.6% tuning — slightly more than the
    # unbuildable 4-bit design, because the steps are coarser but the span is
    # wider. The cost is 4 bands instead of 16, so KVCO rises roughly 4x.
    (-108.0, "10f", "8u",  "2"),
    (-130.0, "20f", "16u", "4"),
]
for i, (y, cval, wsw, ngsw) in enumerate(BANK):
    # Capacitors at +/-25 rather than +/-14, and the switch offset from x = 0.
    #
    # The first floorplan put both bank switches on the centre line with their
    # source and drain pins 0.35 um apart — a gap fixed by gate length and
    # contact spacing, not by device size. The tail net also has to pass from
    # the emitters at +/-9 down to the mirror at x -25, through the same strip.
    # Every route into that region collided with another: nine attempts, nine
    # different shorts.
    #
    # Moving the switch to x = -8 gives the tail a clear corridor at x = 0, and
    # widening the capacitor spacing leaves room to approach each switch pin
    # from opposite sides without the two branches converging.
    place("cmim", {"Calculate": "w&l", "C": cval}, -25.0, y, label=f"CB{i}A")
    place("cmim", {"Calculate": "w&l", "C": cval},  25.0, y, mirror=True,
          label=f"CB{i}B")
    place("nmos", {"w": wsw, "l": "0.13u", "ng": ngsw, "m": "1",
                   "guardRingType": "psub"}, -8.0, y, label=f"XSW{i}")

print("\n=== fixed tank capacitor ===")
place("cmim", {"Calculate": "w&l", "C": "31.6f"}, 20.0, -95.0, label="CT")

print("\n=== varactor and coupling ===")
place("SVaricap", {"w": "3.74u", "l": "0.3u", "Nx": 4}, 0.0, -172.0, label="XCV")
# 4 pF is 51.6 um square — the second largest object after the inductor.
place("cmim", {"Calculate": "w&l", "C": "4p"}, -45.0, -250.0, label="CC1")
place("cmim", {"Calculate": "w&l", "C": "4p"},  45.0, -250.0, mirror=True,
      label="CC2")

print("\n=== bias resistors ===")
# rhigh computes its own length from R. NumberOfSegments would serpentine it
# if the strip gets unwieldy; left at 1 for now to keep the first pass simple.
place("rhigh", {"Calculate": "l", "R": "10k", "w": "1u"}, -45.0, -160.0,
      label="RB1")
place("rhigh", {"Calculate": "l", "R": "10k", "w": "1u"},  45.0, -160.0,
      mirror=True, label="RB2")

print("\n=== bleed resistors ===")
# Eight 100k strips holding the switch nodes at a defined DC level. No signal
# current, so they can sit anywhere convenient — out to the sides, clear of
# the tank.
# 75 um strips. Eight of them will not fit beside the bank without hitting
# the inductor, so they go in two columns well outside it. They carry no
# signal current, so distance costs nothing.
for i in range(2):
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
# The tail node swings at twice the oscillation frequency and carries 2 mA,
# so the run from the cross-coupled emitters down to the tail mirror is a real
# inductive path, not just a wire. At MY = -295 that run was 220 um. Moving
# the row up to -190 roughly halves it.
#
# Coordinates are symmetric about x = 0. An earlier floorplan shift used a
# regex that caught x as well as y, which left XMT2/XMT1 at -55/+30 and the
# buffer mirrors skewed. Differential asymmetry does not announce itself.
MY = -190.0

# Tail mirror, directly beneath the cross-coupled pair at x = +/-9.
place("nmos", {"w": "70u", "l": "1u", "ng": "10", "m": "1", "guardRingType": "psub"}, -20.0, MY,
      label="XMT2")
place("nmos", {"w": "70u", "l": "1u", "ng": "10", "m": "1", "guardRingType": "psub"},  20.0, MY,
      mirror=True, label="XMT1")

# Reference branch, off to one side and out of the tank's way.
place("nmos", {"w": "10u", "l": "1u", "ng": "2", "m": "1", "guardRingType": "psub"}, -55.0, MY,
      label="XMR2")
place("nmos", {"w": "10u", "l": "1u", "ng": "2", "m": "1", "guardRingType": "psub"}, -42.0, MY,
      label="XMR1")

# Buffer mirrors, each pair under the buffer it feeds at x = +/-115.
place("nmos", {"w": "139u", "l": "1u", "ng": "20", "m": "1", "guardRingType": "psub"}, -130.0, MY - 120,
      label="XMB2A")
place("nmos", {"w": "139u", "l": "1u", "ng": "20", "m": "1", "guardRingType": "psub"},  -95.0, MY - 120,
      label="XMB1A")
place("nmos", {"w": "139u", "l": "1u", "ng": "20", "m": "1", "guardRingType": "psub"},   95.0, MY - 120,
      mirror=True, label="XMB2B")
place("nmos", {"w": "139u", "l": "1u", "ng": "20", "m": "1", "guardRingType": "psub"},  130.0, MY - 120,
      mirror=True, label="XMB1B")

print("\n=== reference resistor ===")
place("rhigh", {"Calculate": "l", "R": "10k", "w": "1u"}, -75.0, MY,
      label="RREF")

layout.write(OUT)
print(f"\n{len(placed)} devices placed")
print(f"extent: {top.dbbox().width():.1f} x {top.dbbox().height():.1f} um")
print(f"wrote {OUT}")
print("\nNo routing yet — this is placement only. Run DRC to check the")
print("devices themselves are legal before wiring anything.")
