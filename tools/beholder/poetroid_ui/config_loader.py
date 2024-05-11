# config_loader.py
import yaml

def load_configuration(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)
