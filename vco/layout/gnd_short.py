import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The radial runs cross the whole die on TopMetal1 and collected Vcc, the tail
# and both control lines. Only the ring's own perimeter is genuinely clear.
#
# Ground points near the perimeter can reach it in a few microns; the ones deep
# in the interior cannot be connected without crossing something, and that is a
# floorplan problem rather than a routing one. Connect the reachable ones and
# report the rest, rather than dragging half the design onto ground.
old = '''    xside = -RX if gx < 0 else RX
    wire("TM1", gx, gy, xside, gy, 2.0)'''
new = '''    xside = -RX if gx < 0 else RX
    if abs(xside - gx) > 40.0:
        print(f"  {nm}: {abs(xside-gx):.0f} um from the ring, not routed")
        continue
    wire("TM1", gx, gy, xside, gy, 2.0)'''
assert old in s
s = s.replace(old, new)
p.write_text(s)
print("only near-perimeter points connected")
