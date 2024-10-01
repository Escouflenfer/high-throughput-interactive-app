"""
Functions used in MOKE interactive plot using dash module to detach it completely from Jupyter Notebooks.
Internal use for Institut Néel and within the MaMMoS project, to export and read big datasets produced at Institut Néel.

@Author: William Rigaut - Institut Néel (william.rigaut@neel.cnrs.fr)
"""

import os
import numpy as np
import plotly.graph_objects as go
from scipy import signal


def read_info(fullpath):
    """Reads the info.txt file created when a MOKE scan is done. The function will return the applied voltage
    in the coil and the number of aquisitions per point

    Parameters
    ----------
    fullpath : STR
        Path containing the datafiles and the info.txt file

    Returns
    -------
    info_list : LIST
        List containing the applied voltage in int type and a list containing indexes from 0 to the (number of aquisition - 1)
    """
    if fullpath is None:
        return []

    infopath = f"{fullpath}/info.txt"
    with open(infopath, "r", encoding="iso-8859-1") as file_info:
        for line in file_info:
            if "Pulse_voltage" in line:
                pulse_volt = line.split("=")[1]
            elif "Average_per_point" in line:
                avg_pts = line.split("=")[1]

    return [int(pulse_volt), range(int(avg_pts))]


def heatmap_exists(subfolder, suffix="_MOKE.dat", result_moke_path="./results/MOKE/"):
    """Check if the heatmap was already created in the result_moke_path folder

    Parameters
    ----------
    subfolder : STR
        Path containing the datafiles and the info.txt file

    Returns
    -------
    info_list : LIST
        List containing the applied voltage in int type and a list containing indexes from 0 to the (number of aquisition - 1)
    """
    filepath = f"{subfolder}{suffix}"

    return filepath in os.listdir(result_moke_path)


def get_subfolders(foldername, moke_path="./data/MOKE/"):
    """Converting X and Y real coordinates to the indices used by bruker to label files during edx scans

    Parameters
    ----------
    foldername : STR
        Main folder containing all the different scans for MOKE, where each scan is
        also a folder containing all the datafile

    Returns
    -------
    path_name : LIST
        List containing all the folders inside main MOKE 'foldername'
    """

    folderpath = f"{moke_path}{foldername}/"

    return sorted(
        [
            folder
            for folder in os.listdir(folderpath)
            if not folder.startswith(".") and not folder.endswith(".jpg")
        ]
    )


def make_path_name(fullpath, x_pos, y_pos):
    """Fetching correct datafiles at given (X, Y) position and a given dataset

    Parameters
    ----------
    foldername : STR
        Main folder containing all the different scans for MOKE, where each scan is
        also a folder containing all the datafile
    subfolder : STR
        Folder that contains all the MOKE files in the .txt format.
        Used to read data in the correct path
    x_pos, ypos : INT, INT
        Horizontal position X (in mm) and vertical position Y (in mm) on the sample.
        The MOKE scan saved the datafiles labeled by two numbers (a, b) corresponding to the scan number in the x and y positions.

    Returns
    -------
    path_name : LIST
        List containing the path for the magnetization, pulse and sum files
    """
    # Folder pointing to the MOKE scans
    fullpath = f"{fullpath}"

    if isinstance(x_pos, int):
        x_pos = float("{:.1f}".format(x_pos))
    if isinstance(y_pos, int):
        y_pos = float("{:.1f}".format(y_pos))

    mag = f"x{x_pos}_y{y_pos}_magnetization.txt"
    pul = f"x{x_pos}_y{y_pos}_pulse.txt"
    sum = f"x{x_pos}_y{y_pos}_sum.txt"
    data_mag = f"{fullpath}/{mag}"
    data_pul = f"{fullpath}/{pul}"
    data_sum = f"{fullpath}/{sum}"

    # Check if the 3 datafiles at the requested position are inside the folder
    count_check = 0
    for file in os.listdir(fullpath):
        if count_check == 3:
            break
        elif file.endswith(mag):
            data_mag = f"{fullpath}/{file}"
            count_check += 1
        elif file.endswith(pul):
            data_pul = f"{fullpath}/{file}"
            count_check += 1
        elif file.endswith(sum):
            data_sum = f"{fullpath}/{file}"
            count_check += 1

    return [data_mag, data_pul, data_sum]


