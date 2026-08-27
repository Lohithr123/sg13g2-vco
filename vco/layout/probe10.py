import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
IND="/foss/designs/inductor_synth/inductor3_snapped.gds"
src=pya.Layout(); src.read(IND)
print("inductor bbox:", src.top_cell().dbbox())
for y in [-75.0, -95.0, -110.0, -130.0]:
    ly=pya.Layout(); ly.dbu=0.001
    top=ly.create_cell("t")
    d=ly.create_cell(src.top_cell().name); d.copy_tree(src.top_cell())
    top.insert(pya.DCellInstArray(d.cell_index(), pya.DTrans(0.0,0.0)))
    q=ly.add_pcell_variant(lib, L.pcell_id("npn13G2"), {"Nx":1,"Ny":1})
    top.insert(pya.DCellInstArray(q, pya.DTrans(-15.0,y)))
    top.insert(pya.DCellInstArray(q, pya.DTrans(pya.DTrans.M90, 15.0,y)))
    ly.write(f"/tmp/y{abs(int(y))}.gds")
    print("wrote", y)
