import os
import json
from dotenv import load_dotenv

class ConfigHandler:
    default_vault_dir = 'vault'

    def __init__(self):
        load_dotenv()
        self.config_file = 'config.json'
        self.config = self.load_config()
        
        self.vault_dir = self.config.get('vault_dir', self.default_vault_dir)

    def create_directory(self, directory_name):
        directory_path = os.path.join(os.getcwd(), directory_name)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        return directory_path

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                print("Loading config file")
                return json.load(f)
        else:
            return {}

    def save_config(self):
        with open(self.config_file, 'w') as f:  
           json.dump(self.config, f, indent=4)
        self.vault_dir = self.config.get('vault_dir', self.default_vault_dir)
