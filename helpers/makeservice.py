import os
import subprocess
import argparse

# Create the parser
parser = argparse.ArgumentParser(description='Python script to manage services.')
parser.add_argument('-s', '--script_name', help='The Python script to run.')
args = parser.parse_args()

# Get the current directory
dir = os.getcwd()

# Get the current user and group
user = os.getenv('USER')
group = subprocess.check_output('id -gn', shell=True).decode().strip()

# Get the current directory name for service
dirname = os.path.basename(dir)

# Get the path to the current Python interpreter
python_path = subprocess.check_output('which python', shell=True).decode().strip()

# Check if script name is provided and exists
if not args.script_name:
    print("No script name provided.")
    exit(1)
elif not os.path.isfile(args.script_name):
    print("No script found with name " + args.script_name)
    exit(1)

# Define the service and file name
service_name = "bandolier-" + dirname + "-" + os.path.splitext(args.script_name)[0]

# Define the systemd service configuration
config = f"""
[Unit]
Description={service_name}

[Service]
ExecStart={python_path} {os.path.join(dir, args.script_name)}
Restart=always
User={user}
Group={group}
WorkingDirectory={dir}

[Install]
WantedBy=multi-user.target
"""

# Write the configuration to a file
with open(service_name + ".service", 'w') as f:
    f.write(config)

print("Service file written to " + service_name + ".service")
print(config)

answer = input("Do you want to install and activate the service? (yes/no)\n")

if answer == "yes":
    subprocess.call(['sudo', 'cp', service_name + ".service", '/etc/systemd/system/'])
    subprocess.call(['sudo', 'systemctl', 'enable', service_name])
    subprocess.call(['sudo', 'systemctl', 'start', service_name])
    print("Service installed and activated.")
