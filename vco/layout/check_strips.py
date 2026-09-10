import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
ly=pya.Layout(); ly.dbu=0.001
ci=ly.add_pcell_variant(lib, L.pcell_id("nmos"),
    {"w":"70u","l":"1u","ng":"10","m":"1","guardRingType":"psub"})
c=ly.cell(ci)
print("all Metal1 shapes, w<0.5 and h>2.0 (my filter):")
for sh in c.shapes(ly.layer(8,0)).each():
    b=sh.dbbox()
    hit = "KEPT" if (b.width()<0.5 and b.height()>2.0) else "    "
    print(f"  {hit}  x {b.left:7.2f}..{b.right:7.2f}  y {b.bottom:6.2f}..{b.top:6.2f}"
          f"  {b.width():.2f} x {b.height():.2f}")
