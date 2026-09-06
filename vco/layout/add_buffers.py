import pathlib
p = pathlib.Path('route_v2.py'); s = p.read_text()

new = '''
print("\\n=== buffers ===")
# Emitter followers off each tank node. Base to the tank, collector to Vcc,
# emitter to the output and down to its own current mirror.
#
# The terminal pitch is the same trap as the cross-coupled pair: C at
# y -93.99, E at -95.23, B at -96.37, so 1.14 um apart, with the emitter's own
# Metal2 spanning the whole gap. Nothing can be routed laterally on Metal1 or
# Metal2 near the device. Via stacks land ON each terminal, offset sideways
# within its own metal to clear the device's internal via column, and every
# run happens on an upper layer.
#
# The terminals here are 3.7 um wide against the cross-coupled pair's 1.86, so
# there is more room to place the stack.

XB1 = find("npn13G2", x=-115.0, y=-95.0)
XB2 = find("npn13G2", x=115.0, y=-95.0)
XMB1A = find("nmos", x=-95.0, y=-282.0, wmin=20)
XMB2A = find("nmos", x=-130.0, y=-282.0, wmin=20)
XMB1B = find("nmos", x=95.0, y=-282.0, wmin=20)
XMB2B = find("nmos", x=130.0, y=-282.0, wmin=20)
for nm, o in [("XB1", XB1), ("XB2", XB2), ("XMB1A", XMB1A),
              ("XMB2A", XMB2A), ("XMB1B", XMB1B), ("XMB2B", XMB2B)]:
    print(f"  {nm:6} {'ok' if o else 'NOT FOUND'}")

if XB1 and XB2:
    bc1, bb1, be1 = label(XB1, "C"), label(XB1, "B"), label(XB1, "E")
    bc2, bb2, be2 = label(XB2, "C"), label(XB2, "B"), label(XB2, "E")

    # --- buffer inputs: tank nodes to the bases ---
    # outp is on Metal3, outn on Metal4, so each base takes its own net's
    # layer and the two never share a plane.
    drop(bb1.x - 1.2, bb1.y, "M3")
    path("M3", [(-16.0, -105.0), (-40.0, -105.0), (-40.0, bb1.y),
                (bb1.x - 1.2, bb1.y)])

    drop(bb2.x + 1.2, bb2.y, "M4")
    path("M4", [(16.0, -109.0), (40.0, -109.0), (40.0, bb2.y),
                (bb2.x + 1.2, bb2.y)])

    # --- buffer emitters: out to the die edge on Metal5 ---
    # The emitter already has Metal2 inside the cell, so the stack starts
    # there and never drives a second Via1 array into the device.
    drop(be1.x - 1.2, be1.y, "M5", frm="Metal2")
    path("M5", [(be1.x - 1.2, be1.y), (-145.0, be1.y)])

    drop(be2.x + 1.2, be2.y, "M5", frm="Metal2")
    path("M5", [(be2.x + 1.2, be2.y), (145.0, be2.y)])

    print(f"  XB1 C({bc1.x:.1f},{bc1.y:.1f}) B({bb1.x:.1f},{bb1.y:.1f}) "
          f"E({be1.x:.1f},{be1.y:.1f})")

'''

s = s.replace('layout.write(OUT)', new + 'layout.write(OUT)')

s = s.replace('''    "RB1_bot": (-45.0, -164.0, "M2"), "RB2_bot": (45.0, -164.0, "M2"),
})''',
'''    "RB1_bot": (-45.0, -164.0, "M2"), "RB2_bot": (45.0, -164.0, "M2"),
    "XB1_B": (-116.2, -96.37, "M1"), "XB2_B": (116.2, -96.37, "M1"),
    "XB1_E": (-116.2, -95.23, "M2"), "XB2_E": (116.2, -95.23, "M2"),
})''')

s = s.replace('''want = [{"XQ1_C", "XQ2_B", "CB0A_top", "CB1A_top", "CC1_top"},''',
'''want = [{"XQ1_C", "XQ2_B", "CB0A_top", "CB1A_top", "CC1_top", "XB1_B"},''')
s = s.replace('''        {"XQ2_C", "XQ1_B", "CB0B_top", "CB1B_top", "CC2_bot"},''',
'''        {"XQ2_C", "XQ1_B", "CB0B_top", "CB1B_top", "CC2_bot", "XB2_B"},''')
s = s.replace('''        {"XQ1_E", "XQ2_E", "XMT2_D"}]''',
'''        {"XQ1_E", "XQ2_E", "XMT2_D"}, {"XB1_E"}, {"XB2_E"}]''')

p.write_text(s)
print("buffer routing added")
