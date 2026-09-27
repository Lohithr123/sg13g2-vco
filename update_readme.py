# Update README.md with the parasitic extraction results.
#
#   python3 update_readme.py
#
# Targeted edits, each checked before it is applied, so nothing else moves.

import pathlib

p = pathlib.Path("README.md")
s = p.read_text(encoding="utf-8")
done, missed = [], []

def rep(old, new, tag):
    global s
    if s.count(old) != 1:
        missed.append(f"{tag} (found {s.count(old)})")
        return
    s = s.replace(old, new)
    done.append(tag)

# ---- 1. headline numbers -------------------------------------------------
rep("| Frequency | 19.01 – 21.26 GHz, continuous |",
    "| Frequency, schematic | 19.01 – 21.26 GHz, continuous |\n"
    "| Frequency, post-layout | 15.06 – 15.37 GHz |",
    "result table frequency")

rep("deck does not extract. Both are covered under [Limitations](#5-limitations).",
    "deck does not extract. The two frequency rows differ because extracted\n"
    "parasitics move the band; section 5 explains why, and section 6 bounds what\n"
    "all of these numbers mean.",
    "note under the table")

# ---- 2. the new section --------------------------------------------------
SECTION = '''## 5. Parasitic extraction

The layout above is DRC clean and LVS clean. Neither says anything about the
capacitance the wiring itself adds, and on a tank of roughly 70 fF there is not
much room for it.

Extracted with KLayout-PEX (`kpex`), 2.5D analytical engine, capacitance only,
MIM devices blackboxed so their modelled value is not counted twice.

### What it found

| | to AC ground | through the 4 pF coupling cap | per side |
|---|---|---|---|
| `outp` | ~60 fF (52.9 to substrate) | ~28 fF (`gp` to substrate) | **~88 fF** |
| `outn` | ~44 fF (37.1 to substrate) | ~40 fF (`gn` to substrate) | **~84 fF** |

Plus 1.9 fF directly across the tank, and 4.5 fF between the varactor gates,
which acts across the tank through the coupling capacitors. Two sides of ~86 fF
in series is ~43 fF differential, so roughly **49 fF added to a 70 fF tank**.

Back-annotated into the testbench and re-simulated:

| code | schematic | extracted | shift |
|---|---|---|---|
| 0 | 20.213 GHz | 15.368 GHz | −24.0% |
| 1 | 19.801 GHz | 15.270 GHz | −22.9% |
| 2 | 19.379 GHz | 15.154 GHz | −21.8% |
| 3 | 19.014 GHz | 15.063 GHz | −20.8% |

Two further effects, both worse than the frequency shift in their way:

**The bank has largely stopped working.** Its reach across the four codes falls
from 1.20 GHz to 0.31 GHz. The bank capacitors are a smaller share of a larger
tank, and each switch node picked up 15–23 fF of its own substrate capacitance,
so an "off" branch still loads the tank.

**Tank swing falls 12%**, from 1.705 to 1.503 Vpp — about 1.1 dB, straight into
the phase noise.

### What is not double-counted

Two things looked like they might already be in the simulation. Both were
checked rather than assumed:

**The inductor is not extracted at all.** Re-running the extraction with the
spiral deleted produced byte-identical capacitances — only two net numbers
changed. The NoRCX blanket over the inductor footprint does exactly what it is
for, so the EM model's own capacitance is not counted a second time.

**The MIM bottom plates are not in the model.** `cap_cmim` in the PDK is a
55 mΩ series resistor and the plate-to-plate capacitor, with no bottom-plate
term. The 25–37 fF each plate presents to the substrate is therefore real, and
missing from the schematic.

### Why it cannot be trimmed out

CT is 31.6 fF. Removing it entirely still leaves the tank near 18 GHz, below
the band. Re-centring at 20.2 GHz needs about **0.52 nH instead of 0.901** —
and the 0.45 nH spiral characterised in section 1 had Q 6.8 against 9.68, so
that is paid for in phase noise. The bank would need resizing too, since a
smaller inductor does not restore its share of the tank.

The other levers are a trade against tuning range and layout:

- **Smaller coupling capacitors.** The 52 × 52 µm plates contribute much of the
  substrate load. 400 fF would shrink them roughly tenfold, at the cost of
  varactor swing — 25% lost instead of 12%, from the table in section 2.
- **Move `outp` up a layer.** It runs on Metal3, closer to the substrate than
  `outn` on Metal4, and carries 15 fF more direct substrate capacitance as a
  result. For a differential tank that asymmetry is a defect in itself.

This is the point of extraction, and it is worth stating plainly: the design is
DRC clean, LVS clean, and misses its band by more than 20%. Nothing earlier in
the flow could have told me that.

---

'''

