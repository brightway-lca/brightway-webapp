# %%
import bw_graph_tools as bgt
import bw2io as bi
import bw2data as bd
import bw2calc as bc

# bi.install_project(project_key="USEEIO-1.1", overwrite_existing=True)
bd.projects.set_current("USEEIO-1.1")

useeio = bd.Database("USEEIO-1.1")

cars_activity = bd.utils.get_node(
    database = 'USEEIO-1.1',
    name = 'Automobiles; at manufacturer',
    type = 'product',
    location = 'United States'
)

method_gcc = bd.Method(('Impact Potential', 'GCC'))
lca = bc.LCA( 
    demand={cars_activity: 1}, 
    method = method_gcc.name # attention here: it's not the Method object, just its name!!!
) 
lca.lci() 
lca.lcia()

contributing_nodes = bgt.NewNodeEachVisitGraphTraversal.calculate(lca, cutoff=0.1)