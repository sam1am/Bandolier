# System Monitor GUI

## 📖 Project Description

This project is a Python GUI application that allows users to monitor and control their computer's system temperature and fan speed. It's built with Tkinter and heavily utilizes Matplotlib for rendering real-time graphs.
Main features of this application include:
- Monitoring system temperature.
- Monitoring fan speed.
- Real-time visual graphs for temperature and fan speed.
- Manual setting of fan speed.
- Automatic control of fan speed based on system readings.

The application communicates with the system's fan control utility using the `subprocess` module and parses the output with the `re` module. Two main control modes are available: automatic and manual, which can be toggled through the interface.

## 🛠️ Installation

To get started with this project, follow these steps:

1. Make sure Python is installed on your system. Python 3 is recommended.
2. Clone the repository or download the source code.
3. Navigate to the project directory where `requirements.txt` is located.
4. Install the required dependencies with the following command:

```bash
pip install -r requirements.txt
```
This will install Matplotlib and any other necessary Python packages.

## 🔧 Usage

Once you have installed the dependencies, you can run the application using:

```bash
python app.py
```

When the GUI launches, you can view the system temperature and fan speed in real-time through the graphs displayed. Use the sliders to adjust the fan speed manually or select the automatic mode to let the application adjust it according to the temperature readings.

## 🙌 Acknowledgements

Special thanks to the Matplotlib team for providing the plotting library that made the visual aspects of this application possible.

## 📄 License

This project is open-source and available under the [MIT License](https://opensource.org/licenses/MIT). Please refer to the LICENSE file for more details.

---

**Remember to always use your systems responsibly and ensure proper permissions when interfacing with system hardware and utilities.**