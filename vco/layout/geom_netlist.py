import pathlib

p = pathlib.Path('/foss/designs/vco/vco_lvs.cdl')
s = p.read_text()

# Mapping taken from the extracted netlist, which is the layout's own view:
#   cap_cmim w=51.58u  -> CC1, CC2   (4p)
#   cap_cmim w=4.53u   -> CT         (31.6f)
#   cap_cmim w=3.59u   -> CB1A, CB1B (20f)
#   cap_cmim w=2.52u   -> CB0A, CB0B (10f)
#   rhigh l=73.73u     -> the four 100k bleeds
#   rhigh l=7.27u      -> RB1, RB2, RREF (10k)
sub = [
    ('CT OUTP OUTN cap_cmim 31.6f',
     'CT OUTP OUTN cap_cmim w=4.53u l=4.53u'),
    ('CC1 OUTP G1 cap_cmim 4p',
     'CC1 OUTP G1 cap_cmim w=51.58u l=51.58u'),
    ('CC2 OUTN G2 cap_cmim 4p',
     'CC2 OUTN G2 cap_cmim w=51.58u l=51.58u'),
    ('CB0A OUTP S0A cap_cmim 10f',
     'CB0A OUTP S0A cap_cmim w=2.52u l=2.52u'),
    ('CB0B OUTN S0B cap_cmim 10f',
     'CB0B OUTN S0B cap_cmim w=2.52u l=2.52u'),
    ('CB1A OUTP S1A cap_cmim 20f',
     'CB1A OUTP S1A cap_cmim w=3.59u l=3.59u'),
    ('CB1B OUTN S1B cap_cmim 20f',
     'CB1B OUTN S1B cap_cmim w=3.59u l=3.59u'),
    ('RB1 G1 VG GND 10k MODEL=rhigh',
     'RB1 G1 VG GND MODEL=rhigh w=1u l=7.27u'),
    ('RB2 G2 VG GND 10k MODEL=rhigh',
     'RB2 G2 VG GND MODEL=rhigh w=1u l=7.27u'),
    ('RREF VCC NC GND 10k MODEL=rhigh',
     'RREF VCC NC GND MODEL=rhigh w=1u l=7.27u'),
    ('RBL0A S0A GND GND 100k MODEL=rhigh',
     'RBL0A S0A GND GND MODEL=rhigh w=1u l=73.73u'),
    ('RBL0B S0B GND GND 100k MODEL=rhigh',
     'RBL0B S0B GND GND MODEL=rhigh w=1u l=73.73u'),
    ('RBL1A S1A GND GND 100k MODEL=rhigh',
     'RBL1A S1A GND GND MODEL=rhigh w=1u l=73.73u'),
    ('RBL1B S1B GND GND 100k MODEL=rhigh',
     'RBL1B S1B GND GND MODEL=rhigh w=1u l=73.73u'),
]

missed = []
for a, b in sub:
    if a in s:
        s = s.replace(a, b)
    else:
        missed.append(a)

p.write_text(s)
print(f"{len(sub) - len(missed)} of {len(sub)} substitutions applied")
for m in missed:
    print("  MISSED:", m)
