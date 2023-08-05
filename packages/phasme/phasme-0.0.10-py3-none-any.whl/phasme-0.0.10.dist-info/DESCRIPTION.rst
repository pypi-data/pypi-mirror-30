# Phasme
Graph with ASP made easy.



## Use cases

### Write an ASP graph into gexf

    phasme convert data.lp target.gexf

### Extract the biggest cc, write it anonymized in gml

    phasme split data.lp --biggest-first "data_cc.lp" --slice 0 1
    phasme convert data_cc_1.lp target.gml --anonymized

### Generate a small world graph in gml

    phasme generate data.gml erdos_renyi_graph n=100 p=0.01


## Packaging

    pip install graph-asp

Will also populate your env with the executable `phasme`,
enabling access to the CLI.

Note that the package *phasme* exists, but is unrelated to this work.


## CLI commands
CLI provides access to higher level [routines](phasme/routines.py).

- `split`: split by connected component.
- `info`: give info about given graph.
- `convert`: rewrite, anonymize or convert the graph to (clean) ASP or standard format.
- `generate`: generate a graph using a given generation method.
<!-- - `compress`: produce the powergraph compression of given graph as a bubble file -->
<!-- - ``:  -->

### Other examples

    # split a graph by cc
    python -m phasme split data.lp -o "data_{}.lp"

    # get infos
    python -m phasme infos data.lp --graph-properties

    # there is a shitload of options
    python -m phasme infos --help

    # conversions between formats
    python -m phasme convert data.lp data.gml --anonymize

    # generation of new graphs to play with
    python -m phasme generate graph.gml powerlaw_cluster_graph n=5 m=2 p=0.01


