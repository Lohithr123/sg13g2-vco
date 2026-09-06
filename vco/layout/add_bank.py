import pathlib
p = pathlib.Path('route_v2.py'); s = p.read_text()

new = '''
print("\\n=== bank branches ===")
# Each branch: tank node -> capacitor -> switch -> capacitor -> other tank node.
# The split-capacitor arrangement keeps the branch symmetric; a single-ended
# switch would unbalance the tank.
#
# Layer choice matters here. The capacitor's top plate is TopMetal1 and its
# bottom plate Metal5 — but Metal5 already carries the tail net down the centre
# at x = 0, straight past both switches. So the tank side connects to the TOP
# plate on TopMetal1, and the switch side leaves the BOTTOM plate on Metal5 but
# jogs out to x = +/-6 before turning down, clear of the tail.
#
# The bank sits below the inductor (whose own TopMetal1 stops at y -85.3), so
# routing on TopMetal1 down here does not touch the spiral.

def cap_plates(inst):
    """Top plate (TopMetal1) and bottom plate (Metal5) of a cmim, in top
    coordinates."""
    tp = [sh.dbbox().transformed(inst.dcplx_trans)
          for sh in layout.cell(inst.cell_index).shapes(LI["TM1"]).each()]
    bp = [sh.dbbox().transformed(inst.dcplx_trans)
          for sh in layout.cell(inst.cell_index).shapes(LI["M5"]).each()]
    return tp[0], bp[0]

BANKY = [-108.0, -130.0]
for i, yb in enumerate(BANKY):
    ca = find("cmim", x=-14.0, y=yb)
    cb = find("cmim", x=14.0, y=yb)
    sw = find("nmos", x=0.0, y=yb, wmin=None)
    if not (ca and cb and sw):
        print(f"  branch {i}: device missing, skipped")
        continue
    ta, ba = cap_plates(ca)
    tb, bb_ = cap_plates(cb)
    sp = pins(sw, 8, 2)
    src, drn = sp[0], sp[1]

    # Tank side: outp (Metal3) to CBxA top plate, outn (Metal4) to CBxB.
    drop(ta.center().x, ta.center().y, "TM1")
    path("M3", [(-16.0, -105.0), (-16.0, ta.center().y),
                (ta.center().x, ta.center().y)])
    drop(tb.center().x, tb.center().y, "TM1")
    path("M4", [(16.0, -109.0), (16.0, tb.center().y),
                (tb.center().x, tb.center().y)])

    # Switch side: bottom plates out to +/-6 on Metal5, then down to the
    # switch pins. Clear of the tail net at x = 0.
    for plate, pin, xj in ((ba, src, -6.0), (bb_, drn, 6.0)):
        path("M5", [(plate.center().x, plate.center().y),
                    (xj, plate.center().y),
                    (xj, pin.center().y),
                    (pin.center().x, pin.center().y)])
        drop(pin.center().x, pin.center().y, "M5")
    print(f"  branch {i} at y {yb}: caps ({ta.center().x:+.1f},"
          f"{tb.center().x:+.1f}) switch pins ({src.center().x:+.2f},"
          f"{drn.center().x:+.2f})")

'''

s = s.replace('layout.write(OUT)', new + 'layout.write(OUT)')

# extend the probe set so the bank appears in the extraction report
s = s.replace('''    "XMT2_D": (d.center().x, d.center().y, "M1"),
})''',
'''    "XMT2_D": (d.center().x, d.center().y, "M1"),
    "CB0A_top": (-14.0, -108.0, "TM1"), "CB0B_top": (14.0, -108.0, "TM1"),
    "CB1A_top": (-14.0, -130.0, "TM1"), "CB1B_top": (14.0, -130.0, "TM1"),
})''')

s = s.replace('''want = [{"XQ1_C", "XQ2_B"}, {"XQ2_C", "XQ1_B"},
        {"XQ1_E", "XQ2_E", "XMT2_D"}]''',
'''want = [{"XQ1_C", "XQ2_B", "CB0A_top", "CB1A_top"},
        {"XQ2_C", "XQ1_B", "CB0B_top", "CB1B_top"},
        {"XQ1_E", "XQ2_E", "XMT2_D"}]''')

p.write_text(s)
print("bank branches added")
