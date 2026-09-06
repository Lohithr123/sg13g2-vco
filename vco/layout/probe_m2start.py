import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
ly=pya.Layout(); ly.dbu=0.001
for b in ["Metal1","Metal2"]:
    ci=ly.add_pcell_variant(lib, L.pcell_id("via_stack"),
        {"b_layer":b,"t_layer":"Metal5","vn_columns":2,"vn_rows":1})
    c=ly.cell(ci); lays=[]
    for li in ly.layer_indexes():
        i=ly.get_info(li)
        if len(list(c.shapes(li).each())): lays.append(f"{i.layer}/{i.datatype}")
    print(f"  {b}->Metal5: {c.dbbox().width():.3f} x {c.dbbox().height():.3f}  {' '.join(lays)}")
