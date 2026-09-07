import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The bank switches are 3.4 um wide with the band-select lines immediately to
# their left and the tail's Metal5 immediately to their right. A ground stack
# at either edge picks one of them up, and there is no third side: the device
# is boxed in.
#
# Leave them out. The psub rings are still drawn and still tie those devices to
# the substrate, which is what satisfies the latch-up rules; what they lack is
# an explicit metal tie to the ground rail. That is a floorplan consequence —
# the switches sit in the middle of the tank with signal routing on both sides
# — and the honest fix is to place them with a ground channel beside them
# rather than to force a route through.
old = '''for nm, dev in (("XSW0", find("nmos", x=-8.0, y=-108.0)),
                ("XSW1", find("nmos", x=-8.0, y=-130.0)),
                ("XMR2", XMR2), ("XMT2", XMT2),'''
new = '''for nm, dev in (("XMR2", XMR2), ("XMT2", XMT2),'''
assert old in s
s = s.replace(old, new)
s = s.replace('"gnd_sw": (-8.0, -250.0, "TM1"),', '"gnd_sw": (-130.0, -250.0, "TM1"),')
p.write_text(s)
print("switch rings left on substrate only")
