import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

old_start = s.index('    gy = g.top + 0.10')
old_end = s.index('    print(f"  bit {i}: gate at')

new = '''    # MEASURED, not assumed. From the PCell geometry:
    #
    #   bank switch (w=8u l=0.13u ng=2)
    #     gate poly      0.130 x 4.360   y -0.18 .. 4.18
    #     active         0.000 .. 4.000
    #     guard ring M1  y 4.88 .. 5.18   (bar at centre y 5.03, 0.30 tall)
    #     contact        0.160 x 0.160
    #
    # The gate is 0.130 um wide and a contact is 0.160 um — the contact is
    # WIDER THAN THE GATE, so nothing can ever land on the gate itself. And the
    # poly overhang above the active area is only 0.18 um, while a contact plus
    # its enclosure needs about 0.30 um. Neither location works.
    #
    # What does work is the 0.70 um band between the gate top (4.18) and the
    # guard ring (4.88): extend the poly up into it, stopping 0.10 um short of
    # the ring for Gat.d (0.07 um minimum GatPoly-to-Activ), and put a single
    # contact there with its own Metal1 pad for M1.d (0.144 um2 minimum).
    #
    # The earlier attempt placed the pad at 4.23..4.83 against a ring starting
    # at 4.88 and a rows=2 stack spanning 4.18..4.88 — it missed by 50 nm,
    # which is what Gat.d and the three Cnt rules were reporting.
    ring_in = min((sh.dbbox().transformed(sw.dcplx_trans).bottom
                   for sh in layout.cell(sw.cell_index).shapes(LI["M1"]).each()
                   if sh.dbbox().width() > 2.0
                   and sh.dbbox().transformed(sw.dcplx_trans).bottom > g.top),
                  default=g.top + 0.9)

    pad_lo = snap(g.top - 0.05)
    pad_hi = snap(ring_in - 0.17)          # Gat.d: 0.07 clear, plus margin
    cy = snap(0.5 * (pad_lo + pad_hi))

    # Poly pad, wide enough to enclose a 0.16 um contact.
    top.shapes(LI["poly"]).insert(pya.DBox(
        snap(g.center().x - 0.22), pad_lo,
        snap(g.center().x + 0.22), pad_hi))
    # One contact, exactly 0.16 um.
    top.shapes(layout.layer(6, 0)).insert(pya.DBox(
        snap(g.center().x - 0.08), snap(cy - 0.08),
        snap(g.center().x + 0.08), snap(cy + 0.08)))
    # Metal1 landing, 0.4 x 0.4 = 0.16 um2, over the M1.d minimum.
    top.shapes(LI["M1"]).insert(pya.DBox(
        snap(g.center().x - 0.20), snap(cy - 0.20),
        snap(g.center().x + 0.20), snap(cy + 0.20)))
    drop(g.center().x, cy, "M2", cols=1, rows=1)

    path("M2", [(g.center().x, cy),
                (g.center().x, yb - 8.0),
                (-38.0 + 5.0 * i, yb - 8.0),
                (-38.0 + 5.0 * i, -145.0)], w=0.4)
'''

s = s[:old_start] + new + s[old_end:]
p.write_text(s)
print("band-select contact placed from measured geometry")
