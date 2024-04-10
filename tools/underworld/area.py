import os
import pygame
from configparser import ConfigParser
from sprites import Background

class Area:

    def __init__(self, area_folder):
        # Load the configuration file for the area
        config = ConfigParser()
        config_path = os.path.join(area_folder, "area.conf")
        print("Loading area config file:", config_path)
        config.read(config_path)

        self.name = config.get("Area", "name")
        self.description = config.get("Area", "description")

        # Load the background image and mask
        self.background = Background(
            os.path.join(area_folder, "lvl.png"), 0, 0)

        self.mask = pygame.image.load(
            os.path.join(area_folder, "lvl_mask.png"))

        # Initialize connecting areas as None
        self.connecting_areas = {"north": None,
                                 "east": None, "south": None, "west": None}

        # Only set connecting areas if they exist in the config file
        if config.has_section("ConnectingAreas"):
            for direction in self.connecting_areas.keys():
                if config.has_option("ConnectingAreas", direction):
                    self.connecting_areas[direction] = config.get(
                        "ConnectingAreas", direction)

    def get_connecting_area(self, direction):
        print("Connecting to area: ", self.connecting_areas.get(direction))
        return self.connecting_areas.get(direction)
