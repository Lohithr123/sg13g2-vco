import re, pathlib, sys
db = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                  else "/tmp/pl4/vco_20g_routed.lvsdb").read_text()
i = db.index(" X(vco_20g VCO_20G")
blk = db[i:]
lay, sch = [], []
for m in re.finditer(r"^   N\(([^)]*)\)", blk, re.M):
    parts = m.group(1).split()
    if len(parts) >= 2:
        if parts[1] == "()":
            lay.append(parts[0])
        elif parts[0] == "()":
            sch.append(parts[1])
print(f"layout nets with no schematic match: {len(lay)}")
print("  ", ", ".join(lay[:20]))
print(f"schematic nets with no layout match: {len(sch)}")
print("  ", ", ".join(sch[:20]))
