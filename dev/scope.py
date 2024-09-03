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
    demand={cars_activity: 1}, 
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
            }
        )
    return pd.DataFrame(list_of_row_dicts)

df_nodes = nodes_dict_to_dataframe(graph_traversal_nodes)
#df_edges = pd.DataFrame(graph_traversal['edges']).drop(0)


def add_branch_information_to_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds 'branch' information to terminal nodes in a dataframe of graph edges.

    For example:

    | consumer_unique_id | producer_unique_id |
    |--------------------|--------------------|
    | 0                  | 1                  | # 1 is terminal producer node
    | 0                  | 2                  |
    | 0                  | 3                  |
    | 2                  | 4                  | # 4 is terminal producer node
    | 3                  | 5                  |
    | 5                  | 6                  | # 6 is terminal producer node

    | consumer_unique_id | producer_unique_id | branch       |
    |--------------------|--------------------|--------------|
    | 0                  | 1                  | [0, 1]       |
    | 0                  | 2                  | [0, 2]       |
    | 0                  | 3                  | [0, 3]       |
    | 2                  | 4                  | [0, 2, 4]    |
    | 3                  | 5                  | [0, 3, 5]    |
    | 5                  | 6                  | [0, 3, 5, 6] |

    Parameters
    ----------
    df_edges : pd.DataFrame
        A dataframe of graph edges.
        Must contain integer-type columns 'consumer_unique_id' and 'producer_unique_id'.

    Returns
    -------
    pd.DataFrame
        A dataframe of graph nodes with a column 'branch' that contains the branch of nodes that lead to the terminal producer node.
    """
    # initialize empty list to store branches
    branches: list = []

    for _, row in df.iterrows():
        branch: list = trace_branch(df, int(row['producer_unique_id']))
        branches.append({
            'producer_unique_id': int(row['producer_unique_id']),
            'branch': branch
        })

    return pd.DataFrame(branches)


def trace_branch(df: pd.DataFrame, start_node: int) -> list:
    """
    Given a dataframe of graph edges and a starting node, returns the branch of nodes that lead to the starting node.

    For example:

    | consumer_unique_id | producer_unique_id |
    |--------------------|--------------------|
    | 0                  | 1                  | # 1 is terminal producer node
    | 0                  | 2                  |
    | 0                  | 3                  |
    | 2                  | 4                  | # 4 is terminal producer node
    | 3                  | 5                  |
    | 5                  | 6                  | # 6 is terminal producer node

    For start_node = 6, the function returns [0, 3, 5, 6]

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of graph edges. Must contain integer-type columns 'consumer_unique_id' and 'producer_unique_id'.
    start_node : int
        The integer indicating the starting node to trace back from.

    Returns
    -------
    list
        A list of integers indicating the branch of nodes that lead to the starting node.
    """

    branch: list = [start_node]

    while True:
        previous_node: int = df[df['producer_unique_id'] == start_node]['consumer_unique_id']
        if previous_node.empty:
            break
        start_node: int = previous_node.values[0]
        branch.insert(0, start_node)

    return branch

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
            (df['UID'] == uid_scope_2)
        ]['Cumulative'].values[0]
    except:
        pass

    return dict_scope

#scope_1: float = df_nodes[df_nodes['unique_id'] == 0]['direct_emissions_score'][0]
#scope_2: float = determine_scope_2_emissions(df_nodes, uid_electricity_process)
#scope_3: float = lca.score - scope_1 - scope_2
#remainder: float = lca.score - df_nodes[df_nodes['unique_id'] == 0]['cumulative_score'][0]


