# %%
import panel as pn
pn.extension(notifications=True)
pn.extension(design='material')
pn.extension('plotly')
pn.extension('tabulator')

import bw2data as bd
import bw2io as bi
import bw2calc as bc
import bw_graph_tools as bgt

from bw2data.backends.base import SQLiteBackend

import lca
import plotting
import utilities

utilities.brightway_wasm_database_storage_workaround()

import pandas as pd

from bw2data.backends.proxies import Activity
from bw_graph_tools.graph_traversal import Node

# COLUMN 1

class app_lca_class:
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
        utilities.check_for_useeio_brightway_project(event)
        self.db = bd.Database(self.db_name)

    def set_list_db_products(self, event):
        self.list_db_products = [node['name'] for node in self.db if 'product' in node['type']]
    
    def set_dict_db_methods(self, event):
        self.dict_db_methods = {', '.join(i):i for i in bd.methods}
    
    def set_chosen_activity(self, event):
        self.chosen_activity: Activity = bd.utils.get_node(
            database = self.db_name,
            name = widget_autocomplete_product.value,
            type = 'product',
            location = 'United States'
        )

    def set_chosen_method(self, event):
        self.chosen_method = bd.Method(self.dict_db_methods[widget_select_method.value])

    def set_chosen_amount(self, event):
        self.chosen_amount = widget_float_input_amount.value

    def perform_lca(self, event):
        self.lca = bc.LCA( 
            demand={self.chosen_activity: self.chosen_amount}, 
            method = self.chosen_method.name
        )
        self.lca.lci()
        self.lca.lcia()

    def set_graph_traversal_cutoff(self, event):
        self.graph_traversal_cutoff = widget_float_slider_cutoff.value / 100

    def perform_graph_traversal(self, event):
        self.graph_traversal: dict = bgt.NewNodeEachVisitGraphTraversal.calculate(self.lca, cutoff=self.graph_traversal_cutoff)
        self.df_graph_traversal_nodes = lca.nodes_dict_to_dataframe(self.graph_traversal['nodes'])


    def determine_scope_1_and_2_emissions(self, event):
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



app_lca_class_instance = app_lca_class()

def action_load_database(event):
    # load lca stuff
    app_lca_class_instance.set_db(event)
    app_lca_class_instance.set_list_db_products(event)
    app_lca_class_instance.set_dict_db_methods(event)

    # update widgets
    widget_autocomplete_product.options = app_lca_class_instance.list_db_products
    widget_select_method.options = list(app_lca_class_instance.dict_db_methods.keys())

# https://panel.holoviz.org/reference/widgets/Button.html
widget_button_load_db = pn.widgets.Button(
    name='Load USEEIO Database',
    icon='database-plus',
    button_type='primary',
    sizing_mode='stretch_width'
)
widget_button_load_db.on_click(action_load_database)

# https://panel.holoviz.org/reference/widgets/AutocompleteInput.html
widget_autocomplete_product = pn.widgets.AutocompleteInput(
    name='Reference Product',
    options=[],
    case_sensitive=False,
    search_strategy='includes',
    placeholder='Start typing your product name here...',
    sizing_mode='stretch_width'
)

# https://panel.holoviz.org/reference/widgets/Select.html
widget_select_method = pn.widgets.Select(
    name='Impact Assessment Method',
    options=[],
    sizing_mode='stretch_width'
)

# https://panel.holoviz.org/reference/widgets/FloatInput.html
widget_float_input_amount = pn.widgets.FloatInput(
    name='Amount of Reference Product',
    value=1,
    step=1,
    start=0,
    sizing_mode='stretch_width'
)

def action_perform_lca(event):
    if widget_autocomplete_product.value == '':
        pn.state.notifications.warning('Please select a reference product first!', duration=50000)
        return
    else:
        pn.state.notifications.info('Calculating LCA score...', duration=5000)
    app_lca_class_instance.set_chosen_activity(event)
    app_lca_class_instance.set_chosen_method(event)
    app_lca_class_instance.set_chosen_amount(event)
    app_lca_class_instance.perform_lca(event)
    pn.state.notifications.success('Completed LCA score calculation!', duration=5000)

    widget_number_lca_score.value = app_lca_class_instance.lca.score

# https://panel.holoviz.org/reference/widgets/Button.html
widget_button_lca = pn.widgets.Button(
    name='Compute LCA Score',
    icon='calculator',
    button_type='primary',
    sizing_mode='stretch_width'
)
widget_button_lca.on_click(action_perform_lca)

