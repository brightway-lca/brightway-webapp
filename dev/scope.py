# %%
import bw_graph_tools as bgt
import bw2io as bi
import bw2data as bd
import bw2calc as bc

from bw2data.backends.proxies import Activity
from bw_graph_tools.graph_traversal import Node

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

graph_traversal: dict = bgt.NewNodeEachVisitGraphTraversal.calculate(lca, cutoff=0.01)

# there is only a single electricity process in the USEEIO database
electricity_process: Activity = bd.utils.get_node(
    database = 'USEEIO-1.1',
    name = 'Electricity; at consumer',
    location = 'United States',
    type = 'process'
)

scope_1: float = 0
scope_2: float = 0
scope_3: float = 0


graph_traversal_nodes: dict = graph_traversal['nodes']

def nodes_to_dataframe(nodes: dict) -> pd.DataFrame:
    """
    Returns a dataframe with human-readable descriptions and emissions values of the nodes in the graph traversal.

    _extended_summary_

    Parameters
    ----------
    nodes : dict
        A dictionary of nodes in the graph traversal.
        Can be created by selecting the 'nodes' key from the dictionary
        returned by the function bw_graph_tools.NewNodeEachVisitGraphTraversal.calculate().

    Returns
    -------
    pd.DataFrame
        _description_
    """
    list_for_df = []
    for i in range(0, len(graph_traversal_nodes)-1):
        current_node: Node = graph_traversal_nodes[i]
        list_for_df.append(
            {
                'unique_id': current_node.unique_id,
                'name': bd.get_node(id=current_node.activity_datapackage_id)['name'],
                'cumulative_score': current_node.cumulative_score,
                'direct_emissions_score': current_node.direct_emissions_score,
            }
        )
    return pd.DataFrame(list_for_df)



list_all_nodes_uid = [node.unique_id for node in graph_traversal_nodes.values()][1:]
list_all_nodes_uid = list_all_nodes_uid[1:] # remove the first node

df_nodes = pd.DataFrame([node for node in graph_traversal['nodes'].values()])
df_edges = pd.DataFrame(graph_traversal['edges'])


for node_uid in list_all_nodes_uid:
    list_uid_in_branch = [node_uid]
    df_current_edges = df_all_edges[df_all_edges['producer_unique_id'] == node_uid]

def add_branch_information_to_nodes(
    df_nodes: pd.DataFrame,
    df_edges: pd.DataFrame,
) -> pd.DataFrame:
    """
    """
    df_nodes['branch'] = np.empty((len(df_nodes), 0)).tolist()
    for uid_producer in df_edges['producer_unique_id'].values:
        uid_consumer = df_edges.loc[df_edges['producer_unique_id'] == uid_producer, 'consumer_unique_id'].values[0]
        df_nodes.loc[df_nodes['unique_id'] == uid_producer, 'branch'] += [uid_producer, uid_consumer]
    return df_nodes


def add_branch_information(df_edges: pd.DataFrame) -> pd.DataFrame:
    """
    Adds 'branch' information to an 

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


    """
# %%
# Initialize an empty list to store the branches
branches = []

# Helper function to backtrack the branch
def find_branch(df, start_node):
    branch = [start_node]
    while True:
        previous_node = df[df['producer_unique_id'] == start_node]['consumer_unique_id']
        if previous_node.empty:
            break
        start_node = previous_node.values[0]
        branch.insert(0, start_node)
    return branch

# Identify terminal nodes
terminal_nodes = set(df_edges['producer_unique_id']) - set(df_edges['consumer_unique_id'])

# Backtrack and build the branch for each terminal node
for node in terminal_nodes:
    branch = find_branch(df_edges, node)
    branches.append(branch)

# Create a new dataframe with the branches
branch_df = pd.DataFrame({
    'producer_unique_id': [branch[-1] for branch in branches],
    'branch': branches
})