def read_moke_data(data_mag, data_pul, data_sum, data_range=range(1), time_step=0.05):
    """Reading the 3 datafiles magnetisation, pulse and sum

    Parameters
    ----------
    data_mag : LIST
        List containing the magnetisation data measured by sMOKE
    data_pul : LIST
        Pulse field emitted by the coil in sMOKE
    data_sum : LIST
        Reflectivity measured by sMOKE
    data_range : LIST
        Contains the number of acquisitions at the same position to average the signal
    time_step : FLOAT
        Time resolution for the sMOKE in μs, default is 50 ns (0.05 μs)

    Returns
    -------
    t_values, mag_values, pul_values, sum_values] : LIST
        t_values, mag_values, pul_values, sum_values
    """
    mag_values, pul_values, sum_values = [], [], []

    try:
        # opening the 3 raw datafiles from MOKE output
        with open(data_mag, "r", encoding="iso-8859-1") as file_mag, open(
            data_pul, "r", encoding="iso-8859-1"
        ) as file_pul, open(data_sum, "r", encoding="iso-8859-1") as file_sum:

            for line in file_mag:
                if not line.startswith("D"):
                    data = line.split()
                    if len(data) > 0:
                        mag_values.append(np.mean([float(data[i]) for i in data_range]))
            for line in file_pul:
                if not line.startswith("P"):
                    data = line.split()
                    if len(data) > 0:
                        pul_values.append(np.mean([float(data[i]) for i in data_range]))
            for line in file_sum:
                if not line.startswith("S"):
                    data = line.split()
                    if len(data) > 0:
                        sum_values.append(np.mean([float(data[i]) for i in data_range]))

        t_values = [j * time_step for j in range(len(mag_values))]
    except FileNotFoundError:
        print("Datafile not found, you are probably outside the range")
    return t_values, mag_values, pul_values, sum_values


def calculate_field_adjusted(pulse_data, adjust_to_max, max_field):
    """Calculate field as a function of applied voltage

    Parameters
    ----------
    pulse_data : INT
        Main folder containing all the different scans for MOKE, where each scan is
        also a folder containing all the datafile
    adjust_to_max : BOOL

    Returns
    -------
    path_name : LIST
        List containing all the folders inside main MOKE 'foldername'
    """
    field = np.cumsum(pulse_data)

    # Calculate the scale factor differently
    if adjust_to_max:
        scale_factor = max_field / np.abs(np.min(field))
    else:
        scale_factor = max_field / np.abs(np.max(field))
    field *= -scale_factor

    return field


def adjust_magnetization(magnetization_data, ranges, avg_sum):
    # Calculate kerr rotation for specified ranges and adjust magnetization data
    """
    Adjust magnetization data

    Parameters
    ----------
    magnetization_data : LIST
        Magnetization data from MOKE
    ranges : LIST
        List of tuples of start and end indices to calculate Kerr rotation
    avg_sum : FLOAT
        Average reflectivity

    Returns
    -------
    adjusted_magnetization_data : LIST
        Adjusted magnetization data
    """
    Mr = [np.mean(magnetization_data[range[0] - 1 : range[1] + 1]) for range in ranges]

    return np.concatenate(
        [
            (magnetization_data[:1002] - np.mean(Mr[:2])) / avg_sum,
            (magnetization_data[1002:] - np.mean(Mr[2:])) / avg_sum,
        ]
    )


def calculate_field_values(
    mag_values, pul_values, sum_values, pulse_volt, coil_factor=0.92667
):
    # Convert from Applied Voltage to Applied Field with calibration coefficient (coil_factor)
    """
    Convert from Applied Voltage to Applied Field with calibration coefficient (coil_factor)

    Parameters
    ----------
    mag_values : LIST
        Magnetization data from MOKE
    pul_values : LIST
        Pulse field emitted by the coil in sMOKE
    sum_values : LIST
        Sum of reflectivity measured by sMOKE
    pulse_volt : INT
        Voltage applied to the coil in sMOKE
    coil_factor : FLOAT, optional
        Calibration coefficient for the coil, by default 0.92667

    Returns
    -------
    field_values : LIST
        Applied field from pulse data
    corr_mag_values : LIST
        Adjusted magnetization data
    """
    max_field = coil_factor * int(pulse_volt) / 100
    avg_sum = np.mean(sum_values)

    field_values = np.concatenate(
        [
            calculate_field_adjusted(pul_values[:1002], True, max_field=max_field),
            calculate_field_adjusted(pul_values[1002:], False, max_field=max_field),
        ]
    )
    corr_mag_values = adjust_magnetization(
        mag_values, [(50, 250), (750, 950), (1050, 1250), (1750, 1950)], avg_sum
    )

    return field_values, corr_mag_values


