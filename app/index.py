# %%
import panel as pn
pn.extension(notifications=True)
pn.extension(design='material')
pn.extension('plotly')
pn.extension('tabulator')

# plotting
import plotly

# data science
import pandas as pd
import numpy as np

# system
import os

# brightway
import bw_graph_tools as bgt
import bw2io as bi
import bw2data as bd
import bw2calc as bc

# type hints
from bw2data.backends.proxies import Activity
from bw_graph_tools.graph_traversal import Node
from bw_graph_tools.graph_traversal import Edge


def brightway_wasm_database_storage_workaround() -> None:
    """
    Sets the Brightway project directory to `/tmp/.
    
    The JupyterLite file system currently does not support storage of SQL database files
    in directories other than `/tmp/`. This function sets the Brightway environment variable
    `BRIGHTWAY_DIR` to `/tmp/` to work around this limitation.
    
    Notes
    -----
    - https://docs.brightway.dev/en/latest/content/faq/data_management.html#how-do-i-change-my-data-directory
    - https://github.com/brightway-lca/brightway-live/issues/10
    """
    os.environ["BRIGHTWAY_DIR"] = "/tmp/"


def check_for_useeio_brightway_project(event):
    """
    Checks if the USEEIO-1.1 Brightway project is installed.
    If not, installs it. Shows Panel notifications for the user.

    Returns
    -------
    SQLiteBackend
        bw2data.backends.base.SQLiteBackend of the USEEIO-1.1 database
    """
    if 'USEEIO-1.1' not in bd.projects:
        notification_load = pn.state.notifications.info('Loading USEEIO database...')
        bi.install_project(project_key="USEEIO-1.1", overwrite_existing=True)
        notification_load.destroy()
        pn.state.notifications.success('USEEIO database loaded!', duration=7000)
    else:
        pn.state.notifications.success('USEEIO database already loaded!', duration=7000)
        pass
    bd.projects.set_current(name='USEEIO-1.1')


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
                'BurdenIntensity': current_node.supply_amount / current_node.direct_emissions_score,
                'Burden(Cumulative)': current_node.cumulative_score,
                'Burden(Direct)': current_node.direct_emissions_score,
                'Depth': current_node.depth,
                'activity_datapackage_id': current_node.activity_datapackage_id,
            }
        )
    return pd.DataFrame(list_of_row_dicts)


def edges_dict_to_dataframe(edges: list) -> pd.DataFrame:
    """
    To be added...
    """
    if len(edges) < 2:
        return pd.DataFrame()
    else:
        list_of_row_dicts = []
        for current_edge in edges:
            list_of_row_dicts.append(
                {
                    'consumer_unique_id': current_edge.consumer_unique_id,
                    'producer_unique_id': current_edge.producer_unique_id
                }
            )
        return pd.DataFrame(list_of_row_dicts).drop(0)


