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


def plot_xrd_pattern(foldername, xrd_filename, x_pos, y_pos, xrd_path="./data/XRD/"):
    """
    Read an XRD pattern file and return a figure object.

    Parameters
    ----------
    foldername : str
        Name of the folder containing the XRD data files.
    xrd_filename : str
        Name of the XRD data file.
    x_pos : int
        x position of the data file, used for plot title.
    y_pos : int
        y position of the data file, used for plot title.
    xrd_path : str, optional
        Path to the folder containing the XRD data files. Defaults to "./data/XRD/".

    Returns
    -------
    fig : plotly.graph_objects.Figure
        A figure object containing a Scatter plot of the XRD data.
    """
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
    """
    Read all XRD data files from the given foldername and return the coordinates and filenames as three separate lists.

    Parameters
    ----------
    foldername : str
        Name of the folder containing the XRD data files.
    xrd_path : str, optional
        Path to the folder containing the XRD data files. Defaults to "./data/XRD/".

    Returns
    -------
    x_pos : list
        List of x coordinates of the data files.
    y_pos : list
        List of y coordinates of the data files.
    xrd_filename : list
        List of filenames of the XRD data files.
    """
    fullpath = pathlib.Path(xrd_path + foldername)
    pos_list = create_coordinate_map(fullpath)

    x_pos = [pos[0] for pos in pos_list]
    y_pos = [pos[1] for pos in pos_list]
    xrd_filename = [pos[2] for pos in pos_list]

    return x_pos, y_pos, xrd_filename


def read_from_lst(lst_file_path, x_pos, y_pos):
    """
    Reads the .lst file from a refinement and returns the header and refined lattice parameters of every phases

    Parameters
    ----------
    lst_file_path : str
        Path to the .lst file.
    x_pos : int
        x position of the data file.
    y_pos : int
        y position of the data file.

    Returns
    -------
    header_lst : str
        The header string containing all the column names.
    DATA_RR_OUTPUT : list
        List containing the position, lattice parameters, and their errors.
    FIT_RR_OUTPUT : list
        List containing the refinement results (R factors, phase name, lattice parameters and their errors).
    """

    with open(lst_file_path, "r") as file:
        header_lst = "x_pos\ty_pos\t"
        phases = []

        DATA_RR_OUTPUT = [x_pos, y_pos]
        FIT_RR_OUTPUT = []

        # reading the .lst file line by line to get lattice parameters
        current_phase = None
        for line in file:
            if line.startswith("Rp="):
                R_factors = line.split("  ")[-1].split(" ")
                for elm in R_factors:
                    FIT_RR_OUTPUT.append(elm.strip())
            elif line.startswith("Local parameters and GOALs for phase"):
                current_phase = line.split()[-1]
                phases.append(current_phase)
                # name of the current phase for the refined lattice parameters
                FIT_RR_OUTPUT.append(current_phase)
            elif (
                line.startswith("A=") or line.startswith("C=") or line.startswith("B=")
            ):
                FIT_RR_OUTPUT.append(line.strip())
                line_lattice = line.rstrip().split("=")
                # the line is in this format 'C=1.234567+-0.001234' and we split it to only get the value and err
                letter = line_lattice[0]
                if line_lattice[1] == "UNDEF":
                    line_lattice[1] = None
                if "+-" in line:
                    lattice = line_lattice[1].split("+-")
                else:
                    lattice = [line_lattice[1], "0.000000"]
                header_lst += (
                    f"{current_phase}_{letter}\t{current_phase}_{letter}_err\t"
                )
                # adding the column name to the header
                DATA_RR_OUTPUT.append(lattice[0])
                DATA_RR_OUTPUT.append(lattice[1].rstrip())

            # extracting volume fractions now (but is actually found first in the .lst file)
            else:
                for k, elmt in enumerate(phases):
                    # same stuff, getting volume fraction values, format can be 'QNd2Fe14B=0.456789' for example
                    if line.startswith("Q" + elmt):
                        FIT_RR_OUTPUT.append(line.strip())
                        if "+-" in line:
                            fraction = line.split("=")[1].split("+-")
                        else:
                            fraction = [line.split("=")[1].rstrip(), "0.000000"]
                        header_lst += f"Q{elmt}\tQ{elmt}_err\t"
                        DATA_RR_OUTPUT.append(fraction[0])
                        DATA_RR_OUTPUT.append(fraction[1].rstrip())
    return header_lst, DATA_RR_OUTPUT, FIT_RR_OUTPUT


def save_refinement_results(foldername, result_xrd_path, header, rr_output):
    save_result_file = pathlib.Path(result_xrd_path + foldername + "_RR_maps.dat")

    with open(save_result_file, "w") as file:
        file.write(header + "\n")

        for line in rr_output:
            saved_line = ""
            for elm in line:
                saved_line += str(elm) + "\t"
            file.write(saved_line + "\n")


