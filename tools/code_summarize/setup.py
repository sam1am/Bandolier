#!/usr/bin/env python3

import os
import subprocess
import sys
import platform
from pathlib import Path

def is_windows():
    return platform.system().lower() == "windows"

def get_script_dir():
    # This returns the absolute path of the directory where the script is located
    return Path(__file__).parent.absolute()

def setup_virtualenv_and_run_script(script_dir):
    venv_activate = script_dir / 'venv' / 'bin' / 'activate'
    run_command = f'source {venv_activate} && python {script_dir / "app.py"}'
    return run_command


def get_shell_configuration_path():
    if is_windows():
        # The path to profile script for PowerShell or Command Prompt can vary
        # This is for PowerShell
        return Path.home() / "Documents" / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1"
    elif platform.system().lower() == "darwin":
        return Path.home() / ".zshrc"
    else:
        return Path.home() / ".bashrc"

def create_virtual_environment(script_dir):
    venv_path = script_dir / "venv"
    if not venv_path.is_dir():
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)])
    return venv_path

def activate_virtual_environment(venv_path):
    if is_windows():
        activate_script = venv_path / "Scripts" / "activate.bat"
        os.system(f'cmd /k "{activate_script}"')
    else:
        activate_script = venv_path / "bin" / "activate"
        os.environ["VIRTUAL_ENV"] = str(venv_path)
        old_path = os.environ["PATH"]
        os.environ["PATH"] = f"{str(venv_path / 'bin')}{os.pathsep}{old_path}"
        subprocess.run(["source", str(activate_script)], shell=True)

def install_dependencies(script_dir, venv_path):
    requirements_path = script_dir / "requirements.txt"
    if requirements_path.is_file():
        subprocess.run(["pip", "install", "-r", str(requirements_path)])
    else:
        print("No requirements.txt found.")

def set_alias(run_command):
    shell_config_path = get_shell_configuration_path()
    alias_name = "code_summarize"
    alias_command = f'alias {alias_name}="{run_command}"'
    
    if shell_config_path.is_file():
        with open(shell_config_path, "r+") as file:
            content = file.read()
            if alias_command not in content:
                file.write(f"\n# Alias for code_summarize script\n{alias_command}\n")
                print(f"Alias added to {shell_config_path}. Please restart your shell or run 'source {shell_config_path}' to use it.")
            else:
                print("Alias already exists in your shell profile.")

def main():
    script_dir = get_script_dir()
    
    venv_path = create_virtual_environment(script_dir)
    activate_virtual_environment(venv_path)
    
    install_dependencies(script_dir, venv_path)
    
    set_alias(script_dir)

if __name__ == "__main__":
    script_dir = get_script_dir()
    run_command = setup_virtualenv_and_run_script(script_dir)

    # set_alias should use `run_command` to create an alias
    set_alias(run_command)

