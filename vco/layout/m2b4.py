import xml.etree.ElementTree as ET, glob, os, re
import pya

f = max(glob.glob('/tmp/safe/*_full.lyrdb'), key=os.path.getmtime)
root = ET.parse(f).getroot()
pts = []
for item in root.iter('item'):
    txt = ' '.join(x.text or '' for x in item.find('values'))
    n = [float(v) for v in re.findall(r'-?\d+\.\d+', txt)]
    if len(n) >= 8:
        pts.append(((n[0]+n[2]+n[4]+n[6])/4, (n[1]+n[3]+n[5]+n[7])/4))

ly = pya.Layout(); ly.read("vco_20g_routed.gds")
top = ly.top_cell()
m2 = ly.layer(10, 0)

for cx, cy in pts:
    print(f"\n=== violation at ({cx:.3f}, {cy:.3f}) ===")
    W = pya.DBox(cx-0.8, cy-0.8, cx+0.8, cy+0.8)
    wr = pya.Region(W.to_itype(ly.dbu))
    mine = pya.Region(top.shapes(m2)) & wr
    for p in sorted(mine.each(), key=lambda q: q.bbox().left):
        b = p.bbox().to_dtype(ly.dbu)
        print(f"   MINE  x {b.left:8.3f}..{b.right:8.3f}  y {b.bottom:9.3f}..{b.top:9.3f}")
    for inst in top.each_inst():
        if not inst.dbbox().overlaps(W): continue
        c = ly.cell(inst.cell_index)
        for sh in c.shapes(m2).each():
            b = sh.dbbox().transformed(inst.dcplx_trans)
            if b.overlaps(W):
                print(f"   [{c.name}] x {b.left:8.3f}..{b.right:8.3f}  y {b.bottom:9.3f}..{b.top:9.3f}")
