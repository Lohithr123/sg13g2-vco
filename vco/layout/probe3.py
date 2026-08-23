import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
ly=pya.Layout(); pid=L.pcell_id("nmos")
for lbl,w,ng in [("XSW0","4u",1),("XSW1","8u",2),("XSW2","16u",4),("XSW3","32u",8),
                 ("XMR","10u",2),("XMT","70u",10),("XMB","139u",20)]:
    ci=ly.add_pcell_variant(lib,pid,{"w":w,"l":"1u","ng":str(ng),"m":"1"})
    b=ly.cell(ci).dbbox()
    print(f"{lbl:5} w={w:6} ng={ng:3} -> {b.width():7.2f} x {b.height():6.2f}")
