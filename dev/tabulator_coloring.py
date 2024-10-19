# %%
import panel as pn
import pandas as pd
import numpy as np

data_original = {
    'UID': [0, 1, 2, 3, 4, 5, 6],
    'SupplyAmount': [1000, 500, 70, 100, 90, 10, 5],
    'Scope?': [1, 2, 3, 3, 3, 3, 3],
    'Branch': [np.NaN, [0, 1], [0, 1, 2], [0, 3], [0, 1, 2, 4], [0, 1, 2, 4, 5], [0, 1, 2, 4, 5, 6]]
}

df_original = pd.DataFrame(data_original)

pn.extension('tabulator')

tabulator_editors = {col: None for col in df_original.columns if col != 'Scope?'}

tabulator_editors['Scope?'] = {'type': 'list', 'values': [1, 2, 3]}


widget_tabulator = pn.widgets.Tabulator(
    df_original,
    theme='site',
    show_index=False,
    selectable=False,
    #formatters=tabulator_formatters,
    editors=tabulator_editors, # is set later such that only a single column can be edited
    layout='fit_data_stretch',
    sizing_mode='stretch_width'
)

def highlight_cells(s):
    """
    See Also
    --------
    - https://stackoverflow.com/a/48306463
    """
    if s.SupplyAmount == 1000:
        return ['background-color: yellow'] * len(s)

widget_tabulator.style.apply(highlight_cells, axis=1)

pn.Column(widget_tabulator).servable()


def highlight_edited_tabulator_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    def highlight(s):
    if s.duration > 5:
        return ['background-color: yellow'] * len(s)

    https://panel.holoviz.org/reference/widgets/Tabulator.html#styling
    https://stackoverflow.com/a/48306463
    """
    pass