def result_file_exists(foldername, result_xrd_path):
    """
    Check if the refinement results file exists in the result_xrd_path folder.

    Parameters
    ----------
    foldername : str
        Name of the folder containing the XRD data files.
    result_xrd_path : str
        Path to the folder containing the refinement results files.

    Returns
    -------
    bool
        True if the refinement results file exists, False otherwise.
    """
    save_result = pathlib.Path(foldername + "_RR_maps.dat")

    return save_result.name in os.listdir(result_xrd_path)


def get_refinement_results(
    foldername, xrd_path="./data/XRD/", result_xrd_path="./results/XRD/"
):

    if not result_file_exists(foldername, result_xrd_path):
        save_list = []
        x_pos, y_pos, xrd_filename = read_xrd_files(foldername)

        for i, ras_file in enumerate(xrd_filename):
            lst_file_path = pathlib.Path(
                xrd_path + foldername + "/" + ras_file.replace(".ras", ".lst")
            )
            # Read the .lst file and get the refined lattice parameters
            header, rr_output = read_from_lst(lst_file_path, x_pos[i], y_pos[i])[0:2]
            if np.abs(x_pos[i]) + np.abs(y_pos[i]) <= 60:
                save_list.append(rr_output)

        save_refinement_results(foldername, result_xrd_path, header, save_list)
    else:
        # print("Refinement results file already exists")
        pass

    read_result_file = pathlib.Path(result_xrd_path + foldername + "_RR_maps.dat")
    with open(read_result_file, "r") as file:
        header = file.readline().split()

    return header


def get_refined_parameter(foldername, datatype, result_xrd_path):
    x_pos, y_pos, z_values = [], [], []

    if datatype != "Raw XRD data" and datatype is not None:
        options = get_refinement_results(foldername, result_xrd_path=result_xrd_path)
        if datatype in options:
            column = options.index(datatype)

            with open(result_xrd_path + foldername + "_RR_maps.dat", "r") as file:
                header = file.readline()

                for line in file:
                    data = line.split()
                    x_pos.append(float(data[0]))
                    y_pos.append(float(data[1]))
                    if data[column] != "None":
                        z_values.append(float(data[column]))
                    else:
                        z_values.append(0)

            return x_pos, y_pos, z_values

    return None


def check_xrd_refinement(
    foldername, xrd_path="./data/XRD/", result_xrd_path="./results/XRD/"
):
    """
    Check if the refinement files (.lst) exist in the given foldername.

    Parameters
    ----------
    foldername : str
        Path to the folder containing the refinement files.
    xrd_path : str, optional
        Path to the folder containing the data files. Defaults to "./data/XRD/".

    Returns
    -------
    bool
        True if refinement files are found, False otherwise.
    """
    fullpath = f"{xrd_path}{foldername}"

    # Check if folder exists
    try:
        os.listdir(fullpath)
    except FileNotFoundError:
        return False

    # Check if refinement files exist
    lst_files = [file for file in os.listdir(fullpath) if file.endswith(".lst")]
    if len(lst_files) > 0:
        options = get_refinement_results(foldername, xrd_path, result_xrd_path)[2:-1]
        return options

    return False


def plot_xrd_heatmap(
    foldername,
    datatype,
    xrd_path="./data/XRD/",
    result_xrd_path="./results/XRD/",
):
    """
    Plot a heatmap of XRD data.

    Parameters
    ----------
    foldername : str
        Name of the folder containing the XRD data files.
    datatype : str
        Type of data to plot. default, plot raw XRD data.
    xrd_path : str, optional
        Path to the folder containing the XRD data files. Defaults to "./data/XRD/".
    result_xrd_path : str, optional
        Path to the folder containing the results. Defaults to "./results/XRD/".

    Returns
    -------
    fig : plotly.graph_objects.Figure
        A figure object containing a Heatmap plot of the XRD data.
    """
    datapath = f"{result_xrd_path}"

    empty_fig = go.Figure(data=go.Heatmap())
    empty_fig.update_layout(height=600, width=600)
    if foldername is None:
        return empty_fig

    x_pos, y_pos, xrd_filename = read_xrd_files(foldername, xrd_path)

    if datatype is None or datatype == "Raw XRD data":
        z_values = np.zeros(len(x_pos) + len(y_pos))
    else:
        x_pos, y_pos, z_values = get_refined_parameter(
            foldername, datatype, result_xrd_path
        )
        if z_values is None:
            return empty_fig

    fig = go.Figure(
        data=go.Heatmap(
            x=x_pos, y=y_pos, z=z_values, text=xrd_filename, colorscale="Jet"
        )
    )
    fig.update_layout(title=f"XRD map for {foldername}")
    fig.data[0].update(zmin=min(z_values), zmax=max(z_values))

    return fig
