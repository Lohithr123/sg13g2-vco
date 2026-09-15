# Establish the CURRENT state before changing anything else.
#
# My repeated failure has one cause: I edit against remembered output rather
# than measured. After the git restore, route_v2.py and the GDS are back to
# HEAD, and I do not actually know which revision that is or what it contains.
#
# Three questions, answered from the files themselves:
#   1. does route_v2.py contain the port-labelling block?
#   2. does the GDS on disk contain those labels?
#   3. therefore, do the two sides have a matching interface?

import pathlib
import pya

src = pathlib.Path('/foss/designs/vco/layout/route_v2.py').read_text()
print("route_v2.py:")
for marker, desc in [("=== port labels ===", "port labelling block"),
                     ("bus_fingers", "finger commoning"),
                     ("_TEXTLAYER", "text layer map"),
                     ("nm.upper()", "uppercase labels")]:
    print(f"   {desc:24} {'present' if marker in src else 'ABSENT'}")

ly = pya.Layout()
ly.read('/foss/designs/vco/layout/vco_20g_routed.gds')
top = ly.top_cell()

print("\nlabels in the GDS on disk:")
found = []
for lay, dt in [(8,25),(10,25),(30,25),(50,25),(67,25),(126,25),(134,25)]:
    it = top.begin_shapes_rec(ly.layer(lay, dt))
    while not it.at_end():
        sh = it.shape()
        if sh.is_text():
            t = it.trans() * sh.text
            found.append((f"{lay}/{dt}", t.string))
        it.next()
if found:
    for l, n in found:
        print(f"   {l:8} '{n}'")
else:
    print("   none — the GDS has no port labels")

print(f"\n{len(found)} port label(s) in the layout")
