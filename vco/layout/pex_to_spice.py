# Back-annotate the kpex extraction into the ngspice testbench.
#
#   klayout -z -r pex_to_spice.py
#
# Writes, next to vco_2bit.spice:
#   pex_caps.inc        the extracted capacitors on simulation node names
#   vco_2bit_pex.spice  a copy of the testbench that includes them
#
# kpex names nets by layout id; its LVS database maps those to schematic nets
# (OUTP, G1, ...), and the table below maps schematic nets to the node names
# used in vco_2bit.spice (outp, gp, ...).
#
# Nets the testbench does not have - the mirror bias nodes (NC, NB, NTX ...)
# and any net kpex could not name - are treated as AC ground. The testbench
# models the tail as an ideal source, so those nodes do not exist in it, and
# they are all DC bias nodes. Grounding them slightly over-counts the tank
# load, so the resulting frequency shift is if anything pessimistic.

import collections
import gzip
import os
import re
import shutil
import pya

RUN = os.environ.get("RUN", "/foss/designs/vco/layout/pex/run2/vco_20g_routed__vco_20g")
CSV = os.path.join(RUN, "vco_20g_k25d_pex_netlist.csv")
TB = "/foss/designs/vco/vco_2bit.spice"
INC = "/foss/designs/vco/pex_caps.inc"
TB_PEX = "/foss/designs/vco/vco_2bit_pex.spice"

SIM = {
    "OUTP": "outp", "OUTN": "outn",
    "G1": "gp", "G2": "gn",
    "E": "e", "VCC": "vcc", "VG": "vg", "W": "vt",
    "S0A": "s0a", "S0B": "s0b", "S1A": "s1a", "S1B": "s1b",
    "NB0": "nb0", "NB1": "nb1",
    "OUTBP": "ep", "OUTBN": "en",
    "GND": "0", "VSUBS": "0",
}

# --- layout net -> schematic net ------------------------------------------
names = {}
tmp = "/tmp/kpex_xref.lvsdb"
with gzip.open(os.path.join(RUN, "vco_20g.lvsdb.gz"), "rb") as fi, open(tmp, "wb") as fo:
    shutil.copyfileobj(fi, fo)
lvs = pya.LayoutVsSchematic()
lvs.read(tmp)
xref = lvs.xref()
for cp in xref.each_circuit_pair():
    for np_ in xref.each_net_pair(cp):
        a, b = np_.first(), np_.second()
        if a and b:
            names[a.expanded_name()] = b.expanded_name().upper()

def node(n):
    sch = names.get(n, n).upper()
    if n in ("VSUBS", "gnd"):
        return "0"
    return SIM.get(sch, "0")

# --- merge capacitors onto simulation nodes --------------------------------
merged = collections.defaultdict(float)
dropped = 0.0
with open(CSV) as f:
    for line in f:
        p = [x for x in line.strip().split(";") if x != ""]
        if len(p) < 4 or not p[0].startswith("C"):
            continue
        try:
            v = float(p[3])
        except ValueError:
            continue
        a, b = node(p[1]), node(p[2])
        if a == b:
            dropped += v          # both ends on the same node: no effect
            continue
        merged[tuple(sorted((a, b)))] += v

with open(INC, "w") as f:
    f.write("* kpex 2.5D extracted capacitance, mapped to testbench nodes (fF)\n")
    f.write(f"* source: {CSV}\n")
    for i, ((a, b), v) in enumerate(sorted(merged.items(), key=lambda kv: -kv[1])):
        if v < 0.01:
            continue
        f.write(f"Cpex{i} {a} {b} {v:.3f}f\n")
print("wrote", INC)

print("\ncapacitance added, by node pair (fF):")
for (a, b), v in sorted(merged.items(), key=lambda kv: -kv[1])[:16]:
    print(f"   {v:8.3f}   {a:5} - {b}")
print(f"   ({dropped:.1f} fF dropped as same-node, e.g. bias nets to ground)")

# --- testbench copy with the include ---------------------------------------
src = open(TB).read().split("\n")
out, done = [], False
for line in src:
    if not done and re.match(r"^\s*\.(control|end)\b", line, re.I):
        out.append(".include pex_caps.inc")
        done = True
    out.append(line)
if not done:
    out.append(".include pex_caps.inc")
open(TB_PEX, "w").write("\n".join(out))
print("\nwrote", TB_PEX)
