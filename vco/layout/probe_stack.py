import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib = pya.Library.library_by_name("SG13_dev", "sg13g2")
L = lib.layout()
print(f"{'cols':>4} {'rows':>4}  {'M2 width':>9} {'M2 height':>10}  legal?")
for cols in (1, 2, 3):
    for rows in (1, 2, 4, 8):
        ly = pya.Layout(); ly.dbu = 0.001
        ci = ly.add_pcell_variant(lib, L.pcell_id("via_stack"),
             {"b_layer": "Metal1", "t_layer": "Metal5",
              "vn_columns": cols, "vn_rows": rows})
        w = h = 0
        for sh in ly.cell(ci).shapes(ly.layer(10, 0)).each():
            b = sh.dbbox()
            w, h = b.width(), b.height()
        ok = "yes" if min(w, h) >= 0.21 else "NO"
        print(f"{cols:>4} {rows:>4}  {w:9.3f} {h:10.3f}  {ok}")
