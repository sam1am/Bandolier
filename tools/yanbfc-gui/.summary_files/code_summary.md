Output of tree command:
```
|-- app.py
|-- requirements.txt

```

---

./app.py
```
import tkinter as tk
from tkinter import ttk
import subprocess
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# The lists to store temperature and fan speed readings
temperature_readings = []
fanspeed_readings = []

# Add variables to keep track of the control mode (auto or manual)
CONTROL_MODE_AUTO = "auto"
CONTROL_MODE_MANUAL = "manual"
current_control_mode = CONTROL_MODE_MANUAL

# Function to fetch the current temperature and fan speed
def get_system_readings():
    try:
        output = subprocess.check_output(['nbfc', 'status', '-a'], text=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute 'nbfc status -a': {e}")
        return "n/a", "n/a"
    
    temperature_match = re.search(r'Temperature\s+:\s+(\d+\.?\d*)', output)
    # fan_speed_match = re.search(r'Current fan speed\s+:\s+(\d+\.?\d*)', output)
    fan_speed_match = re.search(r'Current fan speed\s+:\s+(\d+\.?\d*)', output)

    temperature = temperature_match.group(1) if temperature_match else "n/a"
    fan_speed = fan_speed_match.group(1) if fan_speed_match else "n/a"
    print(f"Temperature: {temperature}, Fan Speed: {fan_speed}")
    return temperature, fan_speed

# Create the main window
root = tk.Tk()
root.title("System Monitor")
root.minsize(width=800, height=600)

# Define two global figures and axes for plotting the temperature and fan speed
temp_fig, temp_ax = plt.subplots(figsize=(8, 2))
temp_canvas = FigureCanvasTkAgg(temp_fig, master=root)
temp_canvas.get_tk_widget().pack()

fan_speed_fig, fan_speed_ax = plt.subplots(figsize=(8, 2))
fan_speed_canvas = FigureCanvasTkAgg(fan_speed_fig, master=root)
fan_speed_canvas.get_tk_widget().pack()

# Update the graph with new temperature readings
def update_temperature_graph():
    global temperature_readings, temp_ax

    if len(temperature_readings) > 600:  # Limit the number of readings
        temperature_readings.pop(0)

    temp_ax.clear()
    temp_ax.plot(temperature_readings, marker='o', color='b')
    temp_ax.set_title('Temperature Over Time')
    temp_ax.set_ylabel('Temperature (°C)')
    temp_ax.set_xlabel('Reading')
    temp_ax.set_xticks(range(0, len(temperature_readings), max(len(temperature_readings)//6, 1)))
    temp_ax.grid(True)
    temp_canvas.draw()

# Update the graph with new fan speed readings
def update_fanspeed_graph():
    global fanspeed_readings, fan_speed_ax

    if len(fanspeed_readings) > 600:  # Limit the number of readings
        fanspeed_readings.pop(0)

    fan_speed_ax.clear()
    fan_speed_ax.plot(fanspeed_readings, marker='o', color='r')
    fan_speed_ax.set_title('Fan Speed Over Time')
    fan_speed_ax.set_ylabel('Fan Speed (%)')
    fan_speed_ax.set_xlabel('Reading')
    fan_speed_ax.set_xticks(range(0, len(fanspeed_readings), max(len(fanspeed_readings)//6, 1)))
    fan_speed_ax.set_ylim(0, 100)  # Set the y-axis to always range from 0 to 100
    fan_speed_ax.grid(True)
    fan_speed_canvas.draw()

# Function to check if delay has passed, then execute the fan setting command
def delayed_fan_setting(value):
    rounded_value = round(float(value))
    subprocess.call(['sudo', 'nbfc', 'set', '-s', str(rounded_value)])

# Function to update the temperature and fan speed labels and the graphs
def update_readings():
    global temperature_readings, fanspeed_readings
    temperature, fan_speed = get_system_readings()
    temp_label.config(text=f"Temperature: {temperature} °C")
    fan_speed_label.config(text=f"Fan Speed: {fan_speed}%")
    refresh_seconds = int(refresh_slider.get())

    # Append new readings to the lists and update the graphs if valid
    if temperature != "n/a" and fan_speed != "n/a":
        temperature_readings.append(float(temperature))
        fanspeed_readings.append(float(fan_speed))
        update_temperature_graph()
        update_fanspeed_graph()

    # Schedule the next update
    root.after(refresh_seconds * 1000, update_readings)

# Function to handle the slider and introduce a delay
def set_fan_speed(value):
    slider_value = round(float(value))
    manual_control_value_label.config(text=f"{slider_value}%")  # Display rounded value
    if current_control_mode == CONTROL_MODE_MANUAL:
        # Adjust the delay here by changing the first argument, it is currently set to 3000 milliseconds (3 seconds)
        delayed_fan_setting(slider_value)

# Function to enable automatic fan control
def set_auto_control():
    global current_control_mode
    current_control_mode = CONTROL_MODE_AUTO
    subprocess.call(['sudo', 'nbfc', 'set', '-a'])
    fan_speed_control_slider.config(state='disabled')  # Disable manual control slider

# Function to enable manual fan control via the slider
def set_manual_control():
    global current_control_mode
    current_control_mode = CONTROL_MODE_MANUAL
    fan_speed_control_slider.config(state='normal')  # Enable manual control slider

# Define width for the sliders
slider_length = 400

# Create temperature label
temp_label = ttk.Label(root, text="Temperature: ")
temp_label.pack(pady=10)

# Create fan speed label
fan_speed_label = ttk.Label(root, text="Fan Speed: ")
fan_speed_label.pack(pady=10)

# Create a slider for refresh interval
refresh_label = ttk.Label(root, text="Refresh Interval (seconds): ")
refresh_label.pack(pady=10)
refresh_slider = ttk.Scale(root, from_=1, to_=30, orient='horizontal', length=slider_length)
refresh_slider.pack(pady=(0, 10))
refresh_slider.set(5)  # Default value for the refresh interval

# Create a label to display the refresh slider's current value
refresh_value_label = ttk.Label(root, text="5 seconds")
refresh_value_label.pack(pady=(0, 20))
refresh_slider.configure(command=lambda value: refresh_value_label.config(text=f"{int(float(value))} seconds"))

# Create radio buttons for auto and manual control
control_mode = tk.StringVar(value=CONTROL_MODE_MANUAL)  # Set initial control mode to Manual
radio_auto_control = ttk.Radiobutton(root, text='Auto Control', value=CONTROL_MODE_AUTO, variable=control_mode, command=set_auto_control)
radio_auto_control.pack(pady=5)

radio_manual_control = ttk.Radiobutton(root, text='Manual Control', value=CONTROL_MODE_MANUAL, variable=control_mode, command=set_manual_control)
radio_manual_control.pack(pady=5)

# Create a slider for manual fan speed control
manual_control_label = ttk.Label(root, text="Manual Fan Speed (%): ")
manual_control_label.pack(pady=10)
fan_speed_control_slider = ttk.Scale(root, from_=0, to_=100, orient='horizontal', length=slider_length)
fan_speed_control_slider.pack(pady=(0, 10))
fan_speed_control_slider.set(50)  # Default value for fan speed

# Create a label to display the fan speed slider current value
manual_control_value_label = ttk.Label(root, text="50%")
manual_control_value_label.pack(pady=(0, 20))

# Update the command of the fan speed control slider to use the set_fan_speed function
fan_speed_control_slider.configure(command=set_fan_speed)

# Start the timer to update the readings
update_readings()

# Start the Tkinter main loop
root.mainloop()
```
---

./requirements.txt
```
matplotlib```
---
