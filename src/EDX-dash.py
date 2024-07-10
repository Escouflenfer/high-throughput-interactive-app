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
    className="cell11",
)
# Folderpath for the EDX map
W_folderpath_edx = html.Div(
    children=[
        html.Label("Folderpath"),
        dcc.Dropdown(
            [elm for elm in os.listdir("./data/EDX/") if not elm.startswith(".")],
            id="folderpath_edx",
        ),
    ],
    className="cell11",
)
# Element component
W_element = html.Div(
    children=[html.Label("Element"), dcc.Dropdown([], id="element_edx")],
    className="cell21",
)
# Slider X component
W_x_slider = html.Div(
    children=[
        html.Label("X Position"),
        dcc.Slider(min=-40, max=40, step=5, value=0, id="x_slider"),
    ],
    className="cell12",
)
# Slider Y component
W_y_slider = html.Div(
    children=[
        html.Label("Y Position"),
        dcc.Slider(min=-40, max=40, step=5, value=0, id="y_slider"),
    ],
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
# EDX spectra graph that will be modified by user interaction
W_edx_spectra = html.Div([dcc.Graph(id="edx_spectra")], className="plot_cell")
# EDX heatmap
W_edx_heatmap = html.Div([dcc.Graph(id="edx_heatmap")], className="plot_cell")

# App initialization
app = Dash(__name__)

# Defining the main window layout
app.layout = html.Div(
    [
        dcc.Tabs(
            id="tabs",
            value="tab-1",
            children=[
                dcc.Tab(
                    id="tab-1",
                    label="EDX Spectra",
                    children=[
                        html.Div(
                            [
                                W_folderpath,
                                W_x_slider,
                                W_xrange_slider,
                                W_y_slider,
                                W_yrange_slider,
                                W_edx_spectra,
                            ],
                            className="grid_layout",
                        )
                    ],
                ),
                dcc.Tab(
                    id="tab-2",
                    label="Composition map",
                    children=[
                        html.Div(
                            [W_folderpath_edx, W_element, W_edx_heatmap],
                            className="grid_layout",
                        )
                    ],
                ),
            ],
        )
    ],
    className="window_layout",
)


# Callback on update_graph() when sliders are updated, can be optimized using Patch class from dash module when range sliders are updated
@callback(
    Output("edx_spectra", "figure"),
    Input("folderpath", "value"),
    Input("x_slider", "value"),
    Input("y_slider", "value"),
    Input("xrange_slider", "value"),
    Input("yrange_slider", "value"),
)
def update_graph(foldername, x_pos, y_pos, xrange, yrange):
    """Updating the EDX spectra graph when the user uses a widget and changes its value, the update only appends on_monse_release for sliders.
    The data is read inside an .xml datafile exported by the BRUKER software with the function generate_spectra() in the edx local library

    Parameters
    ----------
    foldername : STR
        Folder that contains all the EDX datafiles in the .xml format
        Used to read data in the correct path
    x_pos, ypos : INT, INT
        Horizontal position X (in mm) and vertical position Y (in mm) on the sample.
        The EDX scan saved the datafiles labeled by two numbers (a, b) corresponding to the scan number in the x and y positions
    xrange, yrange : INT, INT
        Ranges for the axes of the plot from sliders value

    Returns
    -------
    fig : Figure
        Figure object from plotly.graph_objects
    """
    fig = edx.generate_spectra(foldername, x_pos, y_pos)
    fig.update_xaxes(title="Energy (keV)", range=xrange)
    fig.update_yaxes(title="Counts", range=yrange)
    return fig


@callback(
    Output("edx_heatmap", "figure"),
    Input("folderpath", "value"),
    Input("element_edx", "value"),
)
def update_heatmap(folderpath_edx, element_edx):
    fig = edx.generate_heatmap(folderpath_edx, element_edx)
    fig.update_xaxes(title="X Position")
    fig.update_yaxes(title="Y Position")
    fig.data[0].colorbar.title = "Conctr. at.%"
    return fig


@callback(
    Output("folderpath", "value"),
    Output("folderpath_edx", "value"),
    Output("element_edx", "options"),
    Output("element_edx", "value"),
    Input("tabs", "value"),
    Input("folderpath", "value"),
    Input("folderpath_edx", "value"),
    Input("element_edx", "options"),
    Input("element_edx", "value"),
)
def update_on_tab_change(
    tab, folderpath, folderpath_edx, element_edx_opt, element_edx_val
):
    if tab == "tab-1":
        folderpath_edx = folderpath
    elif tab == "tab-2":
        element_edx_opt = edx.get_elements(folderpath_edx)
        if element_edx_val is None and len(element_edx_opt) > 0:
            element_edx_val = element_edx_opt[0]
        folderpath = folderpath_edx
    return folderpath, folderpath_edx, element_edx_opt, element_edx_val


if __name__ == "__main__":
    app.run(debug=True)
