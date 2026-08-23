import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib = pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()

print("=== guardRingType choices ===")
for p in L.pcell_declaration("nmos").get_parameters():
    if p.name=="guardRingType":
        print("  default:", p.default, " choices:", getattr(p,"choices",None))

print("\n=== nmos footprint vs w and ng ===")
ly=pya.Layout(); pid=L.pcell_id("nmos")
for w,ng in [("4u",1),("16u",1),("16u",4),("70u",1),("70u",10),
             ("139u",1),("139u",10),("139u",20)]:
    ci=ly.add_pcell_variant(lib,pid,{"w":w,"l":"1u","ng":str(ng),"m":"1"})
    b=ly.cell(ci).dbbox()
    print(f"  w={w:6} ng={ng:3}  {b.width():7.2f} x {b.height():7.2f}")
