import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# XSW1's pins are 0.35 um apart and the minimum Metal2 width is 0.21 um with
# 0.21 um spacing — so a stub beside one pin always touches the next. There is
# no geometry that commons this device's fingers without shorting it.
#
# Skip devices whose strip pitch cannot hold a track plus two clearances. The
# terminal routing already contacts one strip of each type; the remaining
# fingers stay unconnected, which is a real limitation of this floorplan and
# is recorded as such rather than papered over.
old = '''    src, drn = strips[0::2], strips[1::2]'''
new = '''    _pitch = (strips[1].center().x - strips[0].center().x
              if len(strips) > 1 else 1.38)
    if _pitch < 0.75:
        print(f"  {tag:8} pitch {_pitch:.2f} um too tight to common, skipped")
        return None

    src, drn = strips[0::2], strips[1::2]'''
assert s.count(old) == 1
s = s.replace(old, new)
p.write_text(s)
print("devices below 0.75 um pitch are skipped")