rep("## 5. Limitations", SECTION + "## 6. Limitations", "new section 5")
rep("## 6. Toolchain issues found", "## 7. Toolchain issues found", "renumber toolchain")

# ---- 3. limitations ------------------------------------------------------
rep("""**No parasitic extraction yet.** Extracted parasitics will land on the tank and
shift the band plan; the fixed capacitor will need re-trimming and the corners
re-running. This is the next piece of work, and the real test of the layout.""",
    """**The extraction is 2.5D, not a field solve.** The analytical engine tends to
over-estimate substrate coupling, so the 24% shift in section 5 is an upper
estimate. A FasterCap run on the tank nets would tighten it. Cutting the other
way, the extraction treats the substrate as a perfect lossless ground, so real
substrate resistance will make Q worse than the re-simulation shows.

**Bias nets were grounded in the back-annotation.** The testbench models the
tail as an ideal source, so the mirror bias nodes do not exist in it. Their
extracted capacitance was tied to ground, which slightly over-counts the load.

**The post-layout design has not been re-verified.** The 15.1–15.4 GHz figures
come from re-simulating the existing testbench with extracted capacitance. The
corners, phase noise and band plan have not been re-run, because the sensible
next step is to fix the design rather than characterise it as it stands.""",
    "limitations: PEX")

# ---- 4. toolchain issues -------------------------------------------------
rep("""9. **Inductor extraction is commented out** of the PDK's LVS deck, so the
   spiral does not extract as a device.""",
    """9. **Inductor extraction is commented out** of the PDK's LVS deck, so the
   spiral does not extract as a device.

10. **`cap_cmim` has no bottom-plate capacitance.** The model is a series
    resistor and the plate-to-plate capacitor only, so a MIM's substrate
    parasitic is absent from simulation and must come from extraction.

11. **kpex cannot read this PDK's LVS database.** Passing `--lvsdb` from
    `run_lvs.py` gives "No extracted layers found"; the layer naming does not
    match what kpex expects. It has to run its own LVS from the GDS.

12. **kpex crashes writing its SPICE output.** The 2.5D extraction completes
    and the CSV is written, then the netlist writer fails with "Invalid
    parameter name: 'C'". The CSV is the usable result.""",
    "toolchain: new items")

# ---- 5. reproducing ------------------------------------------------------
rep("""        --no_series_res --no_parallel_res \\
        --disable_tap_extraction --top_lvl_pins
```""",
    """        --no_series_res --no_parallel_res \\
        --disable_tap_extraction --top_lvl_pins

# parasitic extraction and re-simulation
kpex --pdk ihp_sg13g2 --gds vco_20g_routed.gds --schematic ../vco_lvs.cdl \\
     --cell vco_20g --2.5D --mode CC --blackbox true --out_dir pex/run
klayout -z -r pex_summary.py      # per-net capacitance, named
klayout -z -r pex_to_spice.py     # writes pex_caps.inc, vco_2bit_pex.spice
cd .. && ngspice -b vco_2bit_pex.spice
```""",
    "reproducing: PEX commands")

p.write_text(s, encoding="utf-8")
print(f"applied {len(done)}:")
for d in done:
    print("   ", d)
if missed:
    print("NOT APPLIED:")
    for m in missed:
        print("   ", m)
