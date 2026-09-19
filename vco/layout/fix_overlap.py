import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

old = '''            _mir = -1.0 if inst.dcplx_trans.is_mirror() else 1.0
            _dx = _mir * 0.25 if ylev == y_d else 0.0'''

new = '''            _mir = -1.0 if inst.dcplx_trans.is_mirror() else 1.0
            # ROOT CAUSE of the four remaining M2.b violations.
            #
            # Measured on XSW1: the drain strip's pad spans x -8.615..-8.405
            # and my drain stub -8.390..-8.130. They are 15 nm apart — and
            # they are the SAME NET. M2.b flags a notch regardless of net, so
            # the fault was never the stub being close to a neighbour; it was
            # the stub nearly touching its own pad without overlapping it.
            #
            # A stub between two stacks can never satisfy 0.21 um either side:
            # the gap is 0.305 um and that needs 0.63 um. But it does not have
            # to. It only has to clear the OPPOSITE net, and overlap its own.
            #
            #   pad left edge        = strip - 0.105
            #   neighbour stack left = strip + pitch - 0.100
            #   right limit          = that, minus 0.21 clearance
            #   usable width         = pitch - 0.205
            #
            # For the 0.51 um switch pitch that is 0.305 um: the stub starts
            # inside its own pad and stops 0.21 um short of the next stack.
            _pitch = (strips[1].center().x - strips[0].center().x
                      if len(strips) > 1 else 1.38)
            _tight = _pitch < 0.75
            if ylev == y_d and not _tight:
                _dx = _mir * 0.25
            else:
                _dx = 0.0'''

assert s.count(old) == 1, f"matched {s.count(old)}"
s = s.replace(old, new)

old2 = '''                wire("M2", b.center().x, ylev,
                     b.center().x + _dx + 0.13, ylev, 0.26)'''
new2 = '''                if _tight and ylev == y_d:
                    # Overlap this strip's own pad, clear the next stack.
                    _w = min(0.4, _pitch - 0.205)
                    _x0 = b.center().x - 0.105
                    wire("M2", _x0, ylev, _x0 + _w, ylev, 0.26)
                else:
                    wire("M2", b.center().x, ylev,
                         b.center().x + _dx + 0.13, ylev, 0.26)'''
assert s.count(old2) == 1, f"jog matched {s.count(old2)}"
s = s.replace(old2, new2)

p.write_text(s)
print("drain stubs on tight pitches now overlap their own pad")
