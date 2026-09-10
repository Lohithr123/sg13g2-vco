import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# "narrow and tall" also describes the guard ring's vertical sides (0.30 x 8.76),
# and since they sit at the outermost x they were bussed as source fingers —
# tying every guard ring to its device's source. The real diffusion strips are
# exactly 0.16 wide and span the device's w in y, so filter on that instead.
old = '        if b.width() < 0.5 and b.height() > 2.0:'
new = '        if b.width() < 0.25 and b.height() > 2.0:'
assert old in s
s = s.replace(old, new)
p.write_text(s)
print("strip filter narrowed to exclude the guard ring")
