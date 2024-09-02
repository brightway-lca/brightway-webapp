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

# COLUMN 3

diagram = pn.pane.SVG(
    'app/_media/scope_splitting.svg',
    alt_text='Diagrammatic Illustration of Scope Splitting',
    link_url='https://en.wikipedia.org/wiki/Carbon_accounting',
    width=500,
)

documentation_markdown_top = pn.pane.Markdown("""

## Some Sub-Heading
                                              
The [WISER Project](https://wiser-climate.com)

""")

col3 = pn.Column(
    '# Documentation',
    documentation_markdown_top,
    diagram,
    styles=dict(background='WhiteSmoke')
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

gspec = pn.GridSpec(ncols=3, sizing_mode='stretch_both')
gspec[:,0] = dial
gspec[:,1] = col3
gspec[:,2] = pn.Spacer(styles=dict(background='red'))

template = pn.template.MaterialTemplate(
    header=header,
    title='Brightway WebApp (Carbon Accounting)',
    header_background='#2d853a',
    logo='app/_media/BW_white.svg',
)

template.main.append(
    gspec
)

template.servable()

# https://panel.holoviz.org/reference/layouts/Column.html
#pn.Column(
#    dial
#).servable()