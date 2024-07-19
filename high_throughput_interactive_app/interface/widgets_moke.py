"""
class file for edx widgets using dash module to detach it completely from Jupyter Notebooks.
Internal use for Institut Néel and within the MaMMoS project, to read big datasets produced at Institut Néel.

@Author: William Rigaut - Institut Néel (william.rigaut@neel.cnrs.fr)
"""

import os
from dash import html, dcc
from itertools import count, takewhile


def frange(start, stop, step):
    return takewhile(lambda x: x < stop, count(start, step))


class WidgetsMOKE:
    folderpath_id = "moke_folderpath"
    folderpath_dataPath = "./data/MOKE/"
    folderpath_className = "moke_cell12"

    subfolder_id = "moke_subfolder"
    subfolderpath_className = "moke_cell22"

    xrange_slider_id = "moke_xrange_slider"
    xrange_slider_min = 0
    xrange_slider_max = 100
    xrange_slider_step = 1
    xrange_slider_value = [0, 100]
    xrange_slider_markStep = 10
    xrange_slider_className = "moke_cell13"

    yrange_slider_id = "moke_yrange_slider"
    yrange_slider_min = -1
    yrange_slider_max = 1
    yrange_slider_step = 0.01
    yrange_slider_value = [-0.5, 0.5]
    yrange_slider_markStep = 0.5
    yrange_slider_className = "moke_cell23"

    crange_slider_id = "moke_crange_slider"
    crange_slider_min = 0
    crange_slider_max = 10
    crange_slider_step = 0.1
    crange_slider_value = [0, 3]
    crange_slider_markStep = 2
    crange_slider_className = "moke_cell11"

    moke_loop_id = "moke_loop"
    moke_loop_className = "moke_loop_plot_cell"

    moke_heatmap_id = "moke_heatmap"
    moke_heatmap_className = "moke_heatmap_plot_cell"

    def __init__(self):
        # Folderpath for the MOKE loop
        self.folderpath = html.Div(
            children=[
                html.Label("Folderpath"),
                dcc.Dropdown(
                    [
                        elm
                        for elm in os.listdir(self.folderpath_dataPath)
                        if not elm.startswith(".")
                    ],
                    id=self.folderpath_id,
                ),
            ],
            className=self.folderpath_className,
        )

        # Element component
        self.subfolder = html.Div(
            children=[html.Label("Subfolder"), dcc.Dropdown([], id=self.subfolder_id)],
            className=self.subfolderpath_className,
        )

        # Slider Xrange component
        self.xrange_slider = html.Div(
            children=[
                html.Label("Time"),
                dcc.RangeSlider(
                    min=self.xrange_slider_min,
                    max=self.xrange_slider_max,
                    step=self.xrange_slider_step,
                    value=self.xrange_slider_value,
                    marks={
                        i: f"{i}"
                        for i in range(
                            self.xrange_slider_min,
                            self.xrange_slider_max + self.xrange_slider_markStep,
                            self.xrange_slider_markStep,
                        )
                    },
                    id=self.xrange_slider_id,
                ),
            ],
            className=self.xrange_slider_className,
        )

        # Slider Yrange component
        self.yrange_slider = html.Div(
            children=[
                html.Label("Kerr Rotation"),
                dcc.RangeSlider(
                    min=self.yrange_slider_min,
                    max=self.yrange_slider_max,
                    step=self.yrange_slider_step,
                    value=self.yrange_slider_value,
                    marks={
                        i: f"{i}"
                        for i in frange(
                            self.yrange_slider_min,
                            self.yrange_slider_max + self.yrange_slider_markStep,
                            self.yrange_slider_markStep,
                        )
                    },
                    id=self.yrange_slider_id,
                ),
            ],
            className=self.yrange_slider_className,
        )

        # Colorange for heatmap
        self.crange_slider = html.Div(
            children=[
                html.Label("Color Range"),
                dcc.RangeSlider(
                    min=self.crange_slider_min,
                    max=self.crange_slider_max,
                    step=self.crange_slider_step,
                    value=self.crange_slider_value,
                    marks={
                        i: f"{i}"
                        for i in frange(
                            self.crange_slider_min,
                            self.crange_slider_max + self.crange_slider_markStep,
                            self.crange_slider_markStep,
                        )
                    },
                    id=self.crange_slider_id,
                ),
            ],
            className=self.crange_slider_className,
        )

        # EDX spectra graph that will be modified by user interaction
        self.moke_loop = html.Div(
            [dcc.Graph(id=self.moke_loop_id)], className=self.moke_loop_className
        )

        # EDX heatmap
        self.moke_heatmap = html.Div(
            [dcc.Graph(id=self.moke_heatmap_id)], className=self.moke_heatmap_className
        )

    def make_tab_from_widgets(
        self,
        id_moke="moke",
        label_moke="MOKE",
        value_moke="moke",
        className_moke="grid_layout_moke",
    ):
        moke_tab = dcc.Tab(
            id=id_moke,
            label=label_moke,
            value=value_moke,
            children=[
                html.Div(
                    [
                        self.folderpath,
                        self.subfolder,
                        self.crange_slider,
                        self.xrange_slider,
                        self.yrange_slider,
                        self.moke_loop,
                        self.moke_heatmap,
                    ],
                    className=className_moke,
                )
            ],
        )

        return moke_tab
