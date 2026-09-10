import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()

# Every terminal connection currently lands on ONE diffusion strip, in the same
# 0.88 um gap the bus needs. Point them at the bus instead: the bus is the
# terminal now, and the gap holds only one thing.

# tail: XMT2 drain
s = s.replace('d = pins(XMT2, 8, 2)[1]',
              'd = busbox("XMT2", "d")')

# bank switches: source and drain
s = s.replace('''    sp = pins(sw, 8, 2)
    src, drn = sp[0], sp[1]''',
              '''    _tg = "XSW0" if abs(yb + 108.0) < 2.0 else "XSW1"
    src, drn = busbox(_tg, "s"), busbox(_tg, "d")''')

# buffer bias cascodes
s = s.replace('''        p2 = pins(mb2, 8, 2)           # cell-frame order: source, then drain
        s2, d2 = p2[0], p2[1]
        d1 = pins(mb1, 8, 2)[1]''',
              '''        _t2 = "XMB2A" if tag == "A" else "XMB2B"
        _t1 = "XMB1A" if tag == "A" else "XMB1B"
        s2, d2 = busbox(_t2, "s"), busbox(_t2, "d")
        d1 = busbox(_t1, "d")''')

# ground: lower mirror sources
s = s.replace('        src = pins(dev, 8, 2)[0]',
              '        src = busbox(nm, "s") if nm in BUS else pins(dev, 8, 2)[0]')

p.write_text(s)
print("terminal connections redirected to the buses")
