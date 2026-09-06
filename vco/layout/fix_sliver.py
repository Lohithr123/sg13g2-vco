# The Metal2 sliver at the resistor pins is 1.0 x 0.16 um — under the 0.21 um
# minimum width. Patches have not cleared it because they are drawn at the pin
# CENTRE while the sliver spans the pin's full 1.0 um width at only 0.16 um
# tall. That shape is produced by wire() when a "horizontal" segment has zero
# length: the helper falls through to its horizontal branch and emits a box
# whose height is the requested width but whose extent in x is degenerate —
# or, here, whose height comes from a stale coordinate.
#
# Rather than patch over it, stop generating it. wire() should ignore segments
# with no length in either direction, and path() should skip repeated points.

import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

old = '''def wire(lyr, x1, y1, x2, y2, w=1.0):
    x1, y1, x2, y2 = snap(x1), snap(y1), snap(x2), snap(y2)
    if abs(x2 - x1) < 1e-9:
        top.shapes(LI[lyr]).insert(
            pya.DBox(x1 - w / 2, min(y1, y2), x1 + w / 2, max(y1, y2)))
    else:
        top.shapes(LI[lyr]).insert(
            pya.DBox(min(x1, x2), y1 - w / 2, max(x1, x2), y1 + w / 2))'''

new = '''def wire(lyr, x1, y1, x2, y2, w=1.0):
    """Draw one Manhattan segment.

    A segment with no length in either direction produces a box that is only
    `w` in one dimension and nothing in the other — a sliver below minimum
    width, which DRC flags and which no amount of patching over will fix.
    Skip those instead of emitting them.
    """
    x1, y1, x2, y2 = snap(x1), snap(y1), snap(x2), snap(y2)
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    if dx < 1e-9 and dy < 1e-9:
        return                      # zero-length: nothing to draw
    if dx < 1e-9:
        top.shapes(LI[lyr]).insert(
            pya.DBox(x1 - w / 2, min(y1, y2), x1 + w / 2, max(y1, y2)))
    else:
        top.shapes(LI[lyr]).insert(
            pya.DBox(min(x1, x2), y1 - w / 2, max(x1, x2), y1 + w / 2))'''

assert old in s, "wire() not found in the expected form"
s = s.replace(old, new)

# and drop the patches, which were treating the symptom
for r in ("r1_bot", "r2_bot", "r1_top", "r2_top"):
    pat = ('\n    top.shapes(LI["M2"]).insert(pya.DBox(\n'
           f'        snap({r}.center().x - 0.45), snap({r}.center().y - 0.25),\n'
           f'        snap({r}.center().x + 0.45), snap({r}.center().y + 0.25)))')
    s = s.replace(pat, '')
for r in ("r1_bot", "r2_bot"):
    pat = ('\n    wire("M2", ' + r + '.center().x - 0.4, ' + r + '.center().y,\n'
           '         ' + r + '.center().x + 0.4, ' + r + '.center().y, 0.4)')
    s = s.replace(pat, '')

p.write_text(s)
print("wire() now skips zero-length segments; patches removed")