def extract_coercivity(field_values, corr_mag_values):
    """
    Extract coercivity from MOKE loop by taking the minimum of the field values at both sides of the loop
    (and do the mean of the absolute value of both minimums)

    Parameters
    ----------
    field_values : LIST
        Field values from sMOKE
    corr_mag_values : LIST
        Adjusted magnetization values from sMOKE

    Returns
    -------
    coercivity : FLOAT
        Coercivity value extracted from the data
    """
    coercivity1, coercivity2 = [], []
    min_1 = np.min(np.abs(corr_mag_values[356:654]))
    min_2 = np.min(np.abs(corr_mag_values[1356:1664]))

    coercivity1 = field_values[np.where(corr_mag_values == min_1)[0]]
    if len(coercivity1) == 0:
        coercivity1 = field_values[np.where(corr_mag_values == -min_1)[0]]
    coercivity2 = field_values[np.where(corr_mag_values == min_2)[0]]
    if len(coercivity2) == 0:
        coercivity2 = field_values[np.where(corr_mag_values == -min_2)[0]]
    return np.mean([np.min(np.abs(coercivity1)), np.min(np.abs(coercivity2))])


def plot_moke_data(foldername, subfolder, x_pos, y_pos, moke_path="./data/MOKE/"):
    """
    Function to plot the data from the MOKE measurement of the given foldername, subfolder, x position and y position

    Parameters
    ----------
    foldername : STR
        Folder containing the data
    subfolder : STR
        Subfolder containing the data
    x_pos : INT
        X position of the measurement
    y_pos : INT
        Y position of the measurement
    moke_path : STR, optional
        Path to the MOKE data, by default "./data/MOKE/"

    Returns
    -------
    fig : plotly.graph_objects.Figure
        Figure object with the plot
    """
    fullpath = f"{moke_path}{foldername}/{subfolder}/"
    empty_fig = go.Figure(data=go.Scatter())

    if foldername is None or subfolder is None:
        return empty_fig

    datafiles_path = make_path_name(fullpath, x_pos, y_pos)
    moke_data = read_moke_data(*datafiles_path, read_info(fullpath)[1])

    # Creating the scatter plot with plotly.graph_objects library
    time_axis = moke_data[0]
    fig = go.Figure(
        data=[
            go.Scatter(
                x=[t for t in time_axis],
                y=[elm for elm in moke_data[1]],
                marker_color="blue",
                name="Signal",
            ),
            go.Scatter(
                x=[t for t in time_axis],
                y=[elm for elm in moke_data[2]],
                marker_color="red",
                name="Pulse",
            ),
        ]
    )

    return fig


def make_filenames_from_magfile(fullpath, magfile):
    """
    Create the 3 datafiles path from a given magnetization datafile name

    Parameters
    ----------
    fullpath : STR
        Path to the MOKE data
    magfile : STR
        Name of the magnetization datafile

    Returns
    -------
    datafiles_path : LIST
        List containing the path of the magnetization, pulse and sum datafiles
    """
    data_mag = fullpath + magfile
    data_pul = fullpath + magfile.replace("magnetization", "pulse")
    data_sum = fullpath + magfile.replace("magnetization", "sum")

    return [data_mag, data_pul, data_sum]


def get_coordinates_from_name(filename):
    """
    Get the coordinates from a given filename in the MOKE data.

    The filename is expected to have the format "magnetization_x_y.dat" where x and y are the coordinates.
    The function returns a list containing the coordinates as strings.

    Parameters
    ----------
    filename : STR
        The filename to extract the coordinates from

    Returns
    -------
    coordinates : LIST
        List containing the coordinates as strings
    """
    return [
        pos.translate({ord(i): None for i in "xy"}) for pos in filename.split("_")[1:3]
    ]


