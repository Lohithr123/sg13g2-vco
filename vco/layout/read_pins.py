import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
ly=pya.Layout(); ly.dbu=0.001

def pins(name, params):
    ci=ly.add_pcell_variant(lib, L.pcell_id(name), params)
    c=ly.cell(ci)
    print(f"\n=== {name}  bbox {c.dbbox().to_s()} ===")
    for li in ly.layer_indexes():
        i=ly.get_info(li)
        for sh in c.shapes(li).each():
            if sh.is_text():
                print(f"  {i.layer}/{i.datatype:<3} TEXT '{sh.text.string}' at "
                      f"{sh.text.x*ly.dbu:8.2f},{sh.text.y*ly.dbu:8.2f}")

pins("nmos", {"w":"70u","l":"1u","ng":"10","m":"1","guardRingType":"psub"})
pins("npn13G2", {"Nx":1,"Ny":1})
pins("cmim", {"Calculate":"w&l","C":"10f"})
pins("rhigh", {"Calculate":"l","R":"100k","w":"1u"})
pins("SVaricap", {"w":"3.74u","l":"0.3u","Nx":4})
