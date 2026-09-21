import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

old = '''            _gy = snap(g.dbbox().top - 1.21 + 0.62)  # upper part, clear of the drain bar
            _x = snap(b.center().x)'''

new = '''            # MEASURED on XMT2: the commoning's drain bar spans x -25.400 to
            # -14.100, and the contact at the marked gate pin (x -20) lands on
            # it — which is why every cascode gate extracted shorted to its own
            # drain.
            #
            # But the leftmost gate is at x -26.36, outside the drain bar's
            # span: the bar runs between the inner strips while the first gate
            # sits left of them. The poly bar commons every gate, so contacting
            # the leftmost one carries the whole gate and touches nothing.
            _polys = sorted(
                (sh.dbbox().transformed(g.dcplx_trans)
                 for sh in layout.cell(g.cell_index).shapes(LI["poly"]).each()),
                key=lambda q: q.center().x)
            if not _polys:
                continue
            _gy = snap(g.dbbox().top - 1.21 + 0.41)
            _x = snap(_polys[0].center().x)'''

assert s.count(old) == 1, f"matched {s.count(old)}"
s = s.replace(old, new)
p.write_text(s)
print("gate contact moved to the leftmost gate, clear of the drain bar")
