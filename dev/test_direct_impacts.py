# %%
import bw_graph_tools as bgt
import bw2io as bi
import bw2data as bd
import bw2calc as bc
import pandas as pd

from bw2data.backends.proxies import Activity
from bw_graph_tools.graph_traversal import Node

if 'USEEIO-1.1' not in bd.projects:
    bi.install_project(project_key="USEEIO-1.1", overwrite_existing=True)
    bd.projects.set_current("USEEIO-1.1")
else:
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
    demand={cars_activity: 100}, 
    method = method_gcc.name
) 
lca.lci() 
lca.lcia()

graph_traversal: dict = bgt.NewNodeEachVisitGraphTraversal.calculate(lca, cutoff=0.01)

# %%

def nodes_dict_to_dataframe(
        nodes: dict,
        uid_electricity: int = 53 # hardcoded for USEEIO
    ) -> pd.DataFrame:
    """
    Returns a dataframe with human-readable descriptions and emissions values of the nodes in the graph traversal.

    Parameters
    ----------
    nodes : dict
        A dictionary of nodes in the graph traversal.
        Can be created by selecting the 'nodes' key from the dictionary
        returned by the function `bw_graph_tools.NewNodeEachVisitGraphTraversal.calculate()`.

    Returns
    -------
    pd.DataFrame
        A dataframe with human-readable descriptions and emissions values of the nodes in the graph traversal.
    """
    list_of_row_dicts = []
    for current_node in nodes.values():

        scope: int = 3
        if current_node.unique_id == -1:
            continue
        elif current_node.unique_id == 0:
            scope = 1
        elif current_node.activity_datapackage_id == uid_electricity:
            scope = 2
        else:
            pass
        list_of_row_dicts.append(
            {
                'UID': current_node.unique_id,
                'Scope': scope,
                'Name': bd.get_node(id=current_node.activity_datapackage_id)['name'],
                'SupplyAmount': current_node.supply_amount,
                'BurdenIntensity': current_node.direct_emissions_score/current_node.supply_amount,
                'Burden(Cumulative)': current_node.cumulative_score,
                'Burden(Direct)': current_node.direct_emissions_score + current_node.direct_emissions_score_outside_specific_flows,
                'Depth': current_node.depth,
                'activity_datapackage_id': current_node.activity_datapackage_id,
            }
        )
    return pd.DataFrame(list_of_row_dicts)

df_nodes = nodes_dict_to_dataframe(graph_traversal['nodes'])