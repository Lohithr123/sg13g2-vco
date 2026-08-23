import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
ly=pya.Layout(); pid=L.pcell_id("nmos")
print("finding max width per finger (l=1u):")
for wf in ["5u","6u","7u","8u","9u","10u"]:
    ci=ly.add_pcell_variant(lib,pid,{"w":wf,"l":"1u","ng":"1","m":"1"})
    b=ly.cell(ci).dbbox()
    ok = b.height() > 1.0
    print(f"  w/finger={wf:5}  {b.width():6.2f} x {b.height():6.2f}  {'ok' if ok else 'REJECTED'}")
print("\nfinal sizings:")
for lbl,w,ng in [("XSW0","4u",1),("XSW1","4u",2),("XSW2","4u",4),("XSW3","4u",8),
                 ("XMR","5u",2),("XMT","7u",10),("XMB","6.95u",20)]:
    ci=ly.add_pcell_variant(lib,pid,{"w":w,"l":"1u","ng":str(ng),"m":"1"})
    b=ly.cell(ci).dbbox()
    print(f"  {lbl:5} w={w:7} ng={ng:3} -> {b.width():7.2f} x {b.height():6.2f}")
