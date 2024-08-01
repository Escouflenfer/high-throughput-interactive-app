"""
Interactive Plots codes using dash module to detach it completely from Jupyter Notebooks.
Internal use for Institut Néel and within the MaMMoS project, to read big datasets produced at Institut Néel.

@Author: William Rigaut - Institut Néel (william.rigaut@neel.cnrs.fr)
"""

from dash import Dash, html, dcc, Input, Output, callback
from interface import widgets_edx, widgets_moke
from internal_functions import edx, moke

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
            children=[edx_tab, moke_tab],
        )
    ],
    className="window_layout",
)


# Component updates
# EDX components
@callback(Output("element_edx", "options"), Input("folderpath", "value"))
def update_element_edx(folderpath):
    element_edx_opt = []
    if folderpath is not None:
        element_edx_opt = edx.get_elements(folderpath)
    return element_edx_opt


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


# MOKE components
@callback(
    Output(children_moke.subfolder_id, "options"),
    Input(children_moke.folderpath_id, "value"),
)
def update_subfolder_moke(folderpath):
    subfolder_options = []
    if folderpath is not None:
        subfolder_options = moke.get_subfolders(
            folderpath, moke_path=children_moke.folderpath_dataPath
        )

    return subfolder_options


@callback(
    Output("moke", "children"),
    Input(children_moke.data_type_id, "value"),
    Input(children_moke.folderpath_id, "value"),
    Input(children_moke.subfolder_id, "value"),
)
def update_sliders_moke(data_type, folderpath, subfolder):
    print(data_type, children_moke.data_type_value)
    if children_moke.data_type_value == data_type:
        return children_moke
    else:
        children_moke.data_type_value = data_type

    new_children_moke = widgets_moke.WidgetsMOKE()
    new_children_moke.folderpath_value = folderpath
    new_children_moke.subfolder_options = update_subfolder_moke(folderpath)
    new_children_moke.subfolder_value = subfolder

    if data_type == "Magnetic properties":
        new_children_moke.set_properties_to_magnetic()

    elif data_type == "Raw MOKE data":
        new_children_moke.set_properties_to_raw()

    return new_children_moke.get_children()


# Heatmap updates
#   EDX
@callback(
    Output("edx_heatmap", "figure"),
    Output("crange_slider", "value"),
    Input("folderpath", "value"),
    Input("element_edx", "value"),
)
def update_heatmap_edx(foldername, element_edx):
    fig = edx.generate_heatmap(foldername, element_edx)

    # Update the dimensions of the heatmap and the X-Y title axes
    fig.update_layout(height=750, width=750, clickmode="event+select")
    fig.update_xaxes(title="X Position")
    fig.update_yaxes(title="Y Position")

    # Update the colorbar title
    fig.data[0].colorbar = dict(title="Conctr. at.%")

    # Update the colorbar range
    crange = [0, 100]
    if foldername is not None and element_edx is not None:
        z_values = fig.data[0].z
        crange = [min(z_values), max(z_values)]

    return fig, crange


#   MOKE
@callback(
    Output(children_moke.moke_heatmap_id, "figure"),
    Input(children_moke.folderpath_id, "value"),
    Input(children_moke.subfolder_id, "value"),
    Input(children_moke.data_type_id, "value"),
)
def update_heatmap_moke(foldername, subfolder, datatype):
    fig, header_data = moke.plot_moke_heatmap(foldername, subfolder, datatype)
    # Update the dimensions of the heatmap and the X-Y title axes
    fig.update_layout(height=750, width=750, clickmode="event+select")
    fig.update_xaxes(title="X Position")
    fig.update_yaxes(title="Y Position")

    fig.data[0].colorbar = dict(title=header_data)

    return fig


# Single graph updates
#   EDX spectra
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


#   MOKE data
@callback(
    Output(children_moke.moke_loop_id, "figure"),
    Input(children_moke.folderpath_id, "value"),
    Input(children_moke.subfolder_id, "value"),
    Input(children_moke.moke_heatmap_id, "clickData"),
    Input(children_moke.xrange_slider_id, "value"),
    Input(children_moke.yrange_slider_id, "value"),
    Input(children_moke.data_type_id, "value"),
)
def update_moke_data(foldername, subfolder, clickData, xrange, yrange, data_type):
    if clickData is None:
        x_pos, y_pos = 0, 0
    else:
        x_pos = int(clickData["points"][0]["x"])
        y_pos = int(clickData["points"][0]["y"])

    fig = moke.plot_1D_with_datatype(foldername, subfolder, x_pos, y_pos, data_type)

    fig.update_layout(
        height=750,
        width=1100,
        title=f"MOKE Signal for {subfolder} at position ({x_pos}, {y_pos})",
    )
    fig.update_xaxes(title="Time (μs)", range=xrange)
    fig.update_yaxes(title="Kerr Rotation (V)", range=yrange)

    return fig


# Run app
if __name__ == "__main__":
    app.run(debug=True)
