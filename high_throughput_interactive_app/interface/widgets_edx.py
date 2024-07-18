import os
from dash import html, dcc


class WidgetsEDX:
    folderpath_dataPath = "./data/EDX/"
    folderpath_className = "cell12"

    element_className = "cell22"

    xrange_slider_min = 0
    xrange_slider_max = 20
    xrange_slider_step = 0.1
    xrange_slider_value = [0, 10]
    xrange_slider_markStep = 5
    xrange_slider_className = "cell13"

    yrange_slider_min = 0
    yrange_slider_max = 50000
    yrange_slider_step = 1000
    yrange_slider_value = [0, 10000]
    yrange_slider_markStep = 10000
    yrange_slider_className = "cell23"

    crange_slider_min = 0
    crange_slider_max = 100
    crange_slider_step = 0.1
    crange_slider_value = [0, 100]
    crange_slider_markStep = 5
    crange_slider_className = "cell21"

    edx_spectra_className = "plot_cell_right"

    edx_heatmap_className = "plot_cell_left"

    def __init__(self):
        # Folderpath for the EDX spetras
        self.folderpath = html.Div(
            children=[
                html.Label("Folderpath"),
                dcc.Dropdown(
                    [
                        elm
                        for elm in os.listdir(self.folderpath_dataPath)
                        if not elm.startswith(".")
                    ],
                    id="folderpath",
                ),
            ],
            className=self.folderpath_className,
        )

        # Element component
        self.element = html.Div(
            children=[html.Label("Element"), dcc.Dropdown([], id="element_edx")],
            className=self.element_className,
        )

        # Slider Xrange component
        self.xrange_slider = html.Div(
            children=[
                html.Label("Energy Range"),
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
                    id="xrange_slider",
                ),
            ],
            className=self.xrange_slider_className,
        )

        # Slider Yrange component
        self.yrange_slider = html.Div(
            children=[
                html.Label("Counts"),
                dcc.RangeSlider(
                    min=self.yrange_slider_min,
                    max=self.yrange_slider_max,
                    step=self.yrange_slider_step,
                    value=self.yrange_slider_value,
                    marks={
                        i: f"{i}"
                        for i in range(
                            self.yrange_slider_min,
                            self.yrange_slider_max + self.yrange_slider_markStep,
                            self.yrange_slider_markStep,
                        )
                    },
                    id="yrange_slider",
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
                        for i in range(
                            self.crange_slider_min,
                            self.crange_slider_max + self.crange_slider_markStep,
                            self.crange_slider_markStep,
                        )
                    },
                    id="crange_slider",
                ),
            ],
            className="cell21",
        )

        # EDX spectra graph that will be modified by user interaction
        self.edx_spectra = html.Div(
            [dcc.Graph(id="edx_spectra")], className=self.edx_spectra_className
        )

        # EDX heatmap
        self.edx_heatmap = html.Div(
            [dcc.Graph(id="edx_heatmap")], className=self.edx_heatmap_className
        )
