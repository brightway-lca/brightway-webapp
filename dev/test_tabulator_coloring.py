# %%
import panel as pn
import pandas as pd

pn.extension('tabulator')

data_original = {
    'UID': [0, 1, 2, 3, 4, 5, 6],
    'SupplyAmount': [1000, 500, 70, 100, 90, 10, 5],
    'Scope': [2, 1, 3, 3, 3, 3, 3],
}
df_original = pd.DataFrame(data_original)

data_edited = {
    'UID': [0, 1, 2, 3, 4, 5, 6],
    'SupplyAmount': [1000, 500, 70, 100, 90, 10, 5],
    'Scope': [2, 1, 3, 3, 3, 3, 3],
    'Edited?': [False, True, False, True, False, False, False]
}
df_edited = pd.DataFrame(data_edited)


tabulator_editors = {col: None for col in df_original.columns if col != 'Scope'}
tabulator_editors['Scope'] = {'type': 'list', 'values': [1, 2, 3]}

def highlight_cells(s):
    """
    https://stackoverflow.com/a/48306463
    https://discourse.holoviz.org/t/dynamic-update-of-tabulator-style/
    """
    if s['Edited?'] == True:
        return ['background-color: yellow'] * len(s)
    else:
        return [''] * len(s)

widget_tabulator = pn.widgets.Tabulator(
    df_original,
    theme='site',
    show_index=False,
    selectable=False,
    editors=tabulator_editors,
    layout='fit_data_stretch',
    sizing_mode='stretch_width'
)
widget_tabulator.style.apply(highlight_cells, axis=1)

def update_tabulator(event):
    widget_tabulator.value = df_edited

button_update_tabulator = pn.widgets.Button( 
    name='Update Tabulator',
    button_type='primary',
    sizing_mode='stretch_width'
)
button_update_tabulator.on_click(update_tabulator)

pn.Column(
    button_update_tabulator,
    widget_tabulator
).servable()