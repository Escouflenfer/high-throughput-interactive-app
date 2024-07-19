"""
Interactive Plots codes using dash module to detach it completely from Jupyter Notebooks.
Internal use for Institut Néel and within the MaMMoS project, to read big datasets produced at Institut Néel.

@Author: William Rigaut - Institut Néel (william.rigaut@neel.cnrs.fr)
"""

from dash import Dash, html, dcc, Input, Output, callback
from interface import widgets_edx, widgets_moke
from internal_functions import edx

# EDX tab with all the components
children_edx = widgets_edx.WidgetsEDX()
edx_tab = children_edx.make_tab_from_widgets()

# MOKE tab
children_moke = widgets_moke.WidgetsMOKE()
moke_tab = children_moke.make_tab_from_widgets()

# App initialization
app = Dash(__name__)

# Defining the main window layout
app.layout = html.Div(
    [
        dcc.Tabs(
            id="tabs",
            value="edx",
            children=[edx_tab],
        )
    ],
    className="window_layout",
)


# Update element_edx widget when olderpath is changed by the user
@callback(Output("element_edx", "options"), Input("folderpath", "value"))
def update_element_edx(folderpath):
    element_edx_opt = []
    if folderpath is not None:
        element_edx_opt = edx.get_elements(folderpath)
    return element_edx_opt


# Update crange_slider widget when olderpath or element_edx is changed by the user
@callback(
    Output("edx_heatmap", "figure", allow_duplicate=True),
    Input("folderpath", "value"),
    Input("element_edx", "value"),
    Input("edx_heatmap", "figure"),
    Input("crange_slider", "value"),
    prevent_initial_call=True,
)
def update_crange_slider(folderpath, element_edx, fig, crange):
    if folderpath is not None and element_edx is not None:
        fig["data"][0]["zmin"] = min(crange)
        fig["data"][0]["zmax"] = max(crange)

    return fig


@callback(
    Output("edx_heatmap", "figure"),
    Output("crange_slider", "value"),
    Input("folderpath", "value"),
    Input("element_edx", "value"),
)
def update_heatmap(folderpath, element_edx):
    fig = edx.generate_heatmap(folderpath, element_edx)

    # Update the dimensions of the heatmap and the X-Y title axes
    fig.update_layout(height=750, width=750, clickmode="event+select")
    fig.update_xaxes(title="X Position")
    fig.update_yaxes(title="Y Position")

    # Update the colorbar title
    fig.data[0].colorbar = dict(title="Conctr. at.%")

    # Update the colorbar range
    crange = [0, 100]
    if folderpath is not None and element_edx is not None:
        z_values = fig.data[0].z
        crange = [min(z_values), max(z_values)]

    return fig, crange


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

    fig, meta = edx.generate_spectra(foldername, x_pos, y_pos)
    fig.update_layout(
        title=f"EDX Spectrum for {foldername} at position ({x_pos}, {y_pos})",
        height=750,
        width=1100,
        annotations=[meta],
    )
    fig.update_xaxes(title="Energy (keV)", range=xrange)
    fig.update_yaxes(title="Counts", range=yrange)
    return fig


if __name__ == "__main__":
    app.run(debug=True)