def trace_branch(df: pd.DataFrame, start_node: int) -> list:
    """
    Given a dataframe of graph edges and a "starting node" (producer_unique_id), returns the branch of nodes that lead to the starting node.

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
        The integer indicating the producer_unique_id starting node to trace back from.

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


def add_branch_information_to_edges_dataframe(df: pd.DataFrame) -> pd.DataFrame:
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
            'Branch': branch
        })

    return pd.DataFrame(branches)


def create_user_input_columns(
        df_original: pd.DataFrame,
        df_user_input: pd.DataFrame,
    ) -> pd.DataFrame:
    """
    Creates a new column in the 'original' DataFrame where only the
    user-supplied values are kept. The other values are replaced by NaN.

    For instance, given an "original" DataFrame of the kind:

    | UID | SupplyAmount | BurdenIntensity |
    |-----|--------------|-----------------|
    | 0   | 1            | 0.1             |
    | 1   | 0.5          | 0.5             |
    | 2   | 0.2          | 0.3             |

    and a "user input" DataFrame of the kind:

    | UID | SupplyAmount | BurdenIntensity |
    |-----|--------------|-----------------|
    | 0   | 1            | 0.1             |
    | 1   | 0            | 0.5             |
    | 2   | 0.2          | 2.1             |

    the function returns a DataFrame of the kind:

    | UID | SupplyAmount | SupplyAmount_USER | BurdenIntensity | BurdenIntensity_USER |
    |-----|--------------|-------------------|-----------------|----------------------|
    | 0   | 1            | NaN               | 0.1             | NaN                  |
    | 1   | 0.5          | 0                 | 0.5             | NaN                  |
    | 2   | 0.2          | NaN               | 0.3             | 2.1                  |

    Parameters
    ----------
    df_original : pd.DataFrame
        Original DataFrame.

    df_user_input : pd.DataFrame
        User input DataFrame.
    """
    
    df_merged = pd.merge(
        df_original,
        df_user_input[['UID', 'SupplyAmount', 'BurdenIntensity']],
        on='UID',
        how='left',
        suffixes=('', '_USER')
    )

    for column_name in ['SupplyAmount', 'BurdenIntensity']:
        df_merged[f'{column_name}_USER'] = np.where(
            df_merged[f'{column_name}_USER'] != df_merged[f'{column_name}'],
            df_merged[f'{column_name}_USER'],
            np.nan
        )

    return df_merged


def update_burden_intensity_based_on_user_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Updates the burden intensity when user data is provided.

    For instance, given a DataFrame of the kind:

    | UID | BurdenIntensity | BurdenIntensity_USER |
    |-----|-----------------|----------------------|
    | 0   | 0.1             | NaN                  |
    | 1   | 0.5             | 0.25                 |
    | 2   | 0.3             | NaN                  |

    the function returns a DataFrame of the kind:

    | UID | BurdenIntensity |
    |-----|-----------------|
    | 0   | 0.1             |
    | 1   | 0.25            |
    | 2   | 0.3             |
    """
    df['BurdenIntensity'] = df['BurdenIntensity_USER'].combine_first(df['BurdenIntensity'])
    df = df.drop(columns=['BurdenIntensity_USER'])

    return df

def update_production_based_on_user_data(
        df: pd.DataFrame,
    ) -> pd.DataFrame:
    """
    Updates the production amount of all nodes which are upstream
    of a node with user-supplied production amount.
    If an upstream node has half the use-supplied production amount,
    then the production amount of all downstream node is also halved.

    For instance, given a DataFrame of the kind:

    | UID | SupplyAmount | SupplyAmount_USER | Branch        |
    |-----|--------------|-------------------|---------------|
    | 0   | 1            | NaN               | NaN           |
    | 1   | 0.5          | 0.25              | [0,1]         |
    | 2   | 0.2          | NaN               | [0,1,2]       |
    | 3   | 0.1          | NaN               | [0,3]         |
    | 4   | 0.1          | 0.18              | [0,1,2,4]     |
    | 5   | 0.05         | NaN               | [0,1,2,4,5]   |
    | 6   | 0.01         | NaN               | [0,1,2,4,5,6] |

    the function returns a DataFrame of the kind:

    | UID | SupplyAmount      | Branch        |
    |-----|-------------------|---------------|
    | 0   | 1                 | NaN           |
    | 1   | 0.25              | [0,1]         |
    | 2   | 0.2 * (0.25/0.5)  | [0,1,2]       |
    | 3   | 0.1               | [0,3]         |
    | 4   | 0.18              | [0,1,2,4]     |
    | 5   | 0.05 * (0.1/0.18) | [0,1,2,4,5]   |
    | 6   | 0.01 * (0.1/0.18) | [0,1,2,4,5,6] |

    Notes
    -----

    As we can see, the function updates production only
    for those nodes upstream of a node with 'production_user':

    - Node 2 is upstream of node 1, which has a 'production_user' value.
    - Node 3 is NOT upstream of node 1. It is upstream of node 0, but node 0 does not have a 'production_user' value.

    As we can see, the function always takes the "most recent"
    'production_user' value upstream of a node:

    - Node 5 is upstream of node 4, which has a 'production_user' value.
    - Node 4 is upstream of node 1, which also has a 'production_user' value.

    In this case, the function takes the 'production_user' value of node 4, not of node 1.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame. Must have the columns 'production', 'production_user' and 'branch'.

    Returns
    -------
    pd.DataFrame
        Output DataFrame.
    """

    df_filtered = df[~df['SupplyAmount_USER'].isna()]
    dict_user_input = df_filtered.set_index('UID').to_dict()['SupplyAmount_USER']
    
    """
    For the example DataFrame from the docstrings above,
    the dict_user_input would be:

    dict_user_input = {
        1: 0.25,
        4: 0.18
    }
    """

    df = df.copy(deep=True)
    def multiplier(row):
        if not isinstance(row['Branch'], list):
            return row['SupplyAmount']
        for branch_UID in reversed(row['Branch']):
            if branch_UID in dict_user_input:
                return row['SupplyAmount'] * dict_user_input[branch_UID]
        return row['SupplyAmount']

    df['SupplyAmount_EDITED'] = df.apply(multiplier, axis=1)

    df.drop(columns=['SupplyAmount_USER'], inplace=True)
    df['SupplyAmount'] = df['SupplyAmount_EDITED']
    df.drop(columns=['SupplyAmount_EDITED'], inplace=True)

    return df


