"""
callback functions used in XRD interface.
Internal use for Institut Néel and within the MaMMoS project, to export and read big datasets produced at Institut Néel.

@Author: William Rigaut - Institut Néel (william.rigaut@neel.cnrs.fr)
"""

from dash import Input, Output, callback
from functions import xrd
from interface import widgets_xrd


def callbacks_xrd(app, children_xrd):
    # XRD components
    @callback(
        Output(children_xrd.data_type_id, "options"),
        Output(children_xrd.data_type_id, "value"),
        Input(children_xrd.folderpath_id, "value"),
    )
    def update_data_type_options(foldername):
        refinement_options = xrd.check_xrd_refinement(
            foldername, xrd_path="./data/XRD/"
        )

        if refinement_options is not False:
            return (["Raw XRD data"] + refinement_options), "Raw XRD data"
        else:
            return ["Raw XRD data"], "Raw XRD data"

    # XRD heatmap
    @callback(
        Output(children_xrd.xrd_heatmap_id, "figure"),
        Input(children_xrd.folderpath_id, "value"),
        Input(children_xrd.data_type_id, "value"),
    )
    def update_xrd_heatmap(foldername, datatype):
        fig = xrd.plot_xrd_heatmap(foldername, datatype)

        # Update the dimensions of the heatmap and the X-Y title axes
        fig.update_layout(height=600, width=600, clickmode="event+select")
        fig.update_xaxes(title="X Position")
        fig.update_yaxes(title="Y Position")

        fig.data[0].colorbar = dict(title="Lattice (Å)")

        return fig

    # XRD single pattern
    @callback(
        Output(children_xrd.xrd_pattern_id, "figure"),
        Input(children_xrd.folderpath_id, "value"),
        Input(children_xrd.xrd_heatmap_id, "clickData"),
        Input(children_xrd.xrange_slider_id, "value"),
        Input(children_xrd.yrange_slider_id, "value"),
    )
    def update_xrd_pattern(foldername, clickData, xrange, yrange):
        if clickData is None:
            x_pos, y_pos = 0, 0
            xrd_filename = "Areamap_009009.ras"

        else:
            x_pos = int(clickData["points"][0]["x"])
            y_pos = int(clickData["points"][0]["y"])
            xrd_filename = clickData["points"][0]["text"]

        # print(foldername, x_pos, y_pos)
        fig = xrd.plot_xrd_pattern(foldername, xrd_filename, x_pos, y_pos)

        fig.update_layout(
            height=650,
            width=1000,
            title=f"XRD spectra for {foldername} at position ({x_pos}, {y_pos})",
        )
        fig.update_xaxes(title="2Theta (°)", range=xrange)
        fig.update_yaxes(title="Counts", range=yrange)

        return fig
