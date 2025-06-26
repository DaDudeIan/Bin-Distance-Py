import cv2
import numpy as np
import matplotlib.pyplot as plt
from entities.doors import Door
from entities.bins import Bin


class World:
    def __init__(self, name: str, img_path: str):
        self.name = name
        self.img_path = img_path
        self.img = None
        self.bw_img = None
        self.doors = []
        self.bins = []

        self.read_image()
        self.find_doors()
        self.find_bins()
        self.bw_image()


    def read_image(self):
        """Read the image from img_path into a numpy array."""
        print(f"Reading image from {self.img_path} for world '{self.name}'")
        try:
            self.img = cv2.imread(self.img_path)
            if self.img is None:
                print(f"Warning: Could not read image from {self.img_path}")
            else:
                print(f"Successfully loaded image with shape: {self.img.shape}")
        except Exception as e:
            print(f"Error reading image: {e}")
            self.img = None

    def find_doors(self):
        if self.img is None:
            print(f"No image loaded for world '{self.name}'. Cannot find doors.")
            return

        # Convert image to HSV for better color segmentation
        hsv_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)

        # Define range for blue color in HSV
        lower_blue = np.array([100, 150, 50])
        upper_blue = np.array([140, 255, 255])

        # Create mask for blue pixels
        blue_mask = cv2.inRange(hsv_img, lower_blue, upper_blue)

        # Find contours of blue regions
        contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Process each contour to find the center
        door_counter = 1
        for contour in contours:
            # Calculate the moments of the contour
            M = cv2.moments(contour)
            if M["m00"] != 0:
                # Calculate the center of the contour
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                door = Door(door_counter, cx, cy)
                self.add_door(door)
                door_counter += 1
            else:
                print("Skipping contour with zero area.")

        print(f"Found {len(self.doors)} doors in world '{self.name}'.")
        if self.doors:
            print("Door coordinates:")
            for door in self.doors:
                print(f"  Door {door.number}: ({door.x}, {door.y})")

    def find_bins(self):
        if self.img is None:
            print(f"No image loaded for world '{self.name}'. Cannot find bins.")
            return

        # Convert image to HSV for better color segmentation
        hsv_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)

        # Define range for red color in HSV
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])

        # Create masks for red pixels (handle wrap-around in HSV)
        red_mask1 = cv2.inRange(hsv_img, lower_red1, upper_red1)
        red_mask2 = cv2.inRange(hsv_img, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)

        # Find contours of red regions
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Process each contour to find the center
        bin_counter = 1
        for contour in contours:
            # Calculate the moments of the contour
            M = cv2.moments(contour)
            if M["m00"] != 0:
                # Calculate the center of the contour
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                bin_entity = Bin(bin_counter, cx, cy)
                self.add_bin(bin_entity)
                bin_counter += 1
            else:
                print("Skipping contour with zero area.")

        print(f"Found {len(self.bins)} bins in world '{self.name}'.")
        if self.bins:
            print("Bin coordinates:")
            for bin_entity in self.bins:
                print(f"  Bin {bin_entity.number}: ({bin_entity.x}, {bin_entity.y})")

    def add_door(self, door):
        # Check if a door with the same coordinates already exists
        for existing_door in self.doors:
            if existing_door.x == door.x and existing_door.y == door.y:
                return  # Don't add duplicate doors
        self.doors.append(door)

    def add_bin(self, bin_entity):
        # Check if a bin with the same coordinates already exists
        for existing_bin in self.bins:
            if existing_bin.x == bin_entity.x and existing_bin.y == bin_entity.y:
                return  # Don't add duplicate bins
        self.bins.append(bin_entity)

    def bw_image(self):
        """Convert the image to black and white for pathfinding.
        Black pixels (0) are passable, white pixels (255) are obstacles."""
        if self.img is None:
            print(f"No image loaded for world '{self.name}'. Cannot convert to black and white.")
            return None
        
        # Convert the image to grayscale
        gray_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        
        # Use a threshold that allows doors and bins to be passable
        # Door pixel: 51, Bin pixel: 76 - use threshold of 50 to include door
        # After inversion, pixels <= threshold become passable (0)
        _, bw_img = cv2.threshold(gray_img, 10, 255, cv2.THRESH_BINARY)
        
        # Invert the image so that dark areas (including doors/bins) are passable (0)
        # and light areas (walls) are obstacles (255)
        bw_img = cv2.bitwise_not(bw_img)

        self.bw_img = bw_img
        print(f"Converted image to black and white for world '{self.name}'.")

    def find_paths(self):
        """Find paths from each door to its closest bin using A* algorithm"""
        if self.bw_img is None:
            print(f"No black and white image available for pathfinding in world '{self.name}'.")
            return
        
        for door in self.doors:
            closest_bin = door.find_closest_bin(self.bins, self.bw_img)
            if closest_bin:
                print(f"Door {door.number} at ({door.x}, {door.y}) -> Bin {closest_bin.number} at ({closest_bin.x}, {closest_bin.y})")
            else:
                print(f"Door {door.number} at ({door.x}, {door.y}) -> No accessible bin found")