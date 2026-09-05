import pya
ly=pya.Layout(); ly.read("vco_20g.gds")
top=ly.top_cell()
insts=[]
for inst in top.each_inst():
    insts.append((ly.cell(inst.cell_index).name, inst.dbbox()))
for i in range(len(insts)):
    for j in range(i+1, len(insts)):
        n1,b1=insts[i]; n2,b2=insts[j]
        if b1.overlaps(b2):
            print(f"  {n1:12} {b1.to_s()}")
            print(f"  {n2:12} {b2.to_s()}\n")
