import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()

print("=== npn13G2 parameters ===")
for p in L.pcell_declaration("npn13G2").get_parameters():
    print(f"  {p.name:16} {p.default!r}")

print("\n=== ptap1 parameters ===")
d = L.pcell_declaration("ptap1")
if d is None:
    print("  no ptap1 PCell")
else:
    for p in d.get_parameters():
        print(f"  {p.name:16} {p.default!r}")
    ly=pya.Layout(); ci=ly.add_pcell_variant(lib, L.pcell_id("ptap1"), {})
    b=ly.cell(ci).dbbox()
    print(f"  default footprint: {b.width():.2f} x {b.height():.2f}")

print("\n=== guard_ring parameters ===")
d = L.pcell_declaration("guard_ring")
if d is None:
    print("  no guard_ring PCell")
else:
    for p in d.get_parameters():
        print(f"  {p.name:16} {p.default!r}")
