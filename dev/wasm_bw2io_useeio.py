# %%
import panel as pn

import os
import bw2io as bi
import bw2calc as bc
import bw2data as bd

os.environ["BRIGHTWAY_DIR"] = "/tmp/"

def load_useeio_database(event):
    try:
        bd.projects.delete_project('USEEIO-1.1', delete_dir=True)
    except:
        pass
    bi.install_project(project_key="USEEIO-1.1", overwrite_existing=True)
    bd.projects.set_current("USEEIO-1.1")


def perform_lca(event):
    useeio = bd.Database('USEEIO-1.1')
    list_prod = [node for node in useeio if 'product' in node['type']]
    some_prod = list_prod[42]
    lca = bc.LCA( 
        demand={some_prod: 100}, 
        method = bd.methods.random()
    )
    lca.lci()
    lca.lcia()
    number_lca_score.value = lca.score


button_load = pn.widgets.Button(name='Load USEEIO')
button_load.on_click(load_useeio_database)

button_lca = pn.widgets.Button(name='Perform LCA')
button_lca.on_click(perform_lca)

number_lca_score = pn.indicators.Number(name='LCA Score', value=0)

pn.Column(button_load, button_lca, number_lca_score).servable()