import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

old = '''    path("M4", [(16.0, -109.0), (16.0, tb.center().y),
                (bb_.center().x, tb.center().y)])'''

new = '''    # MEASURED: this route drew Metal4 at y -109.5..-108.5 running from
    # x -9.700 to +16.000, straight across XSW0 whose strips span y -110..-106
    # at x -8.51 and -8.00. Both switch stacks reach Metal4 on their way to
    # Metal5, so the route shorted the switch's source to its drain — the last
    # of the four drain-source shorts, and present since the bank was first
    # wired, long before any finger commoning.
    #
    # The capacitors sit at x +/-25 and the switch at x -8, so the horizontal
    # leg has to pass the switch's column. Move it out of the device's row
    # instead: the strips end at y -106.0, so routing at the capacitor's own y
    # minus a clear 6 um puts it below the device entirely.
    _ybr = tb.center().y - 6.0
    path("M4", [(16.0, -109.0), (16.0, _ybr),
                (bb_.center().x, _ybr),
                (bb_.center().x, tb.center().y)])'''

assert s.count(old) == 1, f"matched {s.count(old)}"
s = s.replace(old, new)
p.write_text(s)
print("outn's bank leg routed clear of the switch row")
