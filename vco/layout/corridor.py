import pya
ly = pya.Layout(); ly.read("vco_20g_routed.gds")
top = ly.top_cell()
LAY = {"M2":(10,0),"M3":(30,0),"M4":(50,0),"M5":(67,0),"TM1":(126,0),"TM2":(134,0)}
flat = {k: pya.Region(top.begin_shapes_rec(ly.layer(*v))).merged() for k,v in LAY.items()}
# For each layer and each side, find horizontal bands y where a 0.6 um track
# from the bleed column (x 150) to the switch-node tap (x 30) touches nothing.
for side, x0, x1 in (("left", -152.0, -24.0), ("right", 24.0, 152.0)):
    print(f"\n=== {side} side, x {x0:.0f}..{x1:.0f} ===")
    for k, reg in flat.items():
        clear = []
        y = -100.0
        while y > -285.0:
            box = pya.Region(pya.DBox(x0, y - 0.8, x1, y + 0.8).to_itype(ly.dbu))
            if (reg & box).is_empty():
                clear.append(round(y, 1))
            y -= 1.0
        # compress to ranges
        rng, start, prev = [], None, None
        for v in clear:
            if start is None: start = prev = v
            elif abs(v - prev) <= 1.01: prev = v
            else: rng.append((start, prev)); start = prev = v
        if start is not None: rng.append((start, prev))
        print(f"  {k:4}: clear bands {rng[:6]}")
