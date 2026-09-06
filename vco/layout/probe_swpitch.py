import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
ly=pya.Layout(); ly.dbu=0.001
for w,ng in [("8u","2"),("8u","1"),("16u","4"),("16u","2"),("16u","1")]:
    ci=ly.add_pcell_variant(lib,L.pcell_id("nmos"),
        {"w":w,"l":"0.13u","ng":ng,"m":"1","guardRingType":"psub"})
    c=ly.cell(ci)
    pins=sorted([sh.dbbox() for sh in c.shapes(ly.layer(8,2)).each()],
                key=lambda b:b.left)
    gap = pins[1].left-pins[0].right if len(pins)>1 else 0
    print(f"  w={w:5} ng={ng}: {c.dbbox().width():6.2f} x {c.dbbox().height():5.2f}"
          f"  {len(pins)} pins, gap {gap:.2f} um")
