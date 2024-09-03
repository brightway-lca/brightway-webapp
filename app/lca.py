# %%
import bw_graph_tools as bgt
import bw2io as bi
import bw2data as bd
import bw2calc as bc
import pandas as pd

from bw2data.backends.proxies import Activity
from bw_graph_tools.graph_traversal import Node

"""
# there is only a single electricity process in the USEEIO database
electricity_process: Activity = bd.utils.get_node(
    database = 'USEEIO-1.1',
    name = 'Electricity; at consumer',
    location = 'United States',
    type = 'process'
)
uid_electricity_process: int = electricity_process.as_dict()['id']
"""

def determine_scope_emissions(df: pd.DataFrame, uid_electricity: int = 53) -> float:
    """
    Given a dataframe of graph nodes and the uid of the electricity production process,
    returns the scope 2 emissions.

    | UID   | Scope 1 | Depth | Cumulative |
    |-------|---------|-------|------------|
    | 0     | True    | 1     | 100        |
    | 1     | True    | 2     | 27         | # known to be scope 1 emissions
    | 2     | False   | 2     | 12         | 
    | (...) | (...)   | 2     | (...)      |
    | 53    | False   | 2     | 6          | # scope 2 emissions
    | (...) | (...)   | (...) | (...)      |

    Parameters
    ----------
    df : pd.DataFrame
       A dataframe of graph edges.
       Must contain integer-type columns `activity_datapackage_id`, `depth`, `cumulative_score`.

    Returns
    -------
    float
        Scope 2 emissions value.
    """
    dict_scope = {
        'Scope 1': 0,
        'Scope 2': 0,
        'Scope 3': 0
    }

    dict_scope['Scope 1'] = df.loc[
        (df['Depth'] == 1)
        &
        (df['UID'] == 0)
    ]['Cumulative'].values[0]

    dict_scope

    dict_scope['Scope 2'] = df.loc[
        (df['Depth'] == 2)
        &
        (df['UID'] == uid)
    ]['Cumulative'].values[0]

    return dict_scope


def nodes_dict_to_dataframe(nodes: dict) -> pd.DataFrame:
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