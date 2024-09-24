"""
Functions used in MOKE interactive plot using dash module to detach it completely from Jupyter Notebooks.
Internal use for Institut Néel and within the MaMMoS project, to export and read big datasets produced at Institut Néel.

@Author: William Rigaut - Institut Néel (william.rigaut@neel.cnrs.fr)
"""

import os
import pathlib
import numpy as np
import plotly.graph_objects as go


def create_coordinate_map(folderpath, prefix="Areamap", suffix=".ras"):
    """
    Create a list of coordinates from the filenames in folderpath.

    This function opens each file in folderpath and reads  the first two coordinates (X and Y) from the file.
    It does this by looking for the lines that start with "*MEAS_COND_AXIS_POSITION-6" and "*MEAS_COND_AXIS_POSITION-7" in the header

    Returns
    -------
    list
        A list of coordinates. Each coordinate is a list with two elements: [X, Y].
    """
    filelist = [
        file
        for file in os.listdir(folderpath)
        if file.endswith(suffix) and file.startswith(prefix)
    ]
    pos_list = []

    for file in filelist:
        file_path = folderpath.joinpath(file)
        with open(file_path, "r", encoding="iso-8859-1") as f:
            for line in f:
                if line.startswith("*MEAS_COND_AXIS_POSITION-6"):
                    x_pos = float(line.split(" ")[1].split('"')[1])
                elif line.startswith("*MEAS_COND_AXIS_POSITION-7"):
                    y_pos = float(line.split(" ")[1].split('"')[1])
                    break
            pos_list.append([x_pos, y_pos, file])
    return pos_list


def check_xrd_refinement(folderpath, xrd_path="./data/XRD/"):

    return None


def read_xrd_pattern(foldername, xrd_filename, x_pos, y_pos, xrd_path="./data/XRD/"):
    empty_fig = go.Figure(data=go.Heatmap())
    empty_fig.update_layout(height=600, width=600)
    if foldername is None:
        return empty_fig

    fullpath = xrd_path + foldername + "/" + xrd_filename
    xrd_data = []
    try:
        with open(fullpath, "r", encoding="iso-8859-1") as file:
            for line in file:
                if not line.startswith("*"):
                    theta, counts, error = line.split()
                    xrd_data.append([float(theta), float(counts), float(error)])

    except FileNotFoundError:
        print(f"{fullpath} xrd file not found !")
        return empty_fig

    fig = go.Figure(
        data=[
            go.Scatter(
                x=[theta[0] for theta in xrd_data],
                y=[counts[1] for counts in xrd_data],
                marker_color="green",
                name="Counts",
            )
        ]
    )

    return fig


def read_xrd_files(
    foldername,
    xrd_path="./data/XRD/",
):
    fullpath = pathlib.Path(xrd_path + foldername)
    pos_list = create_coordinate_map(fullpath)

    x_pos = [pos[0] for pos in pos_list]
    y_pos = [pos[1] for pos in pos_list]
    xrd_filename = [pos[2] for pos in pos_list]

    return x_pos, y_pos, xrd_filename


def plot_xrd_heatmap(
    foldername,
    datatype,
    xrd_path="./data/XRD/",
    result_xrd_path="./results/XRD/",
):

    datapath = f"{result_xrd_path}"

    empty_fig = go.Figure(data=go.Heatmap())
    empty_fig.update_layout(height=600, width=600)
    if foldername is None:
        return empty_fig

    x_pos, y_pos, xrd_filename = read_xrd_files(foldername, xrd_path)
    if datatype is None:
        z_values = np.zeros(len(x_pos) + len(y_pos))

    fig = go.Figure(
        data=go.Heatmap(
            x=x_pos, y=y_pos, z=z_values, text=xrd_filename, colorscale="Jet"
        )
    )
    fig.update_layout(title=f"XRD map for {foldername}")
    fig.data[0].update(zmin=min(z_values), zmax=max(z_values))

    return fig