def smoothData(field_values, corr_mag_values, polyorder=3):
    """
    Smooth the data using Savitzky-Golay filter.

    Parameters
    ----------
    field_values : LIST
        List containing the field values
    corr_mag_values : LIST
        List containing the corrected magnetization values
    polyorder : INT, optional
        Order of the polynomial used in the Savitzky-Golay filter, by default 3 (needs to be odd number)

    Returns
    -------
    field_values : LIST
        Smoothed field values
    corr_mag_values : LIST
        Smoothed corrected magnetization values
    """
    field_values = signal.savgol_filter(field_values, 12, 10 - polyorder)
    corr_mag_values = signal.savgol_filter(corr_mag_values, 12, 10 - polyorder)

    return field_values, corr_mag_values


def plot_moke_coercivity(foldername, subfolder, x_pos, y_pos, moke_path="./data/MOKE/"):
    """
    Plot a single MOKE loop with coercivity and reflectivity values at given position (x, y).

    Parameters
    ----------
    foldername : STR
        Name of the folder containing the data
    subfolder : STR
        Name of the subfolder
    x_pos : INT
        X coordinate of the loop to plot
    y_pos : INT
        Y coordinate of the loop to plot
    moke_path : STR, optional
        Path to the data folder, by default "./data/MOKE/"

    Returns
    -------
    fig : go.Figure
        The plotly figure object
    """
    fullpath = f"{moke_path}{foldername}/{subfolder}/"
    empty_fig = go.Figure(data=go.Scatter())

    if foldername is None or subfolder is None:
        return empty_fig

    pulse_voltage, data_range = read_info(fullpath)
    files = make_path_name(fullpath, x_pos, y_pos)
    moke_data = read_moke_data(*files, data_range)
    field_values, corr_mag_values = calculate_field_values(
        *moke_data[1:], pulse_voltage
    )

    field_values, corr_mag_values = smoothData(field_values, corr_mag_values)

    coercivity = extract_coercivity(field_values, corr_mag_values)
    reflectivity = np.mean(moke_data[3])

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[*field_values[356:654], *field_values[1356:1664]],
            y=[*corr_mag_values[356:654], *corr_mag_values[1356:1664]],
            mode="markers",
            marker=dict(color="white", size=9, line=dict(color="blue", width=2)),
        )
    )

    meta = go.layout.Annotation(
        text="Coercivity {:.2f} T<br>Reflectivity {:.2f} V".format(
            coercivity, reflectivity
        ),
        align="left",
        showarrow=False,
        xref="paper",
        yref="paper",
        x=0.10,
        y=0.95,
        bordercolor="black",
        borderwidth=1,
    )
    fig.update_layout(annotations=[meta])

    return fig


def plot_1D_with_datatype(foldername, subfolder, x_pos, y_pos, data_type):
    """
    Plot 1D MOKE data or coercivity depending on the data type.

    Parameters
    ----------
    foldername : str
        Name of the folder containing the data
    subfolder : str
        Name of the subfolder
    x_pos : int
        X coordinate of the loop to plot
    y_pos : int
        Y coordinate of the loop to plot
    data_type : str
        Type of data to plot. "Magnetic properties" or "Raw MOKE data"

    Returns
    -------
    fig : go.Figure
        The plotly figure object
    """
    fig = go.Figure(data=go.Scatter())

    if data_type == "Magnetic properties":
        fig = plot_moke_coercivity(foldername, subfolder, x_pos, y_pos)
    elif data_type == "Raw MOKE data":
        fig = plot_moke_data(foldername, subfolder, x_pos, y_pos)
    return fig


def generate_moke_heatmap(fullpath):
    """
    Generate the heatmap data from the moke data in the given folder.

    Parameters
    ----------
    fullpath : str
        The path to the folder containing the moke data

    Returns
    -------
    data_list : list
        A 2D array containing the coercivity and reflectivity at each position.
        Each row of the 2D array is a list containing the x position, y position, coercivity and reflectivity.
    """
    pulse_voltage, data_range = read_info(fullpath)
    data_list = []

    for file in [mag for mag in os.listdir(fullpath) if "magnetization" in mag]:
        file_list = get_coordinates_from_name(file)
        datafiles = make_filenames_from_magfile(fullpath, file)
        moke_data = read_moke_data(*datafiles, data_range)
        field_values, corr_mag_values = calculate_field_values(
            *moke_data[1:], pulse_voltage
        )

        field_values, corr_mag_values = smoothData(field_values, corr_mag_values)

        file_list.append(extract_coercivity(field_values, corr_mag_values))
        file_list.append(np.mean(moke_data[-1]))
        data_list.append(file_list)

    return data_list


