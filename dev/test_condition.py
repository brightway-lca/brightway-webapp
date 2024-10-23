# %%

import pandas as pd
import panel as pn

pn.extension(notifications=True)
pn.extension('tabulator')

class panel_class:
    def __init__(self):
        self.df_original = pd.DataFrame({
            'SupplyAmount': [1, 2, 3],
        })
        self.df_user = pd.DataFrame()
        self.df_tabulator = pd.DataFrame()

instance_panel_class = panel_class()

instance_panel_class.df_tabulator = instance_panel_class.df_original.copy()

widget_tabulator = pn.widgets.Tabulator(
    instance_panel_class.df_tabulator,
)

def compare_dataframes(event):
    instance_panel_class.df_user = widget_tabulator.value
    if (
        (instance_panel_class.df_original['SupplyAmount'] != instance_panel_class.df_tabulator['SupplyAmount']).any()
    ):
        pn.state.notifications.success('Different!', duration=7000)
    else:
        pn.state.notifications.success('Same!', duration=7000)

button = pn.widgets.Button(name='Compare DataFrames')
button.on_click(compare_dataframes)

pn.Column(widget_tabulator, button).servable()