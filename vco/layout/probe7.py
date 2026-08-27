import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
for g in ["none","psub"]:
    ly=pya.Layout(); ly.dbu=0.001
    top=ly.create_cell("t")
    ci=ly.add_pcell_variant(lib, L.pcell_id("nmos"),
                            {"w":"4u","l":"0.13u","ng":"1","m":"1","guardRingType":g})
    top.insert(pya.DCellInstArray(ci, pya.DTrans(0.0,0.0)))
    ly.write(f"/tmp/one_{g}.gds")
    print("wrote", f"/tmp/one_{g}.gds")
