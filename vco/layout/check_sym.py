import pya, collections
ly=pya.Layout(); ly.read("vco_20g.gds")
top=ly.top_cell()
rows=collections.defaultdict(list)
for inst in top.each_inst():
    b=inst.dbbox()
    rows[round(b.center().y,1)].append((round(b.center().x,2),
                                        ly.cell(inst.cell_index).name))
print("rows NOT mirror-symmetric about x=0:")
bad=0
for y in sorted(rows, reverse=True):
    xs=sorted(x for x,_ in rows[y])
    if len(xs)==1 and abs(xs[0])<0.01: continue
    paired=all(any(abs(a+b)<0.05 for b in xs) for a in xs)
    if not paired:
        print(f"  y={y:9.1f}  x = {xs}")
        bad+=1
print(f"\n{bad} asymmetric row(s)")
