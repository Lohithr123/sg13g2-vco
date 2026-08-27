import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()

# bare npn, then npn with a ptap1 at increasing distance
for d in [None, 2.0, 4.0, 6.0]:
    ly=pya.Layout(); ly.dbu=0.001
    top=ly.create_cell("t")
    q=ly.add_pcell_variant(lib, L.pcell_id("npn13G2"), {"Nx":1,"Ny":1})
    top.insert(pya.DCellInstArray(q, pya.DTrans(0.0,0.0)))
    tag = "bare"
    if d is not None:
        t=ly.add_pcell_variant(lib, L.pcell_id("ptap1"), {})
        for dx,dy in [(-d,0.0),(d,0.0),(0.0,-d),(0.0,d)]:
            top.insert(pya.DCellInstArray(t, pya.DTrans(dx,dy)))
        tag = f"tap{d:g}"
    ly.write(f"/tmp/npn_{tag}.gds")
    print("wrote", tag)
