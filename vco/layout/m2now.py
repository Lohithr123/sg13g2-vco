# Where are the M2.a and M2.b violations now, and what are the exact numbers?
#
# M2.a is minimum width (0.21 um), M2.b minimum space or notch (0.21 um).
# Print the measured gap or width for each so the fix is arithmetic, not a
# nudge.

import xml.etree.ElementTree as ET
import glob
import re
from collections import Counter

root = ET.parse(sorted(glob.glob('/tmp/l5/*_full.lyrdb'))[0]).getroot()

c = Counter()
rows = []
for item in root.iter('item'):
    cat = (item.findtext('category') or '').strip("'")
    if not cat.startswith('M2.'):
        continue
    c[cat] += 1
    txt = ' '.join(x.text or '' for x in item.find('values'))
    nums = [float(v) for v in re.findall(r'-?\d+\.\d+', txt)]
    if len(nums) >= 8:
        # edge-pair: two edges, each x1,y1;x2,y2
        ax = (nums[0] + nums[2]) / 2
        ay = (nums[1] + nums[3]) / 2
        bx = (nums[4] + nums[6]) / 2
        by = (nums[5] + nums[7]) / 2
        gap = ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5
        rows.append((cat, ax, ay, gap))

for cat, n in c.most_common():
    print(f"{n:4d}  {cat}")

print("\nworst 12 by smallest gap:")
for cat, x, y, gap in sorted(rows, key=lambda r: r[3])[:12]:
    print(f"  {cat:6} at ({x:9.3f},{y:10.3f})   gap {gap*1000:6.0f} nm")

print("\ngrouped by region:")
reg = Counter()
for cat, x, y, gap in rows:
    if abs(x + 8) < 3:
        reg['bank switches (x -8)'] += 1
    elif abs(abs(x) - 130) < 8 or abs(abs(x) - 95) < 8:
        reg['buffer mirrors (x +/-95,130)'] += 1
    elif abs(abs(x) - 20) < 8 or abs(abs(x) - 26) < 8:
        reg['tail/ref mirrors (x +/-20,26)'] += 1
    else:
        reg[f'other (x~{x:.0f})'] += 1
for k, v in reg.most_common():
    print(f"  {v:4d}  {k}")
