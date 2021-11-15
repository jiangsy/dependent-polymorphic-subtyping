eval `(opam env)`;
coqtop < DrawDependency.v;
python modify_dpd.py;
dpd2dot -without-defs new_graph.dot;
dot -Tsvg new_graph.dot > dpd.svg;

