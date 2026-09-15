# The "not matching any net" count is the number of LAYOUT nets. The layout has
# not changed, so that number cannot move no matter what I fix in the netlist.
# I have been steering by an instrument that reads constant.
#
# The real measure is the cross-reference: how many device and net PAIRS the
# comparison actually formed. In the lvsdb, entries are
#
#     D(layout_id schematic_id status)
#
# where a status of 1 with both ids present is a match, and an empty side is an
# unmatched device. Same for N(...) nets and P(...) pins.

import re
import pathlib
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/n5/vco_20g_routed.lvsdb"
db = pathlib.Path(path).read_text()

i = db.index(" X(vco_20g VCO_20G")
blk = db[i:]

def tally(letter):
    both = one = 0
    for m in re.finditer(rf"^   {letter}\(([^)]*)\)", blk, re.M):
        parts = m.group(1).split()
        if len(parts) >= 2 and parts[0] != "()" and parts[1] != "()":
            both += 1
        else:
            one += 1
    return both, one

for letter, name in (("D", "devices"), ("N", "nets"), ("P", "pins")):
    b, o = tally(letter)
    print(f"  {name:8}  matched pairs: {b:4d}   unmatched: {o:4d}")

print("\nfirst few log messages:")
for m in re.finditer(r"B\('([^']+)'\)", blk):
    print("   ", m.group(1)[:72])
