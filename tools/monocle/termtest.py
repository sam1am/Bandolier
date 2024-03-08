import subprocess

def run_command(command, cwd=None):
    """
    Runs a shell command and returns its output, error and exit status.

    Args:
    - command (str): The shell command to run.
    - cwd (str, optional): The current working directory to execute the command in.

    Returns:
    - output (str): The standard output of the command.
    - error (str): The standard error of the command.
    - exit_status (int): The exit status of the command.
    """
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd)
    stdout, stderr = process.communicate()
    exit_status = process.returncode
    return stdout, stderr, exit_status

def display_output_on_external(output, error, exit_status):
    """
    Placeholder function to display command output on an external display.
    Replace this function with your actual implementation for the external display.

    Args:
    - output (str): The standard output of the command.
    - error (str): The standard error of the command.
    - exit_status (int): The exit status of the command.
    """
    if exit_status == 0:
        print(output, end='', flush=True)
    else:
        print(f"Error: {error}\nExit Status: {exit_status}", flush=True)

def main():
    cwd = None  # Current working directory for commands
    while True:
        command = input("Enter a command (or type 'exit' to quit): ")
        if command.lower() == 'exit':
            print("Exiting...")
            break
        
        # Special handling for 'cd' command to change the working directory
        if command.startswith('cd '):
            path = command.split(' ', 1)[1]
            cwd = path  # Update the current working directory
            continue  # Skip executing 'cd' as a subprocess command

        stdout, stderr, exit_status = run_command(command, cwd)
        display_output_on_external(stdout, stderr, exit_status)

if __name__ == "__main__":
    main()
