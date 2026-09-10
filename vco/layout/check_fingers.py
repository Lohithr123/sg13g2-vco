import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
ly=pya.Layout(); ly.dbu=0.001
ci=ly.add_pcell_variant(lib, L.pcell_id("nmos"),
    {"w":"70u","l":"1u","ng":"10","m":"1","guardRingType":"psub"})
c=ly.cell(ci)
m1=pya.Region(c.shapes(ly.layer(8,0))).merged()
poly=pya.Region(c.shapes(ly.layer(5,0))).merged()
print(f"Metal1: {m1.count()} separate polygons after merging")
print(f"GatPoly: {poly.count()} separate polygons after merging")
print("\nIf these are not 2-3 and 1, the fingers are not commoned by the PCell.")
