import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
d=L.pcell_declaration("nmos")
for p in d.get_parameters():
    if p.name in ("guardRingType","guardRingDistance"):
        print(p.name, "type:", p.type, "default:", repr(p.default))
        for a in ("choices","choice_values","choice_descriptions"):
            print("   ", a, getattr(p, a, "n/a"))
ly=pya.Layout(); pid=L.pcell_id("nmos")
for g in ["none","full","ptap","sub","p","ring","PTAP"]:
    try:
        ci=ly.add_pcell_variant(lib,pid,{"w":"4u","l":"1u","ng":"1","guardRingType":g})
        b=ly.cell(ci).dbbox()
        print(f"  guardRingType={g:6} -> {b.width():6.2f} x {b.height():6.2f}")
    except Exception as e:
        print(f"  guardRingType={g:6} -> {e}")
