# A 19–21 GHz LC VCO in IHP SG13G2

Design, verification and layout of a switched-band voltage-controlled
oscillator in a 130 nm SiGe BiCMOS open PDK, using only free tools on a
laptop.

## Result

| | |
|---|---|
| Frequency | 19.01 – 21.26 GHz, continuous |
| Tuning range | 11.1%, four overlapping bands |
| KVCO | 261 – 316 MHz/V |
| Phase noise | −104.3 dBc/Hz at 1 MHz offset |
| Output | −2.4 to −3.0 dBm differential into 50 Ω |
| Supply | 3.3 V; 6.6 mW core, 33 mW including buffers |
| Tank | 0.901 nH, Q 9.68 at 20 GHz, EM-extracted |
| Layout | 29 devices, 300 × 433 µm, DRC clean |
| FoM | −181.6 dBc/Hz |

Every figure comes from simulation of components characterised in this
process, not from datasheet values or textbook estimates.

## Why this circuit

The bottleneck in AI datacentre hardware is not compute cores; it is the
mixed-signal layer around them — SerDes, HBM PHYs, PLLs. A 112G or 224G link
is an RF problem: channel loss, S-parameters, jitter budgets. The clock source
behind such a link is an LC VCO in the 15–25 GHz range, and its phase noise
sets the jitter floor.

SG13G2 is a good fit for that: SiGe HBTs with ~350 GHz fT, an Apache-licensed
open PDK, and thick top metal suitable for on-chip inductors. It is also
underused by the open-source community, which is largely digital.

## Toolchain

IIC-OSIC-TOOLS in Docker on Windows, WSL2 capped at 4 GB. ngspice for
circuit simulation, openEMS and Palace for electromagnetic extraction,
KLayout for layout, DRC and LVS. Total cost: nothing.

The 4 GB memory cap shaped several decisions and is noted where it did.

---

## 1. Device characterisation

### HBT

The npn13G2 was swept for fT against collector current at Vce = 1 V, using an
AC analysis with the base driven by a current source and the collector held at
AC ground — h21 falls to unity at fT, and with a 1 A AC base current the
collector current *is* h21.

| Ib | Ic | β | fT |
|---|---|---|---|
| 1 µA | 0.62 mA | 621 | 335 GHz |
| 5 µA | 1.80 mA | 359 | **415 GHz** |
| 10 µA | 2.67 mA | 267 | 402 GHz |
| 30 µA | 4.18 mA | 139 | 224 GHz |
| 50 µA | 2.05 mA | 41 | 46 GHz |

Peak fT is 415 GHz at Ic ≈ 1.8 mA. The peak is broad — above 400 GHz from
1 to 2.7 mA — so the bias point is not critical. Above ~4 mA the device enters
high injection and fT collapses; note the collector current *falls* while base
current rises. That cliff appears again independently in the buffer
characterisation later, which is a useful cross-check.

At 20 GHz there is roughly 20× headroom, so the transistor is not the limiting
element. The tank is.

### Inductor

The PDK ships an FEM synthesis flow (gds2palace) that generates candidate
spiral geometries, simulates them, and re-tunes the best to a target value.
The first attempt used the 2 nH example shipped with the PDK:

> 1.7 nH, self-resonant at 23 GHz, Q peaking at 19 just below resonance.

A 20 GHz oscillator would sit at 87% of that SRF — where inductance is
strongly frequency-dependent and process variation moves the operating point
substantially. Unusable, and only visible from the EM sweep. A closed-form
calculation would have said 1.7 nH resonates near 20 GHz with 37 fF and looked
entirely fine.

Synthesising for smaller values gave 0.45 nH with Q 6.8. Then a question worth
asking: does Q vary with inductor size? I had assumed roughly not.

> **0.901 nH: Q 9.68 at 20 GHz, SRF above 40 GHz.**

Q rose 43% with double the inductance. Larger spirals have lower series
resistance per unit inductance in this range. Combined with the doubled
inductance, tank Rp went from 385 Ω to 1096 Ω — nearly 3×.

Geometry: 2 turns, 6 µm track, 3 µm spacing, 110.59 µm outer diameter.

### Varactor

The sg13_hv_svaricap was characterised differentially via S-parameters,
sweeping the gate–well voltage and extracting C and Q from the differential
impedance.

