Output of tree command:
```
|-- app.py
|-- requirements.txt

```

---

./app.py
```
Summary:
The given code is a Tkinter-based graphical user interface (GUI) application in Python that monitors system temperature and fan speed, allowing users to visualize this data in real-time graphs and set the speed manually or switch to automatic control. It utilizes the `subprocess` module to interact with the system's fan control utility (likely "NoteBook FanControl" or "nbfc"), the `re` module to parse the command output, and the `matplotlib` library for plotting.

Key Components:
- Temperature and fan speed readings are stored in `temperature_readings` and `fanspeed_readings`, respectively.
- Two control modes are defined: automatic (`CONTROL_MODE_AUTO`) and manual (`CONTROL_MODE_MANUAL`), with the active mode stored in `current_control_mode`.
- The `get_system_readings` function retrieves temperature and fan speed by running a subprocess that executes the 'nbfc status -a' command.
- `root` is the main Tkinter window where control widgets and graphs are added.
- Two Matplotlib graphs (`temp_fig`, `fan_speed_fig`) are created and embedded in the Tkinter application using `FigureCanvasTkAgg`.
- `update_temperature_graph` and `update_fanspeed_graph` functions update their respective graphs with new data and limit the readings to 600 points.
- `delayed_fan_setting` is intended to change the fan speed after some delay but currently executes the command instantly.
- `update_readings` fetches the current system readings, updates the labels, the graphs, and reschedules itself to run at intervals set by a slider.
- `set_fan_speed` applies a new fan speed when in manual control mode.
- `set_auto_control` and `set_manual_control` functions are used to enable automatic or manual fan control, adjusting the GUI accordingly.
- Corresponding Tkinter widgets (`Labels`, `Scale` sliders, and `Radiobuttons`) are created to display system readings, adjust refresh interval, and control fan speed.
- The application starts by calling `update_readings` and enters the Tkinter main loop.

Function Documentation:
- `get_system_readings`: Runs a subprocess to get temperature and fan speed from 'nbfc'. Returns temperature and fan speed. Handles `subprocess.CalledProcessError` exceptions.
- `update_temperature_graph`: Updates the temperature graph using `temperature_readings`.
- `update_fanspeed_graph`: Updates the fan speed graph using `fanspeed_readings`.
- `delayed_fan_setting`: Executes 'nbfc' command to set fan speed to a given value.
- `update_readings`: Fetches readings, updates labels, graphs, and schedules the next update call.
- `set_fan_speed`: Sets the fan speed manually and triggers `delayed_fan_setting` using the value from the manual control slider.
- `set_auto_control`: Switches the control mode to automatic and disables the manual control slider.
- `set_manual_control`: Switches the control mode to manual and enables the manual control slider.

Parameters:
- `value` in `set_fan_speed` and `delayed_fan_setting` functions is the fan speed percentage to set.
- `refresh_seconds` in `update_readings` is the time interval for refreshing readings.

Notes:
- `CONTROL_MODE_AUTO` and `CONTROL_MODE_MANUAL` are constants representing available control modes.
- The update intervals for graph and readings are controlled through `refresh_slider`.
- Error handling is implemented only for the `subprocess.check_output` using a try-except block.
- The application assumes the `nbfc` utility is available and configured with the necessary permissions (`sudo` used without password prompt).
- Comments within the code provide additional inline documentation for specific code blocks.
- The GUI is non-resizable with a minimum size defined, improving stability in the layout presentation.```
---

./requirements.txt
```
Matplotlib is a comprehensive library for creating static, animated, and interactive visualizations in Python. It offers an object-oriented API for embedding plots into applications using general-purpose GUI toolkits like Tkinter, wxPython, Qt, or GTK. It's also commonly used in Jupyter notebooks for inline plots.

Here is a high-level summary of key components and concepts in Matplotlib:

1. `pyplot` module: Provides a MATLAB-like interface for plotting and is stateful, i.e., it keeps track of the current figure and plotting area, and the plotting functions are directed to the current axes.

2. `Figure`: The top-level container for all plot elements. Represents the overall window or page where everything is drawn.

3. `Axes`: This is what you might think of as 'a plot.' It is the region of the image with the data space and can contain multiple `Axis` objects.

4. `Axis`: These are the number-line-like objects and take care of setting the graph limits and generating the ticks and tick labels.

5. `Artist`: Everything you can see on the figure is an artist, including `Figure`, `Axes`, and `Axis` objects. Even the text is considered an artist.

Here are some common functions you might encounter when using Matplotlib:

- `plt.figure()`: Creates a new figure.
- `plt.plot()`: Plot y versus x as lines and/or markers.
- `plt.xlabel()`, `plt.ylabel()`: Set the labels of the x-axis and y-axis.
- `plt.title()`: Set a title for the axes.
- `plt.legend()`: Place a legend on the axes.
- `plt.show()`: Display a figure to the user.
- `plt.savefig()`: Save the current figure.
- `plt.subplots()`: Create a figure and a set of subplots.

Example usage for creating a simple line plot:

```python
import matplotlib.pyplot as plt
# Data for plotting
x = [1, 2, 3, 4]
y = [10, 20, 25, 30]
# Create a new figure and an axes to plot in
fig, ax = plt.subplots()
# Plot data on the axes
ax.plot(x, y)
# Label the axes
ax.set_xlabel('X axis label')
ax.set_ylabel('Y axis label')
# Show the plot
plt.show()
```

When documenting or referencing Matplotlib in code, always mention the version of Matplotlib being used, as some functionality can change between versions. Additionally, it's useful to note which back-end is in use, as this can affect how plots are displayed or saved.```
---
