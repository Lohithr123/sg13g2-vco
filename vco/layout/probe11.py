import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
for C in ["9f","10f","11f","12f","13f","14f","15f","16f"]:
    ly=pya.Layout(); ly.dbu=0.001
    top=ly.create_cell("t")
    ci=ly.add_pcell_variant(lib, L.pcell_id("cmim"), {"Calculate":"w&l","C":C})
    top.insert(pya.DCellInstArray(ci, pya.DTrans(0.0,0.0)))
    b=ly.cell(ci).dbbox()
    ly.write(f"/tmp/cap_{C}.gds")
    print(f"{C:8} {b.width():6.2f} x {b.height():6.2f}")
