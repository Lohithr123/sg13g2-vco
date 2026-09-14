import pathlib
p = pathlib.Path('route_v2.py')
s = p.read_text()
# Checked before changing: the 1.18 um band below the strips holds the guard
# ring bar and its corners on Metal1, plus a Metal5 terminal route — so a
# Metal1 bus there would short every source to ground, which is what happened
# when this was tried before.
#
# Metal2 in that band is empty. Drop the source bus one layer and route it
# below the device, where it crosses nothing: the pads already carry each
# source strip up to Metal2, so only the connecting bar moves.
old = '''    for group, ylev in ((src, y_s), (drn, y_d)):'''
new = '''    # Sources bus below the device on Metal2 (empty there), drains above.
    # A bus drawn across the array would pass over the opposite net's strips.
    y_s = snap(strips[0].bottom - 0.55)
    for group, ylev in ((src, y_s), (drn, y_d)):'''
assert s.count(old) == 1
s = s.replace(old, new)
p.write_text(s)
print("source bus moved below the device on Metal2")
