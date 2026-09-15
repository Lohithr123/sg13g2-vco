import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

old = '''        if len(group) > 1:
            wire("M2", group[0].center().x, ylev,
                 group[-1].center().x, ylev, 0.4)'''

new = '''        if len(group) > 1:
            # MEASURED on XSW0: the strips span y -110.00..-106.00, so a bus
            # at y_s = y0 + 0.12h sits at -109.52 and, 0.4 um wide, spans
            # -109.72..-109.32. The DRAIN strip's Metal2 runs -109.440..
            # -106.560. They overlap by 0.12 um, which is what shorts drain to
            # source on every device where the two levels are close enough.
            #
            # A bus drawn across the array always crosses the opposite net,
            # because the strips interdigitate. So the bus goes OUTSIDE the
            # strip span, and each strip reaches it by a stub at its own x —
            # and a stub at a source x never overlaps a drain strip's x, so
            # nothing crosses.
            #
            # Space available (measured): strip ends at -110.00, guard ring
            # Metal1 starts at -110.88, and Metal2 is empty in that 0.88 um
            # band. Same above, between -106.00 and -105.12.
            _out = (snap(strips[0].bottom - 0.45) if ylev == y_s
                    else snap(strips[0].top + 0.45))
            for b in group:
                wire("M2", b.center().x, ylev, b.center().x, _out, 0.26)
            wire("M2", group[0].center().x, _out,
                 group[-1].center().x, _out, 0.26)'''

assert s.count(old) == 1, f"matched {s.count(old)}"
s = s.replace(old, new)
p.write_text(s)
print("buses moved outside the strip span, stubs at each strip's own x")
