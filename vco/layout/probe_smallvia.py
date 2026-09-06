import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
print("via_stack parameters:")
for p in L.pcell_declaration("via_stack").get_parameters():
    print(f"  {p.name:14} {p.default!r}")
ly=pya.Layout(); ly.dbu=0.001
pid=L.pcell_id("via_stack")
for c,r in [(1,1),(1,2),(2,1)]:
    ci=ly.add_pcell_variant(lib,pid,{"b_layer":"Metal1","t_layer":"Metal3",
                                     "vn_columns":c,"vn_rows":r})
    b=ly.cell(ci).dbbox()
    print(f"  cols={c} rows={r}: {b.width():.3f} x {b.height():.3f}")
