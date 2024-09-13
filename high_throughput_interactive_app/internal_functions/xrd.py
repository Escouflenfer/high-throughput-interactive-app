"""
Functions used in MOKE interactive plot using dash module to detach it completely from Jupyter Notebooks.
Internal use for Institut Néel and within the MaMMoS project, to export and read big datasets produced at Institut Néel.

@Author: William Rigaut - Institut Néel (william.rigaut@neel.cnrs.fr)
"""

import os
import pathlib
import numpy as np
import plotly.graph_objects as go


def create_coordinate_map(folderpath, suffix=".ras"):
    filelist = [file for file in os.listdir(folderpath) if file.endswith(suffix)]
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
            pos_list.append([x_pos, y_pos])
    print(pos_list)


def check_xrd_refinement(folderpath):

    return None


def read_xrd_pattern(
    foldername,
    xrd_path="./data/XRD/",
):
    fullpath = pathlib.Path(xrd_path + foldername)
    create_coordinate_map(fullpath)

    return None


def plot_moke_heatmap(
    foldername,
    datatype,
    xrd_path="./data/XRD/",
    result_xrd_path="./results/XRD/",
):
    fullpath = f"{xrd_path}{foldername}/"
    datapath = f"{result_xrd_path}"
    empty_fig = go.Figure(data=go.Heatmap())
    empty_fig.update_layout(height=600, width=600)
    if foldername is None or datatype is None:
        return empty_fig

    fig = go.Figure(data=go.Heatmap(x=x_pos, y=y_pos, z=z_values, colorscale="Jet"))
    fig.update_layout(title=f"MOKE {header_data.split()[0]} map for {subfolder}")
    fig.data[0].update(zmin=min(z_values), zmax=max(z_values))

    return fig, header_data
