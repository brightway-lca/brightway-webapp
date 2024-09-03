# %%
import panel as pn

pn.extension("plotly")

import plotly

def create_plotly_figure_piechart(data_dict: dict) -> plotly.graph_objects.Figure:
    dict_colors={
        'Scope 1': '##16db89',
        'Scope 2': '#00d1e4',
        'Scope 3': '#ffd96b'
    }
    plotly_figure = plotly.graph_objects.Figure(
        data=[
            plotly.graph_objects.Pie(
                labels=[label for label in data_dict.keys()],
                values=[value for value in data_dict.values()]
            )
        ]
    )
    plotly_figure.update_traces(
        marker=dict(
            colors=[color for color in dict_colors.values()],
            line=dict(color='#000000', width=2)
        )
    )
    plotly_figure.update_layout(
        autosize=True,
        height=300,
        legend=dict(
            orientation="v",
            yanchor="auto",
            y=1,
            xanchor="right",
            x=-0.3
        ),
        margin=dict(
            l=50,
            r=50,
            b=0,
            t=0,
            pad=0
        ),
    )

    
    return plotly_figure