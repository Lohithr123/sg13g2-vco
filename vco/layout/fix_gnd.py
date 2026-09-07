import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()

old = '''    try:
        drop(gx, gy, "TM1", cols=1, rows=2)
    except Exception as exc:
        print(f"  {nm}: stack failed ({exc})")
        continue
    xout = -155.0 if gx < 0 else 155.0
    path("TM1", [(gx, gy), (gx, gy - 6.0), (xout, gy - 6.0),
                 (xout, GND_Y)], w=4.0)'''

new = '''    # A Metal1->TopMetal1 stack crosses Metal2 and Metal5 at every point it
    # touches, and with ten ground points that collected the tail and both
    # control lines. Rise to Metal2 at the device, run out sideways, and make
    # the jump to TopMetal1 at the die edge where nothing else is.
    try:
        drop(gx, gy, "M2", cols=1, rows=2)
    except Exception as exc:
        print(f"  {nm}: stack failed ({exc})")
        continue
    xout = -155.0 if gx < 0 else 155.0
    xedge = -150.0 if gx < 0 else 150.0
    path("M2", [(gx, gy), (gx, gy - 6.0), (xedge, gy - 6.0)], w=1.0)
    drop(xedge, gy - 6.0, "TM1", frm="Metal2")
    path("TM1", [(xedge, gy - 6.0), (xout, gy - 6.0),
                 (xout, GND_Y)], w=4.0)'''

assert old in s, "ground block not found in the expected form"
s = s.replace(old, new)
p.write_text(s)
print("ground rises to TopMetal1 at the die edge")
