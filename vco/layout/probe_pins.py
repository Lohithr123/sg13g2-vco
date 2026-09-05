import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
ly=pya.Layout(); ly.dbu=0.001

def dump(name, params):
    ci=ly.add_pcell_variant(lib, L.pcell_id(name), params)
    c=ly.cell(ci)
    print(f"\n=== {name}  bbox {c.dbbox().to_s()} ===")
    for li in ly.layer_indexes():
        info=ly.get_info(li)
        r=pya.Region(c.shapes(li))
        if r.is_empty(): continue
        b=r.bbox().to_dtype(ly.dbu)
        print(f"  {info.layer:3d}/{info.datatype:<3d} {r.count():3d} shapes  "
              f"x {b.left:8.2f}..{b.right:8.2f}   y {b.bottom:8.2f}..{b.top:8.2f}")

dump("npn13G2", {"Nx":1,"Ny":1})
dump("cmim", {"Calculate":"w&l","C":"10f"})
dump("nmos", {"w":"8u","l":"0.13u","ng":"2","m":"1","guardRingType":"psub"})
