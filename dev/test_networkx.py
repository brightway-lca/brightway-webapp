# %%

import networkx as nx
import matplotlib.pyplot as plt

"""
| uid | name  | production |
|-----|-------|------------|
| 1   | car   | 100        |
| 2   | steel | 200        |

| source | target | weight |
|--------|--------|--------|
| 2      | 1      | 0.5    |
"""

G = nx.DiGraph()

G.add_node(1, name='car', production=100)
G.add_node(2, name='steel', production=200)
G.add_edge(1, 2, weight=0.5)

p = figure(
    x_range=(-2, 2),
    y_range=(-2, 2),
    x_axis_location=None,
    y_axis_location=None,
    tools="hover",
    tooltips="index: @index"
)
p.grid.grid_line_color = None

graph = from_networkx(G, nx.spring_layout, scale=1.8, center=(0,0))
p.renderers.append(graph)

graph_renderer = from_networkx(G, nx.circular_layout, scale=1, center=(0, 0))

scatter_glyph = Scatter(size=15, fill_color=Spectral4[0])
graph_renderer.node_renderer.glyph = scatter_glyph
graph_renderer.node_renderer.selection_glyph = scatter_glyph.clone(fill_color=Spectral4[2])
graph_renderer.node_renderer.hover_glyph = scatter_glyph.clone(fill_color=Spectral4[1])

ml_glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=5)
graph_renderer.edge_renderer.glyph = ml_glyph
graph_renderer.edge_renderer.selection_glyph = ml_glyph.clone(line_color=Spectral4[2], line_alpha=1)
graph_renderer.edge_renderer.hover_glyph = ml_glyph.clone(line_color=Spectral4[1], line_width=1)

graph_renderer.selection_policy = EdgesAndLinkedNodes()
graph_renderer.inspection_policy = EdgesAndLinkedNodes()


plot = figure(width=400, height=400, x_range=(-1.2, 1.2), y_range=(-1.2, 1.2),
              x_axis_location=None, y_axis_location=None, toolbar_location=None,
              title="Graph Interaction Demo", background_fill_color="#efefef",
              tooltips="production: @production, weight: @weight")

plot.renderers.append(graph_renderer)


# tooltips="index: @index, club: @club"

show(plot)

# Add some new columns to the node renderer data source
#graph.node_renderer.data_source.data['index'] = list(range(len(G)))
#graph.node_renderer.data_source.data['colors'] = Category20_20

# graph.node_renderer.glyph.update(size=20, fill_color="colors")
#plot.add_tools(HoverTool(tooltips=None), TapTool(), BoxSelectTool())

#graph_renderer.selection_policy = EdgesAndLinkedNodes()
#graph_renderer.inspection_policy = EdgesAndLinkedNodes()

#show(p)


# %%


from bokeh.models import (BoxSelectTool, EdgesAndLinkedNodes, HoverTool,
                          MultiLine, Plot, Range1d, Scatter, TapTool)
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx, show


plot = Plot(width=400, height=400, x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1))
plot.title.text = "Graph Interaction Demonstration"

plot.add_tools(HoverTool(tooltips=None), TapTool(), BoxSelectTool())

graph = from_networkx(G, nx.spring_layout, scale=1.8, center=(0,0))

show(plot)

# %%

scatter_glyph = Scatter(size=15, fill_color=Spectral4[0])
graph_renderer.node_renderer.glyph = scatter_glyph
graph_renderer.node_renderer.selection_glyph = scatter_glyph.clone(fill_color=Spectral4[2])
graph_renderer.node_renderer.hover_glyph = scatter_glyph.clone(fill_color=Spectral4[1])

ml_glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=5)
graph_renderer.edge_renderer.glyph = ml_glyph
graph_renderer.edge_renderer.selection_glyph = ml_glyph.clone(line_color=Spectral4[2], line_alpha=1)
graph_renderer.edge_renderer.hover_glyph = ml_glyph.clone(line_color=Spectral4[1], line_width=1)

graph_renderer.selection_policy = EdgesAndLinkedNodes()
graph_renderer.inspection_policy = EdgesAndLinkedNodes()

plot.renderers.append(graph_renderer)

show(plot)
