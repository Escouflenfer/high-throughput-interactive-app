"""
callback functions used in EDX interface.
Internal use for Institut Néel and within the MaMMoS project, to export and read big datasets produced at Institut Néel.

@Author: William Rigaut - Institut Néel (william.rigaut@neel.cnrs.fr)
"""

from dash import Input, Output, callback
from functions import edx


def callbacks_edx(app, children_edx):
    # EDX components update
    @app.callback(Output("element_edx", "options"), Input("folderpath", "value"))
    def update_element_edx(folderpath):
        element_edx_opt = []
        if folderpath is not None:
            element_edx_opt = edx.get_elements(folderpath)
        return element_edx_opt

    @app.callback(
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

    # EDX heatmap update
    @callback(
        Output("edx_heatmap", "figure"),
        Output("crange_slider", "value"),
        Input("folderpath", "value"),
        Input("element_edx", "value"),
    )
    def update_heatmap_edx(foldername, element_edx):
        fig = edx.generate_heatmap(foldername, element_edx)

        # Update the dimensions of the heatmap and the X-Y title axes
        fig.update_layout(height=600, width=600, clickmode="event+select")
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

    # EDX single spectra update
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
            height=650,
            width=1000,
            annotations=[meta],
        )
        fig.update_xaxes(title="Energy (keV)", range=xrange)
        fig.update_yaxes(title="Counts", range=yrange)
        return fig
