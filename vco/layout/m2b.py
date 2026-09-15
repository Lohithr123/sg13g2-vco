# Locate every M2.b violation and identify, for each, which two shapes are too
# close and where each came from — the top cell (my routing) or a PCell.
#
# M2.b is minimum Metal2 space or notch, 0.21 um.

import xml.etree.ElementTree as ET
import glob
import re
import pya

db = sorted(glob.glob('/tmp/l1/*_full.lyrdb'))
if not db:
    db = sorted(glob.glob('/tmp/l1/*_full.lyrdb'))
root = ET.parse(db[0]).getroot()

pts = []
for item in root.iter('item'):
    cat = (item.findtext('category') or '').strip("'")
    if cat != 'M2.b':
        continue
    txt = ' '.join(x.text or '' for x in item.find('values'))
    nums = [float(v) for v in re.findall(r'-?\d+\.?\d*', txt)]
    if len(nums) >= 4:
        pts.append((sum(nums[0::2]) / len(nums[0::2]),
                    sum(nums[1::2]) / len(nums[1::2])))

print(f"{len(pts)} M2.b violation(s)")

ly = pya.Layout(); ly.read("/foss/designs/vco/layout/vco_20g_routed.gds")
top = ly.top_cell()
m2 = ly.layer(10, 0)

for cx, cy in pts[:6]:
    print(f"\n--- violation near ({cx:.3f}, {cy:.3f}) ---")
    W = pya.DBox(cx - 1.2, cy - 1.2, cx + 1.2, cy + 1.2)
    wr = pya.Region(W.to_itype(ly.dbu))

    mine = pya.Region(top.shapes(m2)) & wr
    print(f"  drawn by me: {mine.count()}")
    for p in mine.each():
        b = p.bbox().to_dtype(ly.dbu)
        print(f"     x {b.left:9.3f}..{b.right:9.3f}  y {b.bottom:9.3f}..{b.top:9.3f}")

    for inst in top.each_inst():
        if not inst.dbbox().overlaps(W):
            continue
        cell = ly.cell(inst.cell_index)
        for sh in cell.shapes(m2).each():
            b = sh.dbbox().transformed(inst.dcplx_trans)
            if not b.overlaps(W):
                continue
            print(f"     [{cell.name}] x {b.left:9.3f}..{b.right:9.3f}  "
                  f"y {b.bottom:9.3f}..{b.top:9.3f}")
