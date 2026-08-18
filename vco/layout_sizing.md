# Layout sizing — 20 GHz VCO, IHP SG13G2

Every device dimension needed to draw the layout, with the source of each
number. Values must land within LVS tolerance of `vco_lvs.cdl`.

## Capacitors — MIM, 1.5 fF/µm²

`cap_carea = 1.5E-15` from `cornerRES.lib`. DRC minimum is 1.14 µm width and
1.30 µm² area (`MIM.a`, `MIM.f`), so the smallest buildable MIM is 1.95 fF.

**The characterised RF model only spans 7–75 µm**, i.e. 74 fF upward. Every
tank capacitor here sits below that. They are manufacturable — DRC passes —
but the parasitic terms in the model are not guaranteed at these sizes, so
values come from the area coefficient alone. Worth stating in any write-up.

| device | value | w × l (µm) | note |
|---|---|---|---|
| CB0A, CB0B | 4.16 fF | 1.67 × 1.67 | bank LSB |
| CB1A, CB1B | 8.32 fF | 2.36 × 2.36 | |
| CB2A, CB2B | 16.64 fF | 3.33 × 3.33 | |
| CB3A, CB3B | 33.28 fF | 4.71 × 4.71 | bank MSB |
| CT | 31.6 fF | 4.59 × 4.59 | fixed tank |
| CC1, CC2 | 4 pF | 51.6 × 51.6 | coupling, inside model range |

The coupling caps are the second-largest objects in the design after the
inductor. If area becomes a problem they are the place to look: 1 pF costs
12% of the varactor's tuning swing, 400 fF costs 25%.

## Resistors — rhigh, 1360 Ω/□

`rsh_rhigh = 1360` from `cornerRES.lib`. DRC minimum width 0.5 µm
(`Rhigh_a.ext_width`), so 1 µm has margin; narrowing to 0.5 µm halves the
length if area demands it.

| device | value | squares | w × l (µm) |
|---|---|---|---|
| RB1, RB2, RREF | 10 kΩ | 7.35 | 1 × 7.35 |
| RBL0A…RBL3B (×8) | 100 kΩ | 73.53 | 1 × 73.5 |

The eight bleed resistors total ~590 µm² and only hold switch nodes at a
defined DC level — no signal current. First candidates for shrinking or
sharing if the floorplan gets tight.

## Active devices

| device | model | parameters |
|---|---|---|
| XQ1, XQ2 | npn13G2 | Nx=1 |
| XB1, XB2 | npn13G2 | Nx=2 |
| XSW0…XSW3 | sg13_lv_nmos | w = 4/8/16/32 µm, l = 0.13 µm |
| XMR1/2 | sg13_lv_nmos | w = 10 µm, l = 1 µm |
| XMT1/2 | sg13_lv_nmos | w = 70 µm, l = 1 µm |
| XMB1A/2A, XMB1B/2B | sg13_lv_nmos | w = 139 µm, l = 1 µm |
| XCV | sg13_hv_svaricap | l = 0.3 µm, w = 3.74 µm, Nx = 2 |

Mirror devices use l = 1 µm rather than the switches' 0.13 µm: flicker noise
goes as 1/(W·L) and the tail's 1/f noise upconverts into the phase noise
skirt, so length is bought deliberately there.

## Inductor

`inductor3_snapped.gds` — 3 terminals (LA, LB tank ends; LC centre tap to
Vcc), 0.90 nH, Q 10.0 at 20 GHz, 110.59 µm outer diameter. DRC clean after
snapping 45° vertices to the 5 nm grid.

## Floorplan notes

The inductor dominates at 110.6 µm; everything else is small beside it.

**Symmetry is the binding constraint.** The tank is differential, so any
imbalance between the outp and outn sides becomes oscillator imbalance. Mirror
everything about a line through the inductor's centre tap: bank branches,
coupling caps, cross-coupled pair, buffers.

**Keep the tank loop tight.** Routing between the inductor terminals and the
cross-coupled pair adds inductance and resistance that were not in the design,
and degrades the Q directly.

**Bias and mirrors are DC** — place them away from the tank, wherever
convenient.
