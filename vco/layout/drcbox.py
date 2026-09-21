import pya, glob, os
from collections import defaultdict
f = max(glob.glob('/tmp/aa1/*_full.lyrdb'), key=os.path.getmtime)
rdb = pya.ReportDatabase("")
rdb.load(f)
g = defaultdict(list)
for cat in rdb.each_category():
    for item in rdb.each_item_per_category(cat.rdb_id()):
        for v in item.each_value():
            b = None
            if v.is_box(): b = v.box()
            elif v.is_polygon(): b = v.polygon().bbox()
            elif v.is_edge_pair(): b = v.edge_pair().bbox()
            elif v.is_edge(): b = v.edge().bbox()
            if b:
                g[cat.name()].append(b)
for cat, bs in sorted(g.items(), key=lambda kv: -len(kv[1])):
    print(f"\n{cat} ({len(bs)}):")
    for b in sorted(bs, key=lambda q: (q.center().y, q.center().x))[:12]:
        print(f"   x {b.left:8.2f}..{b.right:8.2f}  y {b.bottom:8.2f}..{b.top:8.2f}")