def save_moke_heatmap(fullpath, data_list, suffix="_MOKE.dat"):
    """
    Save the moke heatmap data to a file.

    Parameters
    ----------
    fullpath : str
        The path to the folder containing the moke data
    data_list : list
        A 2D array containing the coercivity and reflectivity at each position.
        Each row of the 2D array is a list containing the x position, y position, coercivity and reflectivity.
    suffix : str, optional
        The suffix to add to the filename, by default "_MOKE.dat"

    Returns
    -------
    None
    """
    filepath = f"{fullpath}{suffix}"
    header = f"x_pos\ty_pos\tCoercivity (T)\tReflectivity (V)\n"

    try:
        with open(filepath, "w") as file:
            file.write(header)
            for line in data_list:
                x_pos = float(line[0])
                y_pos = float(line[1])
                if (
                    np.abs(x_pos) + np.abs(y_pos) <= 60
                    and np.abs(x_pos) <= 40
                    and np.abs(y_pos) <= 40
                ):
                    file.write(f"{line[0]}\t{line[1]}\t{line[2]}\t{line[3]}\n")

    except FileNotFoundError:
        print(f"{fullpath} folder does not exist !")
    return None


def read_heatmap(datapath, suffix="_MOKE.dat"):
    """
    Read a heatmap file and return the header and data.

    Parameters
    ----------
    datapath : str
        The path to the folder containing the heatmap file
    suffix : str, optional
        The suffix to add to the filename, by default "_MOKE.dat"

    Returns
    -------
    header : list
        A list containing the column names
    data : 2D array
        A 2D array containing the data
    """
    filepath = f"{datapath}{suffix}"

    with open(filepath, "r") as datafile:
        header = (next(datafile)).strip("\n").split("\t")
        data = np.genfromtxt(datafile, delimiter="\t", skip_header=0)

    return header, data


def plot_moke_heatmap(
    foldername,
    subfolder,
    datatype,
    moke_path="./data/MOKE/",
    result_moke_path="./results/MOKE/",
):
    """
    Plot a heatmap of MOKE data.

    Parameters
    ----------
    foldername : str
        Name of the folder containing the MOKE data files.
    subfolder : str
        Name of the subfolder containing the data files.
    datatype : str
        Type of data to plot. default, plot raw MOKE data.
    moke_path : str, optional
        Path to the folder containing the MOKE data files. Defaults to "./data/MOKE/".
    result_moke_path : str, optional
        Path to the folder containing the results. Defaults to "./results/MOKE/".

    Returns
    -------
    fig : plotly.graph_objects.Figure
        A figure object containing a Heatmap plot of the MOKE data.
    header_data : str
        The column name of the data that was plotted.
    """
    fullpath = f"{moke_path}{foldername}/{subfolder}/"
    datapath = f"{result_moke_path}{subfolder}"
    empty_fig = go.Figure(data=go.Heatmap())
    empty_fig.update_layout(height=800, width=800)
    header_data = None

    if foldername is None or subfolder is None or datatype is None:
        return empty_fig, header_data

    if not heatmap_exists(subfolder):
        data_list = generate_moke_heatmap(fullpath)
        save_moke_heatmap(datapath, data_list)

    header, data_list = read_heatmap(datapath)

    x_pos, y_pos, coercivity, reflectivity = [], [], [], []

    for line in data_list:
        x_pos.append(line[0])
        y_pos.append(line[1])
        coercivity.append(line[2])
        reflectivity.append(line[3])

    z_values = []
    if datatype == "Magnetic properties":
        z_values = coercivity
        header_data = header[2]
    elif datatype == "Raw MOKE data":
        z_values = reflectivity
        header_data = header[3]

    fig = go.Figure(data=go.Heatmap(x=x_pos, y=y_pos, z=z_values, colorscale="Jet"))
    fig.update_layout(title=f"MOKE {header_data.split()[0]} map for {subfolder}")
    fig.data[0].update(zmin=min(z_values), zmax=max(z_values))

    return fig, header_data
