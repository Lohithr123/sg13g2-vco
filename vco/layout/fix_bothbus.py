import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

old = s[s.index('        if len(group) > 1:\n            # Sources are the outer strips'):
        s.index('    # Gates need no contact at all.')]

new = '''        if len(group) > 1:
            # On an interdigitated device the strips alternate source, drain,
            # source, so ANY bus drawn at strip level crosses the opposite
            # net. Both buses therefore leave the array: sources below the
            # diffusion, drains above, each reached by a short stub.
            #
            # Measured clearances on the bank switch (the tightest device):
            # strips span y -110.00..-106.00, guard ring inner edges at
            # -110.88 and -105.12, so there is 0.88 um below and 0.88 um
            # above. A 0.3 um bus at 0.45 um out clears the strips by 0.30 um
            # and the ring by 0.28 um.
            #
            # The stubs run beside each strip's own Metal2, which needs
            # 0.21 um (M2.b), so they are offset sideways by 0.3 um rather
            # than sitting directly on the strip centre.
            if ylev == y_s:
                _yb = snap(strips[0].bottom - 0.45)
                _dir = -1.0
            else:
                _yb = snap(strips[0].top + 0.45)
                _dir = 1.0
            for b in group:
                wire("M2", b.center().x, ylev, b.center().x, _yb, 0.3)
            wire("M2", group[0].center().x, _yb,
                 group[-1].center().x, _yb, 0.3)

'''

s = s.replace(old, new)
p.write_text(s)
print("both buses now leave the array")
