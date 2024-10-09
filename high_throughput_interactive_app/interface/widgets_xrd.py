"""
class file for xrd widgets using dash module to detach it completely from Jupyter Notebooks.
Internal use for Institut Néel and within the MaMMoS project, to read big datasets produced at Institut Néel.

@Author: William Rigaut - Institut Néel (william.rigaut@neel.cnrs.fr)
"""

import os
from dash import html, dcc
from itertools import count, takewhile


def frange(start, stop, step):
    """
    frange(start, stop, step) -> generator

    Generate a sequence of numbers over a specified range.
    Like the built-in range() function, but returns a generator
    instead of a list. Used for floating-point ranges.

    Parameters
    ----------
        start (int or float): The first number in the sequence.
        stop (int or float): The sequence stops before this number.
        step (int or float): The difference between each number in the sequence.

    Returns
    ----------
        The next number in the sequence.
    """
    return takewhile(lambda x: x < stop, count(start, step))


class WidgetsXRD:
    folderpath_id = "xrd_folderpath"
    folderpath_value = None
    folderpath_label = "Folderpath"
    folderpath_dataPath = "./data/XRD/"
    folderpath_className = "xrd_cell12"

    browse_button_id = "xrd_browse_button"
    browse_button_label = "Browse"
    browse_button_className = "xrd_cell22"

    xrange_slider_id = "xrd_xrange_slider"
    xrange_slider_label = "2Theta (°)"
    xrange_slider_min = 0
    xrange_slider_max = 100
    xrange_slider_step = 1
    xrange_slider_value = [20, 70]
    xrange_slider_markStep = 10
    xrange_slider_className = "xrd_cell13"

    yrange_slider_id = "xrd_yrange_slider"
    yrange_slider_label = "Counts"
    yrange_slider_min = -25000
    yrange_slider_max = 200000
    yrange_slider_step = 1000
    yrange_slider_value = [-4000, 30000]
    yrange_slider_markStep = 25000
    yrange_slider_className = "xrd_cell23"

    crange_slider_id = "xrd_crange_slider"
    crange_slider_label = "None"
    crange_slider_min = 0
    crange_slider_max = 10
    crange_slider_step = 0.1
    crange_slider_value = [0, 3]
    crange_slider_markStep = 2
    crange_slider_className = "xrd_cell21"

    data_type_id = "xrd_refined_type"
    data_type_label = "Refined Parameter"
    data_type_value = None
    data_type_className = "xrd_cell11"

    xrd_pattern_id = "xrd_pattern"
    xrd_pattern_className = "xrd_pattern_plot_cell"

    xrd_heatmap_id = "xrd_heatmap"
    xrd_heatmap_className = "xrd_heatmap_plot_cell"

    def __init__(self):
        """
        Initialization of the XRD widgets.

        Creates all the components needed for the XRD interactive tab:
        - Folderpath dropdown
        - Browse button
        - Slider Xrange
        - Slider Yrange
        - Colorange for heatmap
        - Dropdown for data type
        - XRD spectra graph
        - XRD heatmap
        """
        # Folderpath for the xrd pattern
        self.folderpath = html.Div(
            children=[
                html.Label(self.folderpath_label),
                dcc.Dropdown(
                    [
                        elm
                        for elm in os.listdir(self.folderpath_dataPath)
                        if not elm.startswith(".")
                    ],
                    value=self.folderpath_value,
                    id=self.folderpath_id,
                ),
            ],
            className=self.folderpath_className,
        )

        # Browse button component
        self.browse_button = html.Div(
            children=[
                html.Button(self.browse_button_label, id=self.browse_button_id),
            ],
            className=self.browse_button_className,
        )

        # Slider Xrange component
        self.xrange_slider = html.Div(
            children=[
                html.Label(self.xrange_slider_label),
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
                html.Label(self.yrange_slider_label),
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
                html.Label(self.crange_slider_label),
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

        self.data_type = html.Div(
            children=[
                html.Label(self.data_type_label),
                dcc.Dropdown(
                    options=[],
                    value=self.data_type_value,
                    id=self.data_type_id,
                ),
            ],
            className=self.data_type_className,
        )

        # XRD spectra graph that will be modified by user interaction
        self.xrd_pattern = html.Div(
            [dcc.Graph(id=self.xrd_pattern_id)], className=self.xrd_pattern_className
        )

        # XRD heatmap
        self.xrd_heatmap = html.Div(
            [dcc.Graph(id=self.xrd_heatmap_id)], className=self.xrd_heatmap_className
        )

    def get_children(self, className_moke="grid_layout_xrd"):
        """
        Return a Div containing all the components of the XRD widget.

        Parameters
        ----------
        className_moke : str, optional
            The className of the Div. Defaults to "grid_layout_xrd".

        Returns
        -------
        children : Dash Div
            A Div containing all the components of the XRD widget.
        """
        children = html.Div(
            [
                self.folderpath,
                self.crange_slider,
                self.xrange_slider,
                self.yrange_slider,
                self.data_type,
                self.browse_button,
                self.xrd_loop,
                self.xrd_heatmap,
            ],
            className=className_moke,
        )

        return children

    def make_tab_from_widgets(
        self,
        id_xrd="xrd",
        label_xrd="XRD",
        value_xrd="xrd",
        className_xrd="grid_layout_xrd",
    ):
        """
        Return a dcc.Tab containing all the components of the XRD widget.

        Parameters
        ----------
        id_xrd : str, optional
            The id of the dcc.Tab. Defaults to "xrd".
        label_xrd : str, optional
            The label of the dcc.Tab. Defaults to "XRD".
        value_xrd : str, optional
            The value of the dcc.Tab. Defaults to "xrd".
        className_xrd : str, optional
            The className of the Div containing all the components of the XRD widget.
            Defaults to "grid_layout_xrd".

        Returns
        -------
        xrd_tab : dcc.Tab
            A dcc.Tab containing all the components of the XRD widget.
        """
        xrd_tab = dcc.Tab(
            id=id_xrd,
            label=label_xrd,
            value=value_xrd,
            children=[
                html.Div(
                    [
                        self.folderpath,
                        self.crange_slider,
                        self.xrange_slider,
                        self.yrange_slider,
                        self.data_type,
                        self.browse_button,
                        self.xrd_pattern,
                        self.xrd_heatmap,
                    ],
                    className=className_xrd,
                )
            ],
        )

        return xrd_tab
