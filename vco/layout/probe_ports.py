import pya
ly=pya.Layout(); ly.read("vco_20g_routed.gds")
top=ly.top_cell()
L={"M1":(8,0),"M2":(10,0),"M5":(67,0),"TM1":(126,0),"TM2":(134,0)}
P=[("vcc","TM2",0.0,-160.0),("gnd","TM1",0.0,-300.0),
   ("vg","M2",-120.0,-150.0),("vt","M2",-20.0,-155.0),
   ("nb0","M2",-38.0,-145.0),("nb1","M2",-33.0,-145.0),
   ("outbp","M5",-145.0,-95.23),("outbn","M5",145.0,-95.23)]
flat=ly.create_cell("_f"); flat.copy_tree(top)
for nm,lyr,x,y in P:
    r=pya.Region(flat.begin_shapes_rec(ly.layer(*L[lyr])))
    hit=r.interacting(pya.Region(pya.DBox(x-0.05,y-0.05,x+0.05,y+0.05).to_itype(ly.dbu)))
    print(f"  {nm:6} {lyr:4} ({x:7.1f},{y:8.2f})  "
          f"{'ON METAL' if hit.count() else 'NOT on metal'}")
