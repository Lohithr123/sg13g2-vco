# Read the newest DRC database in a given directory and report counts and
# locations. Takes the directory as an argument so it never reads a stale file
# — the hard-coded path in the earlier script is what produced numbers from
# hours ago and sent me chasing violations that had already been fixed.

import xml.etree.ElementTree as ET
import glob
import os
import re
import sys
from collections import Counter

d = sys.argv[1] if len(sys.argv) > 1 else "/tmp/x1"
files = glob.glob(os.path.join(d, "*_full.lyrdb"))
if not files:
    print(f"no DRC database in {d}")
    raise SystemExit

f = max(files, key=os.path.getmtime)
root = ET.parse(f).getroot()

c = Counter()
rows = []
for item in root.iter('item'):
    cat = (item.findtext('category') or '').strip("'")
    c[cat] += 1
    txt = ' '.join(x.text or '' for x in item.find('values'))
    nums = [float(v) for v in re.findall(r'-?\d+\.\d+', txt)]
    if len(nums) >= 4:
        rows.append((cat, (nums[0] + nums[2]) / 2, (nums[1] + nums[3]) / 2))

total = sum(c.values())
print(f"{total} violation(s) in {os.path.basename(f)}")
for k, n in c.most_common():
    print(f"  {n:5d}  {k}")

if rows:
    print("\nlocations (first 10):")
    for cat, x, y in rows[:10]:
        print(f"  {cat:8} ({x:9.3f},{y:10.3f})")
