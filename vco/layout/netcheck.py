import pya
ly=pya.Layout(); ly.read("vco_20g_routed.gds")
top=ly.top_cell()
l2n=pya.LayoutToNetlist(pya.RecursiveShapeIterator(ly, top, []))
l2n.register(pya.Region(top.begin_shapes_rec(ly.layer(8,0))), "M1")
l2n.register(pya.Region(top.begin_shapes_rec(ly.layer(10,0))), "M2")
l2n.register(pya.Region(top.begin_shapes_rec(ly.layer(19,0))), "V1")
l2n.connect(l2n.layer_by_name("M1"))
l2n.connect(l2n.layer_by_name("M2"))
l2n.connect(l2n.layer_by_name("V1"))
l2n.connect(l2n.layer_by_name("M1"), l2n.layer_by_name("V1"))
l2n.connect(l2n.layer_by_name("V1"), l2n.layer_by_name("M2"))
l2n.extract_netlist()
c=l2n.netlist().circuit_by_name(top.name)
probes={"XQ1_C":(-9.0,-99.1),"XQ2_C":(9.0,-99.1),
        "XQ1_B":(-9.0,-101.37),"XQ2_B":(9.0,-101.37)}
for nm,(x,y) in probes.items():
    n=l2n.probe_net(l2n.layer_by_name("M1"), pya.DPoint(x,y))
    print(f"  {nm:7} -> net {n.expanded_name() if n else 'none'}")
