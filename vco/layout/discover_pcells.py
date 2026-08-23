# Discover the PDK's PCell libraries and their parameters.
#
# Must run INSIDE KLayout — the PCell libraries are registered by the
# application when it activates a technology, so a bare standalone
# "import klayout.db" sees nothing:
#
#   klayout -zz -nn $PDK_ROOT/ihp-sg13g2/libs.tech/klayout/tech/sg13g2.lyt \
#           -r discover_pcells.py

try:
    import pya as db
except ImportError:
    import klayout.db as db

WANT = ['npn13g2', 'nmos', 'pmos', 'cmim', 'rhigh', 'rsil', 'rppd',
        'varicap', 'inductor']
TARGETS = ['npn13g2', 'sg13_lv_nmos', 'cap_cmim', 'rhigh', 'sg13_hv_svaricap']

names = db.Library.library_names()
print("=== registered libraries ===")
if not names:
    print("  NONE")

for name in names:
    lib = db.Library.library_by_name(name)
    ly = lib.layout()
    cells = [c.name for c in ly.each_cell()]
    print(f"\n{name}  ({len(cells)} cells)")
    hits = sorted(c for c in cells if any(w in c.lower() for w in WANT))
    for h in hits[:25]:
        try:
            pc = ly.pcell_declaration(h)
        except Exception:
            pc = None
        print(f"    {h:26} {'PCell' if pc else 'fixed'}")

print("\n=== parameters for the devices this design needs ===")
seen = set()
for name in names:
    ly = db.Library.library_by_name(name).layout()
    for c in ly.each_cell():
        cn = c.name
        if cn.lower() not in TARGETS or cn in seen:
            continue
        seen.add(cn)
        try:
            pc = ly.pcell_declaration(cn)
        except Exception:
            pc = None
        if pc is None:
            print(f"\n{cn} ({name}): fixed cell, no parameters")
            continue
        print(f"\n{cn} ({name}):")
        for p in pc.get_parameters():
            print(f"    {p.name:14} default={p.default!r}")
