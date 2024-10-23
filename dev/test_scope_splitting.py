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

electricity_activity = bd.utils.get_node(
    database = 'USEEIO-1.1',
    name = 'Electricity; at consumer',
    type = 'product',
    location = 'United States'
)

bike_act = bd.utils.get_node(
    database = 'USEEIO-1.1',
    name = 'Motorcycle, bicycle, and parts; at manufacturer',
    type = 'product',
    location = 'United States'
)

method_gcc = bd.Method(('Impact Potential', 'GCC'))
lca = bc.LCA( 
    demand={bike_act: 1}, 
    method = method_gcc.name # attention here: it's not the Method object, just its name!!!
) 
lca.lci() 
lca.lcia()

graph_traversal: dict = bgt.NewNodeEachVisitGraphTraversal.calculate(lca, cutoff=0.01)

# there is only a single electricity process in the USEEIO database
electricity_process: Activity = bd.utils.get_node(
    database = 'USEEIO-1.1',
    name = 'Electricity; at consumer',
    location = 'United States',
    type = 'process'
)
uid_electricity_process: int = electricity_process.as_dict()['id']

graph_traversal_nodes: dict = graph_traversal['nodes']

def nodes_dict_to_dataframe(nodes: dict) -> pd.DataFrame:
    list_of_row_dicts = []
    for i in range(0, len(nodes)-1):
        current_node: Node = nodes[i]
        scope_1: bool = False
        if current_node.unique_id == 0:
            scope_1 = True
        else:
            pass
        list_of_row_dicts.append(
            {
                'UID': current_node.unique_id,
                'Scope 1?': scope_1,
                'Name': bd.get_node(id=current_node.activity_datapackage_id)['name'],
                'Cumulative': current_node.cumulative_score,
                'Direct': current_node.direct_emissions_score,
                'Depth': current_node.depth,
                'activity_datapackage_id': current_node.activity_datapackage_id
            }
        )
    return pd.DataFrame(list_of_row_dicts)




df_nodes = nodes_dict_to_dataframe(graph_traversal_nodes)
df_edges = pd.DataFrame(graph_traversal['edges']).drop(0)



def edges_dict_to_dataframe(edges: dict) -> pd.DataFrame:
    """
    To be added...
    """
    if len(edges) < 2:
        return pd.DataFrame()
    else:
        list_of_row_dicts = []
        for i in range(0, len(edges)-1):
            current_edge: Edge = edges[i]
            list_of_row_dicts.append(
                {
                    'consumer_unique_id': current_edge.consumer_unique_id,
                    'producer_unique_id': current_edge.producer_unique_id
                }
            )
        return pd.DataFrame(list_of_row_dicts).drop(0)


test = edges_dict_to_dataframe(graph_traversal['edges'])

#df_branches = add_branch_information_to_dataframe(df_edges)

#df_nodes = pd.merge(df_nodes, df_branches, left_on='unique_id', right_on='producer_unique_id', how='left')

def determine_scope_1_and_2_emissions(df: pd.DataFrame, uid_scope_2: int = 53) -> float:
    dict_scope = {
        'Scope 1': 0,
        'Scope 2': 0,
        'Scope 3': 0
    }

    dict_scope['Scope 1'] = df.loc[(df['Scope 1?'] == True)]['Direct'].values.sum()

    try:
        dict_scope['Scope 2'] = df.loc[
            (df['Depth'] == 2)
            &
            (df['activity_datapackage_id'] == uid_scope_2)
        ]['Direct'].values[0]
    except:
        pass

    return dict_scope