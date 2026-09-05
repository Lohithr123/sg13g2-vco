import pya
ly=pya.Layout(); ly.read("vco_20g_routed.gds")
top=ly.top_cell()
rows={}
for inst in top.each_inst():
    nm=ly.cell(inst.cell_index).name
    if not nm.startswith("nmos"): continue
    b=inst.dbbox()
    rows.setdefault(round(b.center().y,1),[]).append(
        (round(b.center().x,1), nm, round(b.width(),2), round(b.height(),2)))
for y in sorted(rows, reverse=True):
    print(f"\ny = {y}")
    for x,nm,w,h in sorted(rows[y]):
        print(f"   x {x:+8.1f}  {nm:8}  {w:6.2f} x {h:5.2f}")
