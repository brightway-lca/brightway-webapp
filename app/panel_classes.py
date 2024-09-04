import bw2data as bd
import bw2calc as bc
import bw_graph_tools as bgt

import pandas as pd

# type hint imports
from bw2data.backends.proxies import Activity
from bw_graph_tools.graph_traversal import Node


# local imports
import brightway_utilities
import brightway_main


class panel_lca_class:
    """
    This class is used to store all the necessary information for the LCA calculation.
    It provides methods to populate the database and perform Brightway LCA calculations.
    All methods can be bound to a button click event.

    Notes
    -----
    https://discourse.holoviz.org/t/update-global-variable-through-function-bound-with-on-click/
    """
    def __init__(self):
        self.db_name = 'USEEIO-1.1'
        self.db = None
        self.list_db_products = []
        self.dict_db_methods = {}
        self.chosen_activity = ''
        self.chosen_method = ''
        self.chosen_amount = 0
        self.lca = None
        self.scope_dict = {'Scope 1':0, 'Scope 2':0, 'Scope 3':0}
        self.graph_traversal_cutoff = 0.01
        self.graph_traversal = {}
        self.df_graph_traversal_nodes = None

    def set_db(self, event):
        """
        Checks if the USEEIO-1.1 Brightway project is installed.
        If not, installs it and sets is as current project.
        Else just sets the current project to USEEIO-1.1.
        """
        brightway_utilities.check_for_useeio_brightway_project(event)
        self.db = bd.Database(self.db_name)

    def set_list_db_products(self, event):
        """
        Sets `list_db_products` to a list of product names from the database for use in the autocomplete widget.
        """
        self.list_db_products = [node['name'] for node in self.db if 'product' in node['type']]
    
    def set_dict_db_methods(self, event):
        """
        Sets `dict_db_methods` to a dictionary of 'method names': (method, tuples) from the database for use in the select widget.
        """
        self.dict_db_methods = {', '.join(i):i for i in bd.methods}
    
    def set_chosen_activity(self, event, chosen_product_string: str):
        """
        Sets `chosen_activity` to the `bw2data.backends.proxies.Activity` object of the chosen product from the autocomplete widget.
        """
        self.chosen_activity: Activity = bd.utils.get_node(
            database = self.db_name,
            name = chosen_product_string,
            type = 'product',
            location = 'United States'
        )

    def set_chosen_method(self, event, method_string: str):
        """
        Sets `chosen_method` to the (tuple) corresponding to the chosen method string from the select widget.
        """
        self.chosen_method = bd.Method(self.dict_db_methods[method_string])

    def set_chosen_amount(self, event, chosen_amount: float):
        """
        Sets `chosen_amount` to the float value from the float input widget.
        """
        self.chosen_amount = chosen_amount

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
        self.graph_traversal: dict = bgt.NewNodeEachVisitGraphTraversal.calculate(self.lca, cutoff=self.graph_traversal_cutoff)
        self.df_graph_traversal_nodes: pd.DataFrame = brightway_main.nodes_dict_to_dataframe(self.graph_traversal['nodes'])


    def determine_scope_1_and_2_emissions(self, event):
        """
        Determines the scope 1 and 2 emissions from the graph traversal nodes dataframe.
        """
        dict_scope = {
            'Scope 1': 0,
            'Scope 2': 0,
            'Scope 3': 0
        }
        df = self.df_graph_traversal_nodes
        dict_scope['Scope 1'] = df.loc[(df['Scope 1?'] == True)]['Direct'].values.sum()

        try:
            dict_scope['Scope 2'] = df.loc[
                (df['Depth'] == 2)
                &
                (df['UID'] == uid_scope_2)
            ]['Cumulative'].values[0]
        except:
            pass

        self.scope_dict = dict_scope

    def determine_scope_3_emissions(self, event):
        self.scope_dict['Scope 3'] = self.lca.score - self.scope_dict['Scope 1'] - self.scope_dict['Scope 2']
