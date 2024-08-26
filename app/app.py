# %%
import panel as pn
from panel import HSpacer, Spacer

pn.extension()

import bw2data as bd
import bw2io as bi
import bw2calc as bc

# workaround
import os
os.environ["BRIGHTWAY_DIR"] = "/tmp/"

# minimum working example of a
# life-cycle assessment calculation with Brightway

def recreate_fresh_project(project_name):
    try:
        bd.projects.delete_project(project_name, delete_dir=True)
    except:
        pass
    bd.projects.create_project(project_name)
    bd.projects.set_current(project_name)

recreate_fresh_project(project_name = "bw_panel")

bi.add_example_database(searchable=False)
co2 = bd.get_node(name="CO2")
gwp = bd.Method(("GWP", "simple"))
gwp.write([(co2.key, 1)])
lca = bc.LCA({bd.get_node(name="Electric car"):1}, method=("GWP", "simple"))
lca.lci()
lca.lcia()
lca_score = lca.score

# minimum working example of a
# Panel app with a button and a text widget

dial = pn.indicators.Dial(
    name='CO2 [kg]',
    value=lca_score,
    format='{value:,.0f}kg',
    bounds=(0, 5000)
)

# https://panel.holoviz.org/tutorials/basic/templates.html

logos = pn.pane.SVG(
    'app/_media/PSI+ETHZ_white.svg',
    height=50,
    margin=0,
    sizing_mode="fixed",
    align="center"
)
header = pn.Row(
    pn.pane.SVG(
        'app/_media/BW_white.svg',
        height=60,
        margin=0,
        sizing_mode="fixed",
        align="center"
    ),
    HSpacer(),
    pn.pane.SVG(
        'app/_media/PSI+ETHZ+WISER_white.svg',
        height=50,
        margin=0,
        sizing_mode="fixed",
        align="center"
    ),
    sizing_mode="stretch_width",
)


template = pn.template.MaterialTemplate(
    header=header,
    title='Brightway WebApp',
    sidebar=[],
    header_background = '#2d853a'
)

template.main.append(
    pn.Row(
        dial
    )
)

template.servable()

# https://panel.holoviz.org/reference/layouts/Column.html
#pn.Column(
#    dial
#).servable()