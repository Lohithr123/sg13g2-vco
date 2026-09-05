import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
ly=pya.Layout(); ly.dbu=0.001
import sys
DEV=sys.argv[-1] if len(sys.argv)>1 else "npn13G2"
PAR={"npn13G2":{"Nx":1,"Ny":1},"cmim":{"Calculate":"w&l","C":"10f"},"nmos":{"w":"8u","l":"0.13u","ng":"2","m":"1","guardRingType":"psub"},"rhigh":{"Calculate":"l","R":"100k","w":"1u"},"SVaricap":{"w":"3.74u","l":"0.3u","Nx":4}}[DEV]
ci=ly.add_pcell_variant(lib, L.pcell_id(DEV), PAR)
c=ly.cell(ci)

NAMES={(1,0):"Activ",(5,0):"GatPoly",(6,0):"Cont",(7,0):"nSD",(8,0):"Metal1",
       (10,0):"Metal2",(14,0):"pSD",(19,0):"Via1",(26,0):"TRANS",(33,0):"EmWind",
       (51,0):"HeatTrans",(40,0):"Substrate",(1,20):"Activ.mask",(7,21):"nSD.block",
       (8,2):"Metal1.pin",(10,2):"Metal2.pin",(10,0):"Metal2"}

# the three Metal1 shapes
m1=ly.layer(8,0)
shapes=[sh.dbbox() for sh in c.shapes(m1).each()]
shapes.sort(key=lambda b: -b.top)

for i,b in enumerate(shapes):
    print(f"\n--- Metal1 shape {i}: x {b.left:6.2f}..{b.right:6.2f}  "
          f"y {b.bottom:6.2f}..{b.top:6.2f} ---")
    probe = pya.DBox(b.left, b.bottom, b.right, b.top)
    for (lay,dt),nm in sorted(NAMES.items()):
        li = ly.layer(lay,dt)
        r = pya.Region(c.shapes(li)) & pya.Region(probe.to_itype(ly.dbu))
        if not r.is_empty():
            ov = r.area()*ly.dbu*ly.dbu
            print(f"      overlaps {nm:12} ({lay}/{dt})  area {ov:.3f} um2")
