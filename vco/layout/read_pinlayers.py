import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
ly=pya.Layout(); ly.dbu=0.001
for nm,par in [("nmos",{"w":"70u","l":"1u","ng":"10","m":"1","guardRingType":"psub"}),
               ("cmim",{"Calculate":"w&l","C":"10f"}),
               ("rhigh",{"Calculate":"l","R":"100k","w":"1u"})]:
    ci=ly.add_pcell_variant(lib, L.pcell_id(nm), par)
    c=ly.cell(ci)
    print(f"\n=== {nm} ===")
    for lay,dt,t in [(8,2,"Metal1.pin"),(5,2,"GatPoly.pin"),(126,2,"TopMetal1.pin"),
                     (67,2,"Metal5.pin"),(10,2,"Metal2.pin")]:
        li=ly.layer(lay,dt)
        for sh in c.shapes(li).each():
            b=sh.dbbox()
            print(f"  {t:14} x {b.left:7.2f}..{b.right:7.2f}  y {b.bottom:7.2f}..{b.top:7.2f}")
