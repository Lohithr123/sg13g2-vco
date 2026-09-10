import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# The bank switch strips already carry a tall via stack from the terminal
# routing — cols=1 rows=8, 3.16 um on a 4 um strip. There is nowhere on that
# strip for a second via, and none is needed: the stack already takes the strip
# up to Metal2, so the bus only has to touch it.
#
# Skip the pad wherever an existing Via1 sits in its footprint.
old = '''        for b in group:
            x = b.center().x
            for lyr in ("M1", "M2"):'''
new = '''        _v1 = pya.Region(top.shapes(layout.layer(19, 0)))
        for b in group:
            x = b.center().x
            _foot = pya.Region(pya.DBox(x - PAD, ylev - PAD,
                                        x + PAD, ylev + PAD).to_itype(layout.dbu))
            if not (_v1 & _foot).is_empty():
                continue          # already contacted by the terminal routing
            for lyr in ("M1", "M2"):'''
assert old in s
s = s.replace(old, new)
p.write_text(s)
print("pads skipped where a terminal stack already contacts the strip")
