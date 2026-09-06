import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
ly=pya.Layout(); ly.dbu=0.001
pid=L.pcell_id("via_stack")
for b,t in [("Metal1","Metal2"),("Metal1","Metal3"),("Metal1","Metal4"),
            ("Metal1","Metal5"),("Metal1","TopMetal1"),("Metal1","TopMetal2")]:
    try:
        ci=ly.add_pcell_variant(lib,pid,{"b_layer":b,"t_layer":t})
        c=ly.cell(ci); bb=c.dbbox()
        lays=[]
        for li in ly.layer_indexes():
            i=ly.get_info(li)
            if len(list(c.shapes(li).each())): lays.append(f"{i.layer}/{i.datatype}")
        print(f"  {b}->{t:10} {bb.width():5.2f} x {bb.height():5.2f}  layers: {' '.join(lays)}")
    except Exception as e:
        print(f"  {b}->{t:10} FAILED: {e}")