# https://panel.holoviz.org/reference/widgets/EditableFloatSlider.html
widget_float_slider_cutoff = pn.widgets.EditableFloatSlider(
    name='Graph Traversal Cut-Off [%]',
    start=1,
    end=99,
    step=1,
    value=10,
    sizing_mode='stretch_width'
)

markdown_cutoff_documentation = pn.pane.Markdown("""
A cut-off of 10% means that only those processes responsible or 90% of impact will be computed. A lower cut-off therefore results in a longer calculation, which yields a larger amount of processes.
""")

def perform_graph_traversal(event):
    widget_tabulator.loading = True
    app_lca_class_instance.perform_graph_traversal(event)
    widget_tabulator.value = app_lca_class_instance.df_graph_traversal_nodes
    column_editors = {
        colname : {'type': 'editable', 'value': True}
        for colname in app_lca_class_instance.df_graph_traversal_nodes.columns
        if colname != 'Scope 1?'
    }
    widget_tabulator.editors = column_editors
    widget_tabulator.loading = False

def perform_scope_analysis(event):
    app_lca_class_instance.determine_scope_1_and_2_emissions(event)
    app_lca_class_instance.determine_scope_3_emissions(event)
    widget_plotly_figure_piechart.object = plotting.create_plotly_figure_piechart(app_lca_class_instance.scope_dict)

def action_button_scope_analysis(event):
    if app_lca_class_instance.lca is None:
        pn.state.notifications.error('Please perform an LCA calculation first!')
        return
    else:
        if app_lca_class_instance.df_graph_traversal_nodes is None:
            pn.state.notifications.info('Performing Scope Analysis...', duration=5000)
            perform_graph_traversal(event)
            perform_scope_analysis(event)
        else:
            app_lca_class_instance.df_graph_traversal_nodes = widget_tabulator.value
            perform_scope_analysis(event)

        
# https://panel.holoviz.org/reference/widgets/Button.html
widget_button_graph = pn.widgets.Button(
    name='Perform Scope Analysis',
    icon='chart-donut-3',
    button_type='primary',
    sizing_mode='stretch_width'
)
widget_button_graph.on_click(action_button_scope_analysis)

widget_number_lca_score = pn.indicators.Number(
    name='LCA Score',
    font_size='30pt',
    title_size='20pt',
    value=0,
    format='{value:,.5f}',
    margin=0
)

scope_dict = {'Scope 1': 0}
widget_plotly_figure_piechart = pn.pane.Plotly(plotting.create_plotly_figure_piechart(scope_dict))

col1 = pn.Column(
    '## USEEIO Database Query',
    widget_button_load_db,
    widget_autocomplete_product,
    widget_select_method,
    widget_float_input_amount,
    widget_button_lca,
    widget_float_slider_cutoff,
    markdown_cutoff_documentation,
    widget_button_graph,
    pn.Spacer(height=10),
    widget_number_lca_score,
    widget_plotly_figure_piechart,
)

# COLUMN 2

# https://panel.holoviz.org/reference/widgets/Tabulator.html#formatters
from bokeh.models.widgets.tables import BooleanFormatter
widget_tabulator = pn.widgets.Tabulator(
    None,
    theme='site',
    show_index=False,
    selectable=False,
    formatters={'Scope 1?': BooleanFormatter()},
    editors={},
)

col2 = pn.Column(
    '## Table of Upstream Processes',
    widget_tabulator
)

# https://panel.holoviz.org/tutorials/basic/templates.html

logos = pn.pane.SVG(
    'app/_media/PSI+ETHZ_white.svg',
    height=50,
    margin=0,
    align="center"
)
header = pn.Row(
    pn.HSpacer(),
    pn.pane.SVG(
        'app/_media/PSI+ETHZ+WISER_white.svg',
        height=50,
        margin=0,
        align="center"
    ),
    sizing_mode="stretch_width",
)

gspec = pn.GridSpec(ncols=3, sizing_mode='stretch_both')
gspec[:,0:1] = col1
gspec[:,1:3] = col2

template = pn.template.MaterialTemplate(
    header=header,
    title='Brightway WebApp (Carbon Accounting)',
    header_background='#2d853a',
    logo='app/_media/BW_white.svg',
)
template.main.append(gspec)

template.servable()