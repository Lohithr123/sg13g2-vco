import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
ly=pya.Layout(); pid=L.pcell_id("nmos")
for g in ["none","psub"]:
    ci=ly.add_pcell_variant(lib,pid,{"w":"70u","l":"1u","ng":"10","m":"1","guardRingType":g})
    b=ly.cell(ci).dbbox()
    print(f"guardRingType={g:5} -> {b.width():7.2f} x {b.height():6.2f}")
