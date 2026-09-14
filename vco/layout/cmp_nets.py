# Compare the schematic and layout sides of the LVS database device by device,
# rather than inferring from net-match counts.
#
# The extracted netlist is the layout's own circuit written in exactly the form
# the reader accepts, so it is the reference for how each device should be
# declared. Anything present on one side and absent on the other is a concrete,
# fixable difference.

import re
import pathlib

db = pathlib.Path("/tmp/ls2/vco_20g_routed.lvsdb").read_text()

def section(tag):
    i = db.index(f" X({tag}")
    j = db.index(" X(", i + 5)
    return db[i:j]

for side, tag in (("schematic", "VCO_20G"), ("layout", "vco_20g")):
    blk = section(tag)
    devs = re.findall(r"^  D\((\d+) (\S*)", blk, re.M)
    pins = re.findall(r"^  P\((\d+) I\((\w+)\)", blk, re.M)
    nets = re.findall(r"^  N\((\d+) I\((\w+)\)", blk, re.M)
    print(f"\n=== {side} ===")
    print(f"  {len(devs)} devices, {len(pins)} pins, {len(nets)} named nets")
    if pins:
        print("  pins:", ", ".join(p[1] for p in pins))
    from collections import Counter
    print("  device classes:", dict(Counter(d[1] for d in devs)))
