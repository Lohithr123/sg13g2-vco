# Copy the routed layout with the inductor removed, so a second extraction
# shows how much of the tank's capacitance is the spiral itself - which the
# EM model already includes and must not be counted twice.
#
#   klayout -z -r noind.py

import pya

SRC = "/foss/designs/vco/layout/vco_20g_routed.gds"
DST = "/foss/designs/vco/layout/pex/vco_noind.gds"

ly = pya.Layout()
ly.read(SRC)
top = ly.top_cell()

print("top-level instances larger than 80 um:")
victims = []
for inst in top.each_inst():
    b = inst.dbbox()
    name = ly.cell(inst.cell_index).name
    if max(b.width(), b.height()) > 80:
        print(f"   {name:30} x {b.left:8.1f}..{b.right:8.1f}  y {b.bottom:8.1f}..{b.top:8.1f}")
    if "ind" in name.lower():
        victims.append(inst)

if not victims:
    print("\nno instance with 'ind' in its cell name - nothing removed; check the list above")
else:
    for inst in victims:
        b = inst.dbbox()
        print(f"\nremoving {ly.cell(inst.cell_index).name} "
              f"at ({b.center().x:.1f}, {b.center().y:.1f})")
        inst.delete()
    ly.write(DST)
    print("wrote", DST)
