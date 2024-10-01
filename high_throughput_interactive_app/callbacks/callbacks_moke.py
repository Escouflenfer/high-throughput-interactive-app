"""
callback functions used in MOKE interface.
Internal use for Institut Néel and within the MaMMoS project, to export and read big datasets produced at Institut Néel.

@Author: William Rigaut - Institut Néel (william.rigaut@neel.cnrs.fr)
"""

from dash import Input, Output, callback
from functions import moke
from interface import widgets_moke


def callbacks_moke(app, children_moke):
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
        Output(children_moke.moke_heatmap_id, "figure", allow_duplicate=True),
        Input(children_moke.folderpath_id, "value"),
        Input(children_moke.subfolder_id, "value"),
        Input(children_moke.moke_heatmap_id, "figure"),
        Input(children_moke.crange_slider_id, "value"),
        prevent_initial_call=True,
    )
    def update_crange_moke(folderpath, subfolder, fig, crange):
        if folderpath is not None and subfolder is not None:
            fig["data"][0]["zmin"] = min(crange)
            fig["data"][0]["zmax"] = max(crange)
        return fig

    @callback(
        Output("moke", "children"),
        Input(children_moke.data_type_id, "value"),
        Input(children_moke.folderpath_id, "value"),
        Input(children_moke.subfolder_id, "value"),
    )
    def update_sliders_moke(data_type, folderpath, subfolder):
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

    # MOKE heatmap
    @callback(
        Output(children_moke.moke_heatmap_id, "figure"),
        Output(children_moke.crange_slider_id, "value"),
        Input(children_moke.folderpath_id, "value"),
        Input(children_moke.subfolder_id, "value"),
        Input(children_moke.data_type_id, "value"),
    )
    def update_heatmap_moke(foldername, subfolder, datatype):
        fig, header_data = moke.plot_moke_heatmap(foldername, subfolder, datatype)

        # Update the dimensions of the heatmap and the X-Y title axes
        fig.update_layout(height=600, width=600, clickmode="event+select")
        fig.update_xaxes(title="X Position")
        fig.update_yaxes(title="Y Position")

        fig.data[0].colorbar = dict(title=header_data)

        crange = [0, 4]
        if foldername is not None and subfolder is not None:
            z_values = fig.data[0].z
            crange = [min(z_values), max(z_values)]

        return fig, crange

    #   MOKE loop
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
            x_pos = float(clickData["points"][0]["x"])
            y_pos = float(clickData["points"][0]["y"])

        fig = moke.plot_1D_with_datatype(foldername, subfolder, x_pos, y_pos, data_type)

        if data_type == "Raw MOKE data":
            moke_title = f"Raw MOKE data for {subfolder} at position ({x_pos}, {y_pos})"
            x_axis_label = "Time (s)"
            y_axis_label = "Kerr Rotation (V)"

        elif data_type == "Magnetic properties":
            moke_title = f"Magnetic loop for {subfolder} at position ({x_pos}, {y_pos})"
            x_axis_label = "Applied Field (T)"
            y_axis_label = "Kerr Rotation (V)"
        else:
            moke_title = f"Select data type first"
            x_axis_label = ""
            y_axis_label = ""

        fig.update_layout(height=650, width=1000, title=moke_title)

        fig.update_xaxes(title=x_axis_label, range=xrange)
        fig.update_yaxes(title=y_axis_label, range=yrange)

        return fig
