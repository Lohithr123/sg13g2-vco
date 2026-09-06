import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
ly=pya.Layout(); ly.dbu=0.001
for c,r in [(1,1),(1,2),(1,4),(1,8)]:
    ci=ly.add_pcell_variant(lib,L.pcell_id("via_stack"),
        {"b_layer":"Metal1","t_layer":"Metal5","vn_columns":c,"vn_rows":r})
    b=ly.cell(ci).dbbox()
    print(f"  cols={c} rows={r}: {b.width():.3f} x {b.height():.3f}"
          f"  area {b.width()*b.height():.3f}")
