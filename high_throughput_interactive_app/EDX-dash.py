"""
Interactive Plots codes using dash module to detach it completely from Jupyter Notebooks.
Internal use for Institut Néel and within the MaMMoS project, to read big datasets produced at Institut Néel.

@Author: William Rigaut - Institut Néel (william.rigaut@neel.cnrs.fr)
"""

import os
from dash import Dash, html, dcc, Input, Output, callback
from internal_functions import edx

# Defining all the layout components
# Folderpath for the EDX spetras (component defined inside a <div>)
W_folderpath = html.Div(
    children=[
        html.Label("Folderpath"),
        dcc.Dropdown(
            [elm for elm in os.listdir("./data/EDX/") if not elm.startswith(".")],
            id="folderpath",
        ),
    ],
    className="cell12",
)
# Element component
W_element = html.Div(
    children=[html.Label("Element"), dcc.Dropdown([], id="element_edx")],
    className="cell22",
)
# Slider Xrange component
W_xrange_slider = html.Div(
    children=[
        html.Label("Energy Range"),
        dcc.RangeSlider(
            min=0,
            max=20,
            step=0.1,
            value=[0, 10],
            marks={i: f"{i}" for i in range(0, 25, 5)},
            id="xrange_slider",
        ),
    ],
    className="cell13",
)
# Slider Yrange component
W_yrange_slider = html.Div(
    children=[
        html.Label("Counts"),
        dcc.RangeSlider(
            min=0,
            max=50000,
            step=1000,
            value=[0, 15000],
            marks={i: f"{i}" for i in range(0, 60000, 10000)},
            id="yrange_slider",
        ),
    ],
    className="cell23",
)
W_crange_slider = html.Div(
    children=[
        html.Label("Color Range"),
        dcc.RangeSlider(
            min=0,
            max=100,
            step=0.5,
            value=[0, 100],
            marks={i: f"{i}" for i in range(0, 105, 5)},
            id="crange_slider",
        ),
    ],
    className="cell21",
)
# EDX spectra graph that will be modified by user interaction
W_edx_spectra = html.Div([dcc.Graph(id="edx_spectra")], className="plot_cell_right")
# EDX heatmap
W_edx_heatmap = html.Div([dcc.Graph(id="edx_heatmap")], className="plot_cell_left")

# EDX tab with all the components
edx_tab = dcc.Tab(
    id="tab-1",
    label="EDX",
    children=[
        html.Div(
            [
                W_folderpath,
                W_element,
                W_crange_slider,
                W_xrange_slider,
                W_yrange_slider,
                W_edx_heatmap,
                W_edx_spectra,
            ],
            className="grid_layout",
        )
    ],
)

# App initialization
app = Dash(__name__)

# Defining the main window layout
app.layout = html.Div(
    [
        dcc.Tabs(
            id="tabs",
            value="tab-1",
            children=[edx_tab],
        )
    ],
    className="window_layout",
)


@callback(Output("element_edx", "options"), Input("folderpath", "value"))
def update_components(foldername):
    element_edx_opt = []
    if foldername is not None:
        element_edx_opt = edx.get_elements(foldername)
    return element_edx_opt


@callback(
    Output("edx_heatmap", "figure"),
    Input("folderpath", "value"),
    Input("element_edx", "value"),
)
def update_heatmap(folderpath_edx, element_edx):
    fig = edx.generate_heatmap(folderpath_edx, element_edx)
    fig.update_layout(height=750, width=750, clickmode="event+select")
    fig.update_xaxes(title="X Position")
    fig.update_yaxes(title="Y Position")
    fig.data[0].colorbar.title = "Conctr. at.%"
    return fig


@callback(
    Output("edx_spectra", "figure"),
    Input("folderpath", "value"),
    Input("edx_heatmap", "clickData"),
    Input("xrange_slider", "value"),
    Input("yrange_slider", "value"),
)
def update_spectra(foldername, clickData, xrange, yrange):
    if clickData is None:
        x_pos, y_pos = 0, 0
    else:
        x_pos = int(clickData["points"][0]["x"])
        y_pos = int(clickData["points"][0]["y"])
    fig = edx.generate_spectra(foldername, x_pos, y_pos)
    fig.update_layout(height=750, width=1100)
    fig.update_xaxes(title="Energy (keV)", range=xrange)
    fig.update_yaxes(title="Counts", range=yrange)
    return fig


if __name__ == "__main__":
    app.run(debug=True)
