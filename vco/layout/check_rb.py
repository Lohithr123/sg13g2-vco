# Two findings from the first legible LVS comparison, both worth confirming
# before touching anything.
#
# 1. The extractor reports ONE resistor between G1 and G2, l=14.54u. The design
#    has TWO 10k resistors, each from a gate to the vg bias rail. A single
#    resistor at twice the length is those two in series — so the vg rail is
#    connecting them end to end rather than joining them at a common node.
#
#    That is electrically wrong: the gates would float relative to each other
#    rather than both sitting at mid-supply, which is the whole point of the
#    bias network. It is exactly the fault that gave 2.3% tuning in simulation
#    before the DC blocking was added.
#
# 2. RREF appears absent from the extracted resistors. Six real resistors were
#    found: four bleed at l=73.73u and two that sum to the gate bias. RREF is
#    a 10k in the reference branch and should appear at l=7.27u — and one does.
#    So RREF may be present and a bleed resistor missing instead.
#
# Print what the layout actually contains, by position, so the mapping is not
# guessed.

import pya

ly = pya.Layout()
ly.read("/foss/designs/vco/layout/vco_20g.gds")
top = ly.top_cell()

print("rhigh instances in the layout:")
for inst in top.each_inst():
    nm = ly.cell(inst.cell_index).name
    if not nm.startswith("rhigh"):
        continue
    b = inst.dbbox()
    print(f"  {nm:10} centre ({b.center().x:8.2f},{b.center().y:9.2f})  "
          f"{b.width():.2f} x {b.height():.2f}")