def determine_edited_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Determines which rows have been edited by the user.

    For instance, given a DataFrame of the kind:

    | UID | SupplyAmount_USER | BurdenIntensity_USER |
    |-----|-------------------|----------------------|
    | 0   | NaN               | NaN                  |
    | 1   | 0.25              | NaN                  |
    | 2   | NaN               | 2.1                  |
    | 3   | NaN               | NaN                  |

    the function returns a DataFrame of the kind:

    | UID | SupplyAmount_USER | BurdenIntensity_USER | Edited? |
    |-----|-------------------|----------------------|---------|
    | 0   | NaN               | NaN                  | False   |
    | 1   | 0.25              | NaN                  | True    |
    | 2   | NaN               | 2.1                  | True    |
    | 3   | NaN               | NaN                  | False   |
    """
    df['Edited?'] = df[['SupplyAmount_USER', 'BurdenIntensity_USER']].notnull().any(axis=1)
    return df

def create_plotly_figure_piechart(data_dict: dict) -> plotly.graph_objects.Figure:
    marker_colors = []
    for label in data_dict.keys():
        if label == 'Scope 1':
            marker_colors.append('#33cc33')  # Color for Scope 1
        elif label == 'Scope 2':
            marker_colors.append('#ffcc00')  # Color for Scope 2
        elif label == 'Scope 3':
            marker_colors.append('#3366ff')  # Color for Scope 3
        else:
            marker_colors.append('#000000')  # Default color for other labels

    plotly_figure = plotly.graph_objects.Figure(
        data=[
            plotly.graph_objects.Pie(
                labels=list(data_dict.keys()),
                values=list(data_dict.values()),
                marker=dict(colors=marker_colors)  # Set the colors for the pie chart
            )
        ]
    )
    plotly_figure.update_traces(
        marker=dict(
            line=dict(color='#000000', width=2)
        )
    )
    plotly_figure.update_layout(
        autosize=True,
        height=300,
        legend=dict(
            orientation="v",
            yanchor="auto",
            y=1,
            xanchor="right",
            x=-0.3
        ),
        margin=dict(
            l=50,
            r=50,
            b=0,
            t=0,
            pad=0
        ),
    )
    return plotly_figure


class panel_lca_class:
    """
    This class is used to store all the necessary information for the LCA calculation.
    It provides methods to populate the database and perform Brightway LCA calculations.
    All methods can be bound to a button click event.

    Notes
    -----
    https://discourse.holoviz.org/t/update-global-variable-through-function-bound-with-on-click/
    """
    brightway_wasm_database_storage_workaround()
    def __init__(self):
        self.db_name = 'USEEIO-1.1'
        self.db = None
        self.list_db_products = []
        self.dict_db_methods = {}
        self.list_db_methods = []
        self.chosen_activity = ''
        self.chosen_method = ''
        self.chosen_method_unit = ''
        self.chosen_amount = 0
        self.lca = None
        self.scope_dict = {'Scope 1':0, 'Scope 2':0, 'Scope 3':0}
        self.graph_traversal_cutoff = 1
        self.graph_traversal = {}
        self.df_graph_traversal_nodes = None
        self.df_graph_traversal_edges = None
        self.df_tabulator_from_traversal = None
        self.df_tabulator_from_user = None
        self.df_tabulator = None # nota bene: gets updated automatically when cells in the tabulator are edited # https://panel.holoviz.org/reference/widgets/Tabulator.html#editors-editing
        self.bool_user_provided_data = False


    def set_db(self, event):
        """
        Checks if the USEEIO-1.1 Brightway project is installed.
        If not, installs it and sets is as current project.
        Else just sets the current project to USEEIO-1.1.
        """
        check_for_useeio_brightway_project(event)
        self.db = bd.Database(self.db_name)


    def set_list_db_products(self, event):
        """
        Sets `list_db_products` to a list of product names from the database for use in the autocomplete widget.
        """
        self.list_db_products = [node['name'] for node in self.db if 'product' in node['type']]
    

    def set_methods_objects(self, event):
        """
        dict_methods = {
            'HRSP': ('Impact Potential', 'HRSP'),
            'OZON': ('Impact Potential', 'OZON'),
            ...
        }
        """
        dict_methods = {i[-1]:[i] for i in bd.methods}

        """
        dict_method_names = {
            'HRSP': 'Human Health: Respiratory effects',
            'OZON': 'Ozone Depletion',
            ...
        }
        """
        # hardcoded for better Pyodide performance
        dict_methods_names = {
            "HRSP": "Human Health - Respiratory Effects",
            "OZON": "Ozone Depletion",
            "HNC": "Human Health Noncancer",
            "WATR": "Water",
            "METL": "Metals",
            "EUTR": "Eutrophication",
            "HTOX": "Human Health Cancer and Noncancer",
            "LAND": "Land",
            "NREN": "Nonrenewable Energy",
            "ETOX": "Freshwater Aquatic Ecotoxicity",
            "PEST": "Pesticides",
            "REN": "Renewable Energy",
            "MINE": "Minerals and Metals",
            "GCC": "Global Climate Change",
            "ACID": "Acid Rain",
            "HAPS": "Hazardous Air Pollutants",
            "HC": "Human Health Cancer",
            "SMOG": "Smog Formation",
            "ENRG": "Energy"
        }
        # path_impact_categories_names: str = '../app/_data/USEEIO_impact_categories_names.csv'
        # dict_methods_names = {}
        # with open(path_impact_categories_names, mode='r', newline='', encoding='utf-8-sig') as file:
        #    reader = csv.reader(file)
        #    dict_methods_names = {rows[0]: rows[1] for rows in reader}

        """
        dict_methods_units = {
            'HRSP': '[kg PM2.5 eq]',
            'OZON': '[kg O3 eq]',
            ...
        }
        """
        # hardcoded for better Pyodide performance
        dict_methods_units = {
            "HRSP": "[kg PM2.5 eq]",
            "OZON": "[kg O3 eq]",
            "HNC": "[CTUh]",
            "WATR": "[m3]",
            "METL": "[kg]",
            "EUTR": "[kg N eq]",
            "HTOX": "[CTUh]",
            "LAND": "[m2*yr]",
            "NREN": "[MJ]",
            "ETOX": "[CTUe]",
            "PEST": "[kg]",
            "REN": "[MJ]",
            "MINE": "[kg]",
            "GCC": "[kg CO2 eq]",
            "ACID": "[kg SO2 eq]",
            "HAPS": "[kg]",
            "HC": "[CTUh]",
            "SMOG": "[kg O3 eq]",
            "ENRG": "[MJ]"
        }
        # path_impact_categories_units: str = '../app/_data/USEEIO_impact_categories_units.csv'
        # dict_methods_units = {}
        # with open(path_impact_categories_units, mode='r', newline='', encoding='utf-8-sig') as file:
        #    reader = csv.reader(file)
        #    dict_methods_units = {rows[0]: str('[')+rows[1]+str(']') for rows in reader}

        """
        dict_methods_enriched = {
            'HRSP': [('Impact Potential', 'HRSP'), 'Human Health - Respiratory effects', '[kg PM2.5 eq]'],
            'OZON': [('Impact Potential', 'OZON'), 'Ozone Depletion', '[kg O3 eq]'],
            ...
        }
        """
        dict_methods_enriched = {
            key: [dict_methods[key][0], dict_methods_names[key], dict_methods_units[key]]
            for key in dict_methods
        }

        """
        list_methods_for_autocomplete = [
            ('HRSP', 'Human Health: Respiratory effects', '[kg PM2.5 eq]'),
            ('OZON', 'Ozone Depletion', '[kg O3 eq]'),
            ...
        ]
        """
        list_methods_for_autocomplete = [(key, value[1], value[2]) for key, value in dict_methods_enriched.items()]

        self.dict_db_methods = dict_methods_enriched
        self.list_db_methods = list_methods_for_autocomplete


    def set_chosen_activity(self, event):
        """
        Sets `chosen_activity` to the `bw2data.backends.proxies.Activity` object of the chosen product from the autocomplete widget.
        """
        self.chosen_activity: Activity = bd.utils.get_node(
            database = self.db_name,
            name = widget_autocomplete_product.value,
            type = 'product',
            location = 'United States'
        )


    def set_chosen_method_and_unit(self, event):
        """
        Sets `chosen_method` to the (tuple) corresponding to the chosen method string from the select widget.

        Example:
        --------
        widget_select_method.value = ('HRSP', 'Human Health: Respiratory effects', '[kg PM2.5 eq]')
        widget_select_method.value[0] = 'HRSP'
        dict_db_methods = {'HRSP': [('Impact Potential', 'HRSP'), 'Human Health - Respiratory effects', '[kg PM2.5 eq]']}
        dict_db_methods['HRSP'][0] = ('Impact Potential', 'HRSP') # which is the tuple that bd.Method needs
        """
        self.chosen_method = bd.Method(self.dict_db_methods[widget_select_method.value[0]][0])
        self.chosen_method_unit = widget_select_method.value[2]


    def set_chosen_amount(self, event):
        """
        Sets `chosen_amount` to the float value from the float input widget.
        """
        self.chosen_amount = widget_float_input_amount.value


    def perform_lca(self, event):
        """
        Performs the LCA calculation using the chosen product, method, and amount.
        Sets the `lca` attribute to an instance of the `bw2calc.LCA` object.
        """
        self.lca = bc.LCA( 
            demand={self.chosen_activity: self.chosen_amount}, 
            method = self.chosen_method.name
        )
        self.lca.lci()
        self.lca.lcia()


    def set_graph_traversal_cutoff(self, event):
        """
        Sets the `graph_traversal_cutoff` attribute to the float value from the float slider widget.
        Note that the value is divided by 100 to convert from percentage to decimal.
        """
        self.graph_traversal_cutoff = widget_float_slider_cutoff.value / 100


    def perform_graph_traversal(self, event):
        widget_cutoff_indicator_statictext.value = self.graph_traversal_cutoff * 100
        self.graph_traversal: dict = bgt.NewNodeEachVisitGraphTraversal.calculate(self.lca, cutoff=self.graph_traversal_cutoff)
        self.df_graph_traversal_nodes: pd.DataFrame = nodes_dict_to_dataframe(self.graph_traversal['nodes'])
        self.df_graph_traversal_edges: pd.DataFrame = edges_dict_to_dataframe(self.graph_traversal['edges'])
        if self.df_graph_traversal_edges.empty:
            return
        else:
            self.df_graph_traversal_edges = add_branch_information_to_edges_dataframe(self.df_graph_traversal_edges)
            self.df_tabulator_from_traversal = pd.merge(
                self.df_graph_traversal_nodes,
                self.df_graph_traversal_edges,
                left_on='UID',
                right_on='producer_unique_id',
                how='left')


    def determine_scope_emissions(self, df: pd.DataFrame):
        """
        Determines the scope 1/2/3 emissions from the graph traversal nodes dataframe.
        """
        dict_scope = {
            'Scope 1': 0,
            'Scope 2': 0,
            'Scope 3': 0
        }
        burden_total: float = 0

        burden_total = df.loc[(df['UID'] == 0)]['Burden(Cumulative)'].values.sum()
        
        dict_scope['Scope 1'] = df.loc[(df['Scope'] == 1)]['Burden(Direct)'].values.sum()
        dict_scope['Scope 2'] = df.loc[(df['Scope'] == 2)]['Burden(Direct)'].values.sum()
        dict_scope['Scope 3'] = burden_total - dict_scope['Scope 1'] - dict_scope['Scope 2']

        self.scope_dict = dict_scope


brightway_wasm_database_storage_workaround()
panel_lca_class_instance = panel_lca_class()

# COLUMN 1 ####################################################################

def button_action_load_database(event):
    panel_lca_class_instance.set_db(event)
    panel_lca_class_instance.set_list_db_products(event)
    panel_lca_class_instance.set_methods_objects(event)
    widget_autocomplete_product.options = panel_lca_class_instance.list_db_products
    widget_select_method.options = panel_lca_class_instance.list_db_methods
    widget_select_method.value = [item for item in panel_lca_class_instance.list_db_methods if 'GCC' in item[0]][0] # global warming as default value


def button_action_perform_lca(event):
    if widget_autocomplete_product.value == '':
        pn.state.notifications.error('Please select a reference product first!', duration=5000)
        return
    else:
        panel_lca_class_instance.df_graph_traversal_nodes = pd.DataFrame()
        widget_plotly_figure_piechart.object = create_plotly_figure_piechart({'null':0})
        pn.state.notifications.info('Calculating LCA score...', duration=5000)
        pass
    panel_lca_class_instance.set_chosen_activity(event)
    panel_lca_class_instance.set_chosen_method_and_unit(event)
    panel_lca_class_instance.set_chosen_amount(event)
    panel_lca_class_instance.perform_lca(event)
    pn.state.notifications.success('Completed LCA score calculation!', duration=5000)
    widget_number_lca_score.value = panel_lca_class_instance.lca.score
    widget_number_lca_score.format = f'{{value:,.3f}} {panel_lca_class_instance.chosen_method_unit}'
    perform_graph_traversal(event)
    perform_scope_analysis(event)


def perform_graph_traversal(event):
    pn.state.notifications.info('Performing Graph Traversal...', duration=5000)
    panel_lca_class_instance.bool_user_provided_data = False
    panel_lca_class_instance.set_graph_traversal_cutoff(event)
    panel_lca_class_instance.perform_graph_traversal(event)
    panel_lca_class_instance.df_tabulator = panel_lca_class_instance.df_tabulator_from_traversal.copy()
    widget_tabulator.value = panel_lca_class_instance.df_tabulator
    column_editors = {
        colname: None
        for colname in panel_lca_class_instance.df_tabulator.columns
        if colname not in ['Scope', 'SupplyAmount', 'BurdenIntensity']
    }
    column_editors['Scope'] = {'type': 'list', 'values': [1, 2, 3]}
    widget_tabulator.editors = column_editors
    pn.state.notifications.success('Graph Traversal Complete!', duration=5000)


def generate_table_filename(event):
    str_filename: str = (
        "activity='"
        + panel_lca_class_instance.chosen_activity['name'].replace(' ', '_').replace(';', '') .replace(',', '')
        + "'_method='"
        + '-'.join(panel_lca_class_instance.chosen_method.name).replace(' ', '-')
        + "'_cutoff=" 
        + str(panel_lca_class_instance.graph_traversal_cutoff).replace('.', ',') 
        + ".csv"
    )
    return str_filename

def perform_scope_analysis(event):
    pn.state.notifications.info('Performing Scope Analysis...', duration=5000)
    panel_lca_class_instance.determine_scope_emissions(df=widget_tabulator.value)
    widget_plotly_figure_piechart.object = create_plotly_figure_piechart(panel_lca_class_instance.scope_dict)
    filename_download.value = generate_table_filename(event)
    pn.state.notifications.success('Scope Analysis Complete!', duration=5000)


def update_data_based_on_user_input(event):
    pn.state.notifications.info('Updating Supply Chain based on User Input...', duration=5000)
    panel_lca_class_instance.df_tabulator_from_user = create_user_input_columns(
        df_original=panel_lca_class_instance.df_tabulator_from_traversal,
        df_user_input=panel_lca_class_instance.df_tabulator_from_user,
    )
    panel_lca_class_instance.df_tabulator_from_user = determine_edited_rows(df=panel_lca_class_instance.df_tabulator_from_user)
    panel_lca_class_instance.df_tabulator_from_user = update_production_based_on_user_data(df=panel_lca_class_instance.df_tabulator_from_user)
    panel_lca_class_instance.df_tabulator_from_user = update_burden_intensity_based_on_user_data(df=panel_lca_class_instance.df_tabulator_from_user)
    panel_lca_class_instance.df_tabulator = panel_lca_class_instance.df_tabulator_from_user.copy()
    widget_tabulator.value = panel_lca_class_instance.df_tabulator
    pn.state.notifications.success('Completed Updating Supply Chain based on User Input!', duration=5000)

def button_action_scope_analysis(event):
    if panel_lca_class_instance.lca is None:
        pn.state.notifications.error('Please perform an LCA Calculation first!', duration=5000)
        return
    else:
        # if the user has not yet performed graph traversal, or changed the cutoff value,
        # then perform graph traversal and scope analysis
        if (
            panel_lca_class_instance.df_graph_traversal_nodes.empty or
            widget_float_slider_cutoff.value / 100 != panel_lca_class_instance.graph_traversal_cutoff
        ):
            perform_graph_traversal(event)
            perform_scope_analysis(event)
        # if the user has already provided input data, we reset the dataframe
        elif panel_lca_class_instance.bool_user_provided_data == True:
            pn.state.notifications.error('You are not allowed to edit a table which has already been re-computed on your input! Resetting the table...', duration=5000)
            perform_graph_traversal(event)
            perform_scope_analysis(event)
        # if the user has overriden either supply or burden intensity values in the table,
        # then update upstream values based on user input
        elif (
            (panel_lca_class_instance.df_tabulator['SupplyAmount'] != panel_lca_class_instance.df_tabulator_from_traversal['SupplyAmount']).any() or 
            (panel_lca_class_instance.df_tabulator['BurdenIntensity'] != panel_lca_class_instance.df_tabulator_from_traversal['BurdenIntensity']).any()
        ):
            panel_lca_class_instance.bool_user_provided_data = True
            panel_lca_class_instance.df_tabulator_from_user = panel_lca_class_instance.df_tabulator.copy()
            update_data_based_on_user_input(event)
            perform_scope_analysis(event)
        elif (
            (panel_lca_class_instance.df_tabulator['Scope'] != panel_lca_class_instance.df_tabulator_from_traversal['Scope']).any()
        ):
            perform_scope_analysis(event)


widget_button_load_db = pn.widgets.Button( 
    name='Load USEEIO Database',
    icon='database-plus',
    button_type='primary',
    sizing_mode='stretch_width'
)
widget_button_load_db.on_click(button_action_load_database)

widget_autocomplete_product = pn.widgets.AutocompleteInput( 
    name='Reference Product/Product/Service',
    options=[],
    case_sensitive=False,
    search_strategy='includes',
    placeholder='Start typing your product name here...',
    sizing_mode='stretch_width'
)

markdown_method_documentation = pn.pane.Markdown("""
The impact assessment methods are documented [in Table 3](https://www.nature.com/articles/s41597-022-01293-7/tables/4) of the [USEEIO release article](https://doi.org/10.1038/s41597-022-01293-7).
""")

widget_select_method = pn.widgets.Select( 
    name='Impact Assessment Method',
    options=[],
    sizing_mode='stretch_width',

)

widget_float_input_amount = pn.widgets.FloatInput( 
    name='(Monetary) Amount of Reference Product [USD]',
    value=100,
    step=1,
    start=0,
    sizing_mode='stretch_width'
)

widget_button_lca = pn.widgets.Button( 
    name='Compute LCA Score',
    icon='calculator',
    button_type='primary',
    sizing_mode='stretch_width'
)
widget_button_lca.on_click(button_action_perform_lca)

widget_float_slider_cutoff = pn.widgets.EditableFloatSlider(
    name='Graph Traversal Cut-Off [%]',
    start=1,
    end=50,
    step=1,
    value=10,
    sizing_mode='stretch_width'
)

markdown_cutoff_documentation = pn.pane.Markdown("""
[A cut-off of 10%](https://docs.brightway.dev/projects/graphtools/en/latest/content/api/bw_graph_tools/graph_traversal/new_node_each_visit/index.html) means that only those processes responsible or 90% of impact will be computed.
""")
        
widget_button_graph = pn.widgets.Button(
    name='Update Data based on User Input',
    icon='chart-donut-3',
    button_type='primary',
    sizing_mode='stretch_width'
)
widget_button_graph.on_click(button_action_scope_analysis)

widget_number_lca_score = pn.indicators.Number(
    name='LCA Impact Score',
    font_size='30pt',
    title_size='20pt',
    value=0,
    format='{value:,.3f}',
    margin=0
)

widget_plotly_figure_piechart = pn.pane.Plotly(
    create_plotly_figure_piechart(
        {'Scope 1': 0}
    )
)

col1 = pn.Column(
    '# LCA Settings',
    widget_button_load_db,
    widget_autocomplete_product,
    markdown_method_documentation,
    widget_select_method,
    widget_float_input_amount,
    markdown_cutoff_documentation,
    widget_float_slider_cutoff,
    widget_button_lca,
    widget_button_graph,
    pn.Spacer(height=10),
    widget_number_lca_score,
    widget_plotly_figure_piechart,
)

# COLUMN 2 ####################################################################

from bokeh.models.widgets.tables import BooleanFormatter


def highlight_tabulator_cells(tabulator_row):
    """
    See Also
    --------
    - https://stackoverflow.com/a/48306463
    - https://discourse.holoviz.org/t/dynamic-update-of-tabulator-style
    """
    if tabulator_row['Edited?'] == True:
        return ['background-color: orange'] * len(tabulator_row)
    else:
        return [''] * len(tabulator_row)
    

widget_tabulator = pn.widgets.Tabulator(
    pd.DataFrame([['']], columns=['Data will appear here after calculations...']),
    theme='site',
    show_index=False,
    hidden_columns=['activity_datapackage_id', 'producer_unique_id'],
    layout='fit_data_stretch',
    sizing_mode='stretch_width'
)
widget_tabulator.style.apply(highlight_tabulator_cells, axis=1)

filename_download, button_download = widget_tabulator.download_menu(
    text_kwargs={'name': 'Filename', 'value': 'filename.csv'},
    button_kwargs={'name': 'Download Table'}
)
filename_download.sizing_mode = 'stretch_width'
button_download.align = 'center'
button_download.icon = 'download'

widget_cutoff_indicator_statictext = pn.widgets.StaticText(
    name='Includes processes responsible for amount of emissions [%]',
    value=None
)

col2 = pn.Column(
    pn.Row('# Table of Upstream Processes', filename_download, button_download),
    widget_tabulator
)

# SITE ######################################################################

code_open_window = """
window.open("https://github.com/brightway-lca/brightway-webapp/blob/main/README.md")
"""
button_about = pn.widgets.Button(name="Learn more about this prototype...", button_type="success")
button_about.js_on_click(code=code_open_window)

header = pn.Row(
    button_about,
    pn.HSpacer(),
    pn.pane.SVG(
        'https://raw.githubusercontent.com/brightway-lca/brightway-webapp/main/app/_media/logo_PSI-ETHZ-WISER_white.svg',
        #height=50,
        margin=0,
        align="center"
    ),
    sizing_mode="stretch_width",
)

template = pn.template.MaterialTemplate(
    header=header,
    title='Brightway WebApp (Carbon Accounting)',
    header_background='#2d853a', # green
    logo='https://raw.githubusercontent.com/brightway-lca/brightway-webapp/main/app/_media/logo_brightway_white.svg',
    favicon='https://raw.githubusercontent.com/brightway-lca/brightway-webapp/main/app/_media/favicon.png',
)

gspec = pn.GridSpec(ncols=3, sizing_mode='stretch_both')
gspec[:,0:1] = col1 # 1/3rd of the width
gspec[:,1:3] = col2 # 2/3rds of the width

template.main.append(gspec)
template.servable()