import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
ly=pya.Layout(); ly.dbu=0.001
ci=ly.add_pcell_variant(lib, L.pcell_id("npn13G2"), {"Nx":1,"Ny":1})
c=ly.cell(ci)
for lay,dt,tag in [(8,0,"Metal1"),(8,2,"Metal1.pin"),(6,0,"Cont"),(8,1,"Metal1.label")]:
    li=ly.layer(lay,dt)
    print(f"\n{tag} ({lay}/{dt}):")
    for sh in c.shapes(li).each():
        if sh.is_text():
            print(f"   TEXT '{sh.text.string}' at {sh.text.x*ly.dbu:.2f},{sh.text.y*ly.dbu:.2f}")
        else:
            b=sh.dbbox()
            print(f"   box x {b.left:6.2f}..{b.right:6.2f}  y {b.bottom:6.2f}..{b.top:6.2f}")
