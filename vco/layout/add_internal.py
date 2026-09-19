import pathlib

p = pathlib.Path('route_v2.py')
s = p.read_text()

old = '''    ("outbp", "M5",  -145.0, -95.23),   # buffer outputs
    ("outbn", "M5",  145.0,  -95.23),
]'''

new = '''    ("outbp", "M5",  -145.0, -95.23),   # buffer outputs
    ("outbn", "M5",  145.0,  -95.23),

    # Internal nets.
    #
    # The schematic names every node — OUTP, OUTN, E, NC, NB and the bank
    # switch nodes — while the layout's are anonymous $n. LVS matches
    # topologically from named anchors, and with 29 devices and only eight
    # anchors it cannot resolve a unique mapping: 41 nets report no match even
    # though every device and pin pairs.
    #
    # Labelling the internal nets gives it the anchors it needs. Each
    # coordinate is a point the router actually draws on that layer.
    ("outp",  "M3",  -16.0,  -105.0),   # tank, positive side
    ("outn",  "M4",  16.0,   -103.0),   # tank, negative side
    ("e",     "M5",  0.0,    -150.0),   # cross-coupled pair emitters
    ("nc",    "M2",  -30.0,  -212.5),   # cascode mirror bias
    ("nb",    "M2",  -30.0,  -183.4),   # lower mirror bias
]'''

assert s.count(old) == 1, f"matched {s.count(old)}"
s = s.replace(old, new)
p.write_text(s)
print("internal net labels added")
