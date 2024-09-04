# %%
import panel as pn
pn.extension(notifications=True)
pn.extension(design='material')
pn.extension('plotly')
pn.extension('tabulator')

import panel_classes
import brightway_main
import brightway_utilities
import plotting

# Currently required for Brightway to work with JupyterLite/Pyodide
brightway_utilities.brightway_wasm_database_storage_workaround()

panel_lca_class_instance = panel_classes.panel_lca_class()

# COLUMN 1 ####################################################################

def button_action_load_database(event):
    panel_lca_class_instance.set_db(event)
    panel_lca_class_instance.set_list_db_products(event)
    panel_lca_class_instance.set_dict_db_methods(event)
    widget_autocomplete_product.options = panel_lca_class_instance.list_db_products
    widget_select_method.options = list(panel_lca_class_instance.dict_db_methods.keys())


def button_action_perform_lca(event):
    if widget_autocomplete_product.value == '':
        pn.state.notifications.error('Please select a reference product first!', duration=5000)
        return
    else:
        pn.state.notifications.info('Calculating LCA score...', duration=5000)
        pass
    panel_lca_class_instance.set_chosen_activity(event, widget_autocomplete_product.value)
    panel_lca_class_instance.set_chosen_method(event, widget_select_method.value)
    panel_lca_class_instance.set_chosen_amount(event, widget_float_input_amount.value)
    panel_lca_class_instance.perform_lca(event)
    pn.state.notifications.success('Completed LCA score calculation!', duration=5000)
    widget_number_lca_score.value = panel_lca_class_instance.lca.score


def perform_graph_traversal(event):
    panel_lca_class_instance.perform_graph_traversal(event)
    widget_tabulator.value = panel_lca_class_instance.df_graph_traversal_nodes
    column_editors = {
        colname : {'type': 'editable', 'value': True}
        for colname in panel_lca_class_instance.df_graph_traversal_nodes.columns
        if colname != 'Scope 1?'
    }
    widget_tabulator.editors = column_editors


def perform_scope_analysis(event):
    panel_lca_class_instance.determine_scope_1_and_2_emissions(event)
    panel_lca_class_instance.determine_scope_3_emissions(event)
    widget_plotly_figure_piechart.object = plotting.create_plotly_figure_piechart(panel_lca_class_instance.scope_dict)


def button_action_scope_analysis(event):
    if panel_lca_class_instance.lca is None:
        pn.state.notifications.error('Please perform an LCA Calculation first!', duration=5000)
        return
    else:
        if panel_lca_class_instance.df_graph_traversal_nodes is None:
            pn.state.notifications.info('Performing Graph Traversal...', duration=5000)
            pn.state.notifications.info('Performing Scope Analysis...', duration=5000)
            perform_graph_traversal(event)
            perform_scope_analysis(event)
            pn.state.notifications.success('Graph Traversal Complete!', duration=5000)
            pn.state.notifications.success('Scope Analysis Complete!', duration=5000)
        else:
            panel_lca_class_instance.df_graph_traversal_nodes = widget_tabulator.value
            pn.state.notifications.info('Re-Performing Scope Analysis...', duration=5000)
            perform_scope_analysis(event)
            pn.state.notifications.success('Scope Analysis Complete!', duration=5000)


# https://panel.holoviz.org/reference/widgets/Button.html
widget_button_load_db = pn.widgets.Button( 
    name='Load USEEIO Database',
    icon='database-plus',
    button_type='primary',
    sizing_mode='stretch_width'
)
widget_button_load_db.on_click(button_action_load_database)

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

# https://panel.holoviz.org/reference/widgets/Button.html
widget_button_lca = pn.widgets.Button( 
    name='Compute LCA Score',
    icon='calculator',
    button_type='primary',
    sizing_mode='stretch_width'
)
widget_button_lca.on_click(button_action_perform_lca)

 # https://panel.holoviz.org/reference/widgets/EditableFloatSlider.html
widget_float_slider_cutoff = pn.widgets.EditableFloatSlider(
    name='Graph Traversal Cut-Off [%]',
    start=1,
    end=99,
    step=1,
    value=10,
    sizing_mode='stretch_width'
)

# https://panel.holoviz.org/reference/panes/Markdown.html
markdown_cutoff_documentation = pn.pane.Markdown("""
A cut-off of 10% means that only those processes responsible or 90% of impact will be computed. A lower cut-off therefore results in a longer calculation, which yields a larger amount of processes.
""")
        
# https://panel.holoviz.org/reference/widgets/Button.html
widget_button_graph = pn.widgets.Button(
    name='Perform Scope Analysis',
    icon='chart-donut-3',
    button_type='primary',
    sizing_mode='stretch_width'
)
widget_button_graph.on_click(button_action_scope_analysis)

# https://panel.holoviz.org/reference/indicators/Number.html
widget_number_lca_score = pn.indicators.Number(
    name='LCA Score',
    font_size='30pt',
    title_size='20pt',
    value=0,
    format='{value:,.5f}',
    margin=0
)

widget_plotly_figure_piechart = pn.pane.Plotly(
    plotting.create_plotly_figure_piechart(
        {'Scope 1': 0}
    )
)

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

# COLUMN 2 ####################################################################

# https://panel.holoviz.org/reference/widgets/Tabulator.html#formatters
from bokeh.models.widgets.tables import BooleanFormatter
widget_tabulator = pn.widgets.Tabulator(
    None,
    theme='site',
    show_index=False,
    selectable=False,
    formatters={'Scope 1?': BooleanFormatter()}, # tick/cross for boolean values
    editors={}, # is set later such that only a single column can be edited
)

col2 = pn.Column(
    '## Table of Upstream Processes',
    widget_tabulator
)

# SITE ######################################################################

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

# https://panel.holoviz.org/tutorials/basic/templates.html
template = pn.template.MaterialTemplate(
    header=header,
    title='Brightway WebApp (Carbon Accounting)',
    header_background='#2d853a', # green
    logo='app/_media/BW_white.svg',
)

# https://panel.holoviz.org/reference/layouts/GridSpec.html
gspec = pn.GridSpec(ncols=3, sizing_mode='stretch_both')
gspec[:,0:1] = col1 # 1/3rd of the width
gspec[:,1:3] = col2 # 2/3rds of the width

template.main.append(gspec)
template.servable()