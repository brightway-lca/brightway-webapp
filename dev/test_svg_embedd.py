# %%
import panel as pn

svg_pane = pn.pane.SVG(
    'https://raw.githubusercontent.com/brightway-lca/brightway-webapp/branch_feature/app/PSI%2BETHZ%2BWISER_white.svg',
    height=50,
    align="center"
)

pn.Column(svg_pane).servable()