| Vtune | C | Q |
|---|---|---|
| −3.5 V | 22.57 fF | 30.6 |
| +3.5 V | 41.11 fF | 21.9 |

Ratio 1.82. Q falls as capacitance rises, so phase noise is slightly worse at
the low-frequency end of each band — an asymmetry that shows up later in the
oscillator's output amplitude.

---

## 2. Circuit design

Cross-coupled NPN pair, LC tank with a centre-tapped inductor feeding the
supply, switched capacitor bank for coarse tuning, varactor for fine tuning,
emitter-follower output buffers, cascode current mirrors for bias.

### Startup and bias

With Rp = 1096 Ω, oscillation needs gm > 2/Rp = 1.8 mS. The design runs
2 mA tail current, roughly 1 mA per device — about 14× the startup
requirement. Startup margin is not the binding constraint; amplitude is, since
phase noise falls as signal power rises.

Sweeping tail current showed the returns flatten quickly:

| Itail | swing | droop across bands | power |
|---|---|---|---|
| 2.0 mA | 1.76 → 1.68 Vpp | 4.6% | 6.6 mW |
| 2.3 mA | 1.79 → 1.73 Vpp | 3.2% | 7.6 mW |
| 2.6 mA | 1.82 → 1.74 Vpp | 4.4% | 8.6 mW |

2.3 mA buys 0.25 dB of amplitude for 15% more power, and pulls the whole band
down 250 MHz because Cbe grows with current. Not worth it. 2 mA stands.

### The varactor connection

The first working design tied the varactor gates directly to the tank, which
sits at Vcc through the inductor. The device therefore saw Vg − Vw = 3.3 −
Vtune, and sweeping Vtune across the full supply only walked the C–V curve
from +3.3 V down to 0 V of gate–well bias.

That region is nearly flat. Measured result: **2.3% tuning**, with the
frequency essentially static below Vtune = 2.4 V.

Adding coupling capacitors to break the DC path, and biasing the gates
independently at mid-supply, moved the device onto the steep centre of its
S-curve. Tuning went to 5.4% on the same varactor.

The coupling capacitors sit in series with the varactor and shrink its
effective swing:

| Cc | usable range | swing lost |
|---|---|---|
| 100 fF | 15.6–22.6 fF | 62% |
| 400 fF | 20.3–34.1 fF | 25% |
| 4 pF | 21.6–38.0 fF | 12% |

4 pF keeps most of it, at 52 × 52 µm each — the second-largest objects on the
die after the inductor.

### Switched capacitor bank

Wide tuning from a single large varactor is possible but makes KVCO enormous:
an Nx=40 device covering 18.0–22.8 GHz gives 1458 MHz/V, so a millivolt of
noise on the tune line becomes 1.5 MHz of frequency error — landing straight
in the phase noise the tank Q exists to protect.

Splitting the job fixes that. A binary-weighted bank selects a coarse band; a
small varactor tunes within it. Same total range, an order of magnitude lower
KVCO, and a *smaller* varactor, so the tank is less lossy.

Each branch is a split capacitor pair with its switch between them, keeping
the structure symmetric — a single-ended switch would unbalance a differential
tank. Bleed resistors hold the switch nodes at a defined DC level when off;
without them those nodes float and the operating point is undefined.

### Switch sizing

The switches are the hard part. On, they add Ron to the tank; off, their drain
capacitance still loads it. Sweeping the width:

| switch W | coverage | tuning | bank authority | amplitude droop |
|---|---|---|---|---|
| 40 µm | 17.68–18.74 GHz | 5.8% | 697 MHz | — |
| 10 µm | 17.69–20.01 GHz | 12.3% | 1957 MHz | — |
| 4 µm | 17.69–21.14 GHz | 17.8% | 3080 MHz | 27% |
| 2 µm | 17.70–21.88 GHz | 21.2% | 3810 MHz | 35% |

Off-state capacitance dominates: narrowing the switches nearly quadrupled the
bank's authority. But below 4 µm the on-resistance starts loading the tank
and amplitude droops across codes. 4 µm is the knee.

Note the bottom of the range barely moves — with every branch switched in, the
tank capacitance is set by the capacitors, not the switches. All the
improvement is at the top, where off-state parasitic matters. The mechanism is
visible directly in the data.

### Buffers

