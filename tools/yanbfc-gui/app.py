# import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import subprocess
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter.simpledialog import askstring
import sys

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# The lists to store temperature and fan speed readings
temperature_readings = []
fanspeed_readings = []

# Add variables to keep track of the control mode (auto or manual)
CONTROL_MODE_AUTO = "auto"
CONTROL_MODE_MANUAL = "manual"
current_control_mode = CONTROL_MODE_MANUAL
fan_speed_adjustment_delay = None

# Variables to store TDP settings
stapm_limit = 12000
fast_limit = 10000
slow_limit = 3000

# Ask for sudo password upfront
sudo_password = askstring("Password", "Enter sudo password:", show='*')
if sudo_password is None:
    print("No sudo password provided. Exiting program.")
    sys.exit(1)

# Function to fetch the current temperature and fan speed
def get_system_readings():
    try:
        output = subprocess.check_output(['nbfc', 'status', '-a'], text=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute 'nbfc status -a': {e}")
        return "n/a", "n/a"

    temperature_match = re.search(r'Temperature\s+:\s+(\d+\.?\d*)', output)
    fan_speed_match = re.search(r'Current fan speed\s+:\s+(\d+\.?\d*)', output)

    temperature = temperature_match.group(1) if temperature_match else "n/a"
    fan_speed = fan_speed_match.group(1) if fan_speed_match else "n/a"
    print(f"Temperature: {temperature}, Fan Speed: {fan_speed}")
    return temperature, fan_speed

# Function to apply TDP settings
def apply_tdp_settings():
    global stapm_limit, fast_limit, slow_limit
    try:
        subprocess.run(['sudo', '-S', 'ryzenadj', f'--stapm-limit={stapm_limit}', f'--fast-limit={fast_limit}', f'--slow-limit={slow_limit}'], input=sudo_password + '\n', text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error applying TDP settings: {e}")

# Create the main window
root = ttk.Window(themename="darkly")
root.title("Ryzen Master and Commander")

# Create a main frame with a scrollbar
main_frame = ttk.Frame(root)
main_frame.pack(fill=ttk.BOTH, expand=True)

canvas = ttk.Canvas(main_frame)
canvas.pack(side=ttk.LEFT, fill=ttk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(main_frame, orient=ttk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=ttk.RIGHT, fill=ttk.Y)

canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

content_frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=content_frame, anchor='nw')

# Define two global figures and axes for plotting the temperature and fan speed
temp_fig, temp_ax = plt.subplots(figsize=(6, 1.5))
temp_canvas = FigureCanvasTkAgg(temp_fig, master=content_frame)
temp_canvas.get_tk_widget().pack()

fan_speed_fig, fan_speed_ax = plt.subplots(figsize=(6, 1.5))
fan_speed_canvas = FigureCanvasTkAgg(fan_speed_fig, master=content_frame)
fan_speed_canvas.get_tk_widget().pack()

# Update the graph with new temperature readings
def update_temperature_graph():
    global temperature_readings, temp_ax, temp_canvas

    # Ensure `temperature_readings` has at most 600 elements
    temperature_readings = temperature_readings[-600:]

    temp_ax.clear()
    temp_ax.plot(temperature_readings, marker='o', color='b')
    temp_ax.set_title('Temperature Over Time')
    temp_ax.set_ylabel('Temperature (°C)')
    temp_ax.set_xlabel('Reading')
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
    # Set the y-axis to always range from 0 to 100
    fan_speed_ax.set_ylim(0, 100)
    fan_speed_ax.grid(True)
    fan_speed_canvas.draw()

# Function to update the temperature, fan speed, and TDP labels and the graphs
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

    # Update TDP settings
    stapm_limit_label.config(text=f"STAPM Limit: {stapm_limit}")
    fast_limit_label.config(text=f"Fast Limit: {fast_limit}")
    slow_limit_label.config(text=f"Slow Limit: {slow_limit}")

    # Schedule the next update
    root.after(refresh_seconds * 1000, update_readings)

# Function to handle the slider and introduce a delay
def delayed_fan_setting(value):
    global fan_speed_adjustment_delay
    if fan_speed_adjustment_delay is not None:
        root.after_cancel(fan_speed_adjustment_delay)
    fan_speed_adjustment_delay = root.after(1000, apply_fan_speed, value)

# Function to apply the fan speed setting after delay
def apply_fan_speed(value):
    slider_value = round(float(value))
    try:
        subprocess.run(['sudo', '-k'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)   # Reset sudo timeout
        subprocess.run(['sudo', '-S', 'nbfc', 'set', '-s', str(slider_value)], input=sudo_password + '\n', text=True)
        # Update the label with the rounded value
        manual_control_value_label.config(text=f"{slider_value}%")
    except subprocess.CalledProcessError as e:
        print(f"Error setting fan speed: {e}")

# Function to enable automatic fan control
def set_auto_control():
    global current_control_mode
    current_control_mode = CONTROL_MODE_AUTO
    try:
        subprocess.run(['sudo', '-k'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)   # Reset sudo timeout
        subprocess.run(['sudo', '-S', 'nbfc', 'set', '-a'], input=sudo_password + '\n', text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error setting automatic fan control: {e}")
    # Disable manual control slider
    fan_speed_control_slider.config(state='disabled')

# Function to enable manual fan control via the slider
def set_manual_control():
    global current_control_mode
    current_control_mode = CONTROL_MODE_MANUAL
    # Enable manual control slider
    fan_speed_control_slider.config(state='normal')

# Function to update TDP settings
def update_tdp_settings():
    global stapm_limit, fast_limit, slow_limit
    stapm_limit = int(stapm_limit_entry.get())
    fast_limit = int(fast_limit_entry.get())
    slow_limit = int(slow_limit_entry.get())
    apply_tdp_settings()

# Create temperature label
temp_label = ttk.Label(content_frame, text="Temperature: ")
temp_label.pack(pady=5)

# Create fan speed label
fan_speed_label = ttk.Label(content_frame, text="Fan Speed: ")
fan_speed_label.pack(pady=5)

# Define width for the sliders
slider_length = 300

# Create a slider for refresh interval
refresh_label = ttk.Label(content_frame, text="Refresh Interval (seconds): ")
refresh_label.pack(pady=5)
refresh_slider = ttk.Scale(content_frame, from_=1, to_=30, orient='horizontal', length=slider_length)
refresh_slider.pack(pady=(0, 5))
refresh_slider.set(5)  # Default value for the refresh interval

# Create a slider for manual fan speed control
manual_control_label = ttk.Label(content_frame, text="Manual Fan Speed (%): ")
manual_control_label.pack(pady=5)
fan_speed_control_slider = ttk.Scale(content_frame, from_=0, to_=100, orient='horizontal', length=slider_length, command=delayed_fan_setting)
fan_speed_control_slider.pack(pady=(0, 5))
fan_speed_control_slider.set(50)  # Default value for fan speed

# Create a label to display the fan speed slider current value
manual_control_value_label = ttk.Label(content_frame, text="50%")
manual_control_value_label.pack(pady=(0, 10))

# Create radio buttons for auto and manual control
control_mode_frame = ttk.Frame(content_frame)
control_mode_frame.pack(pady=5)
radio_auto_control = ttk.Radiobutton(control_mode_frame, text='Auto Control', value=CONTROL_MODE_AUTO, variable=current_control_mode, command=set_auto_control)
radio_auto_control.grid(row=0, column=0, padx=5)
radio_manual_control = ttk.Radiobutton(control_mode_frame, text='Manual Control', value=CONTROL_MODE_MANUAL, variable=current_control_mode, command=set_manual_control)
radio_manual_control.grid(row=0, column=1, padx=5)

# Create TDP labels and entry fields
tdp_frame = ttk.Frame(content_frame)
tdp_frame.pack(pady=5)

stapm_limit_label = ttk.Label(tdp_frame, text="STAPM Limit: ")
stapm_limit_label.grid(row=0, column=0, padx=5)
stapm_limit_entry = ttk.Entry(tdp_frame)
stapm_limit_entry.grid(row=0, column=1, padx=5)
stapm_limit_entry.insert(0, str(stapm_limit))

fast_limit_label = ttk.Label(tdp_frame, text="Fast Limit: ")
fast_limit_label.grid(row=1, column=0, padx=5)
fast_limit_entry = ttk.Entry(tdp_frame)
fast_limit_entry.grid(row=1, column=1, padx=5)
fast_limit_entry.insert(0, str(fast_limit))

slow_limit_label = ttk.Label(tdp_frame, text="Slow Limit: ")
slow_limit_label.grid(row=2, column=0, padx=5)
slow_limit_entry = ttk.Entry(tdp_frame)
slow_limit_entry.grid(row=2, column=1, padx=5)
slow_limit_entry.insert(0, str(slow_limit))

apply_tdp_button = ttk.Button(tdp_frame, text="Apply TDP Settings", command=update_tdp_settings)
apply_tdp_button.grid(row=3, column=0, columnspan=2, pady=5)

# Start the timer to update the readings
update_readings()

# Start the Tkinter main loop
root.mainloop()