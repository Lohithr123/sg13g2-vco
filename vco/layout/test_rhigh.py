import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
for mir in (False, True):
    ly=pya.Layout(); ly.dbu=0.001
    top=ly.create_cell("t")
    ci=ly.add_pcell_variant(lib, L.pcell_id("rhigh"),
                            {"Calculate":"l","R":"10k","w":"1u"})
    t = pya.DTrans(pya.DTrans.M90,0.0,0.0) if mir else pya.DTrans(0.0,0.0)
    top.insert(pya.DCellInstArray(ci, t))
    ly.write(f"/tmp/rh_{'mir' if mir else 'nom'}.gds")
    print("wrote", "mirrored" if mir else "normal")
