import os, sys, pya
sys.path.insert(0, os.environ.get("PDK_ROOT","/foss/pdks")+"/ihp-sg13g2/libs.tech/klayout/python")
import sg13g2_pycell_lib
lib=pya.Library.library_by_name("SG13_dev","sg13g2"); L=lib.layout()
ly=pya.Layout(); ly.dbu=0.001
ci=ly.add_pcell_variant(lib, L.pcell_id("nmos"),
                        {"w":"70u","l":"1u","ng":"10","m":"1","guardRingType":"psub"})
c=ly.cell(ci)
print("cell bbox:", c.dbbox().to_s())

m1=ly.layer(8,0); poly=ly.layer(5,0); cont=ly.layer(6,0)
strips=sorted([sh.dbbox() for sh in c.shapes(m1).each()], key=lambda b: b.left)
gates =sorted([sh.dbbox() for sh in c.shapes(poly).each()], key=lambda b: b.left)
print(f"\n{len(strips)} Metal1, {len(gates)} GatPoly")

print("\nMetal1 strips (x centre, width, height):")
for b in strips:
    tag=""
    # a diffusion strip sits between two gates; the guard ring does not
    inner=[g for g in gates if g.left < b.center().x < g.right]
    print(f"  x {b.center().x:8.2f}  w {b.width():5.2f}  h {b.height():5.2f}"
          f"  y {b.bottom:8.2f}..{b.top:8.2f}")


# The guard ring is psub, tied to substrate. Source strips in an NMOS mirror
# usually connect toward it; drains do not. Check which strips the ring's
# horizontal bars actually touch or come closest to.
print("\nring bars y:", [(b.bottom,b.top) for b in strips if b.width()>10])
print("\nGatPoly (x centre):")
for g in gates:
    print(f"  x {g.center().x:8.2f}  w {g.width():5.2f}  y {g.bottom:8.2f}..{g.top:8.2f}")