Emitter followers. With the collector at AC ground, Cbe is bootstrapped by the
follower action and barely appears at the input; only Cbc loads the tank. A
common-emitter stage would give gain but Miller-multiply Cbc.

| Nx | Ibuf | Cin | Av into 50 Ω |
|---|---|---|---|
| 1 | 2 mA | 5.73 fF | 0.508 |
| 2 | 4 mA | 8.87 fF | 0.671 |
| 4 | 4 mA | 13.69 fF | 0.755 |

Nx=2 is the knee: Nx=1 saves 2.3 fF but costs 1.5 dB of gain; Nx=4 buys 0.08
more gain for nearly double the loading.

At Nx=1, 6 mA the input capacitance jumps 38% while gain barely improves —
the high-injection cliff from the fT characterisation, appearing in an
independent measurement.

With the buffers attached, tank amplitude went from 1.746 to 1.757 Vpp — under
0.1 dB. The follower's real input resistance is high enough to be negligible
against a 1096 Ω tank, which was the main risk in adding them.

### Bias

Cascode current mirrors. The simple mirror gave 6.4 kΩ of output impedance;
the tail node swings at 2f₀, and a soft current source lets the tail current
modulate with it. Cascoding raised that to 157 kΩ for 0.5 V of headroom out of
the 2.43 V available.

Mirror devices use L = 1 µm rather than the switches' 0.13 µm. Flicker noise
goes as 1/(W·L) and the tail's 1/f noise upconverts into the phase noise
skirt, so length is bought deliberately there — the opposite choice from the
switches, in the same process, for a specific reason.

---

## 3. Verification

### Corners

Four process corners at both band edges:

| corner | code 0 | code 15 | max swing | output |
|---|---|---|---|---|
| bcs/ff | 20.232 GHz | 18.497 GHz | 1.760 Vpp | −2.4 dBm |
| typ/tt | 20.126 GHz | 18.223 GHz | 1.757 Vpp | −2.6 dBm |
| wcs/ss | 20.122 GHz | 18.127 GHz | 1.707 Vpp | −3.0 dBm |
| wcs/ff | 20.213 GHz | 18.243 GHz | 1.716 Vpp | — |

**Total spread 110 MHz at the band top, 369 MHz at the bottom.** Output power
varies 0.6 dB. Oscillation is reliable at every corner.

The tank is dominated by the EM-extracted inductor and MIM capacitors, which
do not vary with process corner. The transistors contribute ~15 fF of a 70 fF
tank, so even a 17% shift in their junction capacitance moves the total by
about 3%. The asymmetry — more spread at the low band — is the switched bank:
with all branches in, the MOS corner adds its own variation.

### Phase noise

ngspice has no harmonic-balance pnoise, so this used transient plus FFT: run
long after startup, FFT the differential output, read the skirt.

| offset | measured | Leeson |
|---|---|---|
| 500 kHz | −99.6 dBc/Hz | |
| **1 MHz** | **−104.3 dBc/Hz** | −101.2 |
| 2 MHz | −119.7 dBc/Hz | |
| 10 MHz | −129.3 dBc/Hz | −121.2 |

Within 3 dB of the Leeson estimate from the EM-extracted tank Q — good
agreement between two independent methods. From 500 kHz outward the slope is
roughly −20 dB/decade, the 1/f² region Leeson predicts.

The 100 kHz point is not trustworthy: at 1.5 FFT bins from the carrier it is
dominated by spectral leakage, not oscillator noise.

---

## 4. Layout

Scripted rather than drawn. The tank is differential, and any mismatch between
the two sides becomes oscillator imbalance directly — hand-placing mirrored
devices is exactly where that error creeps in. Every differential pair is
placed as a computed reflection about x = 0.

**29 devices, 300 × 433 µm, DRC clean.**

### Two constraints that only appeared at layout

**The inductor's footprint is ±85.3 µm, not the ±55 its 110.59 µm spiral
diameter suggests.** The NoRCX blanket and fill-blocking layers extend well
past the coil. Devices placed inside that footprint trip latch-up rules
(LU.a) and contact rules (CntB.h1). The whole floorplan moved down 25 µm.

**The smallest DRC-clean MIM capacitor is 10 fF.** Below that the TopMetal1
top plate falls under minimum width (TM1.a). The PCell will build down to
1.14 µm — matching the DRC area rule — but the metal it draws at those sizes
is illegal.

