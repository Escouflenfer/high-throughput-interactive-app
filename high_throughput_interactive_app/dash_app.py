"""
Interactive Plots codes using dash module to detach it completely from Jupyter Notebooks.
Internal use for Institut Néel and within the MaMMoS project, to read big datasets produced at Institut Néel.

@Author: William Rigaut - Institut Néel (william.rigaut@neel.cnrs.fr)
"""

from dash import Dash, html, dcc
from interface import widgets_edx, widgets_moke, widgets_xrd
from callbacks import callbacks_edx, callbacks_moke, callbacks_xrd

# App initialization
app = Dash(__name__)

# Generating the tabs for the app
children_edx = widgets_edx.WidgetsEDX()
edx_tab = children_edx.make_tab_from_widgets()

children_moke = widgets_moke.WidgetsMOKE()
moke_tab = children_moke.make_tab_from_widgets()

children_xrd = widgets_xrd.WidgetsXRD()
xrd_tab = children_xrd.make_tab_from_widgets()

# Defining the main window layout
app.layout = html.Div(
    [
        dcc.Tabs(
            id="tabs",
            value="edx",
            children=[edx_tab, moke_tab, xrd_tab],
        )
    ],
    className="window_layout",
)


callbacks_edx.callbacks_edx(app, children_edx)
callbacks_moke.callbacks_moke(app, children_moke)
callbacks_xrd.callbacks_xrd(app, children_xrd)

# Run app
if __name__ == "__main__":
    app.run(debug=True)
