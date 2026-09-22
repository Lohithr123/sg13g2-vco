# Summarise a kpex 2.5D extraction per net, with schematic names.
#
#   klayout -z -r pex_summary.py
#
# kpex's CSV names nets by layout id ($I81 ...). Its own LVS database holds a
# cross-reference from each layout net to the schematic net it matched, so we
# use that to put real names (OUTP, OUTN, E, ...) on the numbers.

import collections
import glob
import gzip
import os
import shutil
import pya

RUN = os.environ.get("RUN", "/foss/designs/vco/layout/pex/run2/vco_20g_routed__vco_20g")
CSV = os.path.join(RUN, "vco_20g_k25d_pex_netlist.csv")

# --- layout net -> schematic net, from kpex's LVS database -----------------
names = {}
lvsdb_gz = os.path.join(RUN, "vco_20g.lvsdb.gz")
lvsdb = "/tmp/kpex_vco.lvsdb"
try:
    with gzip.open(lvsdb_gz, "rb") as fi, open(lvsdb, "wb") as fo:
        shutil.copyfileobj(fi, fo)
    lvs = pya.LayoutVsSchematic()
    lvs.read(lvsdb)
    xref = lvs.xref()
    for cp in xref.each_circuit_pair():
        for np_ in xref.each_net_pair(cp):
            a, b = np_.first(), np_.second()
            if a and b:
                names[a.expanded_name()] = b.expanded_name()
    print(f"cross-reference: {len(names)} layout nets named from the schematic")
except Exception as e:
    print("cross-reference unavailable:", e)

def nm(n):
    return f"{names[n]} ({n})" if n in names and names[n] != n else n

# --- read the extracted capacitances ---------------------------------------
pair = collections.defaultdict(float)
total = collections.defaultdict(float)
n_caps = 0
with open(CSV) as f:
    for line in f:
        parts = [p for p in line.strip().split(";") if p != ""]
        if len(parts) < 4 or not parts[0].startswith("C"):
            continue
        try:
            v = float(parts[3])
        except ValueError:
            continue
        a, b = parts[1], parts[2]
        pair[tuple(sorted((a, b)))] += v
        total[a] += v
        total[b] += v
        n_caps += 1
print(f"{n_caps} capacitors read (values in fF)\n")

print("=== total capacitance per net (largest first) ===")
for n, v in sorted(total.items(), key=lambda kv: -kv[1])[:20]:
    print(f"  {v:9.3f} fF   {nm(n)}")

# --- the tank ----------------------------------------------------------------
inv = {v.upper(): k for k, v in names.items()}
labels = ("OUTP", "OUTN", "G1", "G2")
tank = [inv.get(l) for l in labels]
print("\n=== tank nets and varactor gates ===")
for t, label in zip(tank, labels):
    if not t:
        print(f"  {label}: not found in the cross-reference")
        continue
    print(f"\n  {label} = {t}: total {total[t]:.3f} fF")
    rows = [(k, v) for k, v in pair.items() if t in k]
    for k, v in sorted(rows, key=lambda kv: -kv[1])[:10]:
        other = k[0] if k[1] == t else k[1]
        print(f"      {v:8.3f} fF  to {nm(other)}")

if all(tank[:2]):
    cc = pair.get(tuple(sorted(tank[:2])), 0.0)
    print(f"\n  OUTP-OUTN coupling: {cc:.3f} fF")