The designed 4-bit bank needed 4.16 and 8.32 fF capacitors. Two of four bits
were unbuildable.

### The bank redesign

The split-capacitor topology softened the blow: two capacitors in series
either side of the switch means a 10 fF pair gives a 5 fF branch. The bank
became 2-bit with a 5 fF LSB.

| | designed | buildable |
|---|---|---|
| Bank | 4-bit, 2.08 fF LSB | 2-bit, 5 fF LSB |
| Bands | 16 | 4 |
| Coverage | 18.13–20.23 GHz | 19.01–21.26 GHz |
| Tuning | 12.3% | 11.1% |
| KVCO | 111–147 MHz/V | 261–316 MHz/V |

Re-simulated to confirm the bands still overlap:

| code | f_max | f_min | overlap to next |
|---|---|---|---|
| 0 | 21.256 | 20.213 | +566 MHz |
| 1 | 20.779 | 19.801 | +492 MHz |
| 2 | 20.293 | 19.379 | +497 MHz |
| 3 | 19.876 | 19.014 | — |

Continuous, with roughly half a band of margin. The Nx=4 varactor is in fact
larger than needed; a smaller one would load the tank less.

---

## 5. Limitations

Stated plainly, because they bound what the numbers mean.

**Temperature corners were not simulated.** The VBIC self-heating model does
not converge in ngspice across −40 to +125 °C for this circuit. All results
are at 27 °C.

**Phase noise was measured with ideal current sources.** The cascode mirrors
are designed and DC-verified, but ngspice cannot complete a transient with
them in place — it aborts in the VBIC model on the cross-coupled devices,
regardless of initial conditions, integration method, tolerances, or the
self-heating flag. A real tail mirror injects noise that is often the dominant
close-in contributor, so the −104.3 dBc/Hz figure is optimistic by an unknown
margin.

**Bank capacitors sit below the characterised MIM model range.** The RF model
spans 7–75 µm (74 fF and up); the bank uses 10 and 20 fF devices. They are
manufacturable and DRC clean, but their values come from the 1.5 fF/µm² area
coefficient rather than the full model, so the parasitic terms are not
guaranteed.

**The layout is placed but not routed.** No LVS match, no parasitic
extraction. Extracted parasitics would land on the tank and shift the band
plan, requiring the fixed capacitor to be re-trimmed and the corners re-run.

**Phase noise was measured at one band code only**, and only on the 4-bit
design. Tank Q differs across the bank, so the figure will vary.

---

## 6. Toolchain issues found

Four reproducible defects in the open-source flow, each of which silently
produced wrong output rather than erroring:

1. **gds2palace vs scikit-rf 2.x.** `skrf.connect` moved out of the top-level
   namespace; Palace's de-embedding script still expects the 1.x API. Fixed
   with a `sitecustomize.py` shim.

2. **Inductor synthesis emits off-grid geometry.** The 45° octagon vertices
   land 2–3 nm off the 5 nm manufacturing grid, so IHP's own synthesis output
   fails IHP's own DRC. Fixed by snapping.

3. **KLayout's SPICE reader in this PDK takes the device model as a `MODEL=`
   parameter, not positionally.** `R1 a b 100k MODEL=rhigh` works;
   `R1 a b rhigh 100k` silently fails with "Invalid terminal name: 'A'",
   which points at terminals rather than the model.

4. **The nmos PCell substitutes minimum width without erroring.** `w` is total
   width and `ng` divides it into fingers; asking for `w=139u, ng=1` yields a
   0.15 µm device and a warning buried in the log. Four mirror transistors
   were silently the wrong size.

---

## Reproducing

```
git clone https://github.com/Lohithr123/sg13g2-vco.git
cd sg13g2-vco
cd designs
# circuit
ngspice vco/vco_2bit.spice
# layout
klayout -z -nn $PDK_ROOT/ihp-sg13g2/libs.tech/klayout/tech/sg13g2.lyt \
        -r vco/layout/build_layout.py
python3 $PDK_ROOT/ihp-sg13g2/libs.tech/klayout/tech/drc/run_drc.py \
        --path=vco/layout/vco_20g.gds --no_density
```

Requires IIC-OSIC-TOOLS with the IHP SG13G2 PDK.
