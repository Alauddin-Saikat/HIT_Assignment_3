import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import cv2
from PIL import Image, ImageTk
import numpy as np

# ==============================
# Base Class: ImageProcessor
# Handles core image operations
# ==============================
class ImageProcessor:
    def __init__(self):
        # Encapsulated image data
        self.original_image = None
        self.cropped_image = None
        self.processed_image = None

    def load_image(self, path):
        # Loads image from disk using OpenCV
        try:
            image = cv2.imread(path)
            if image is None:
                raise ValueError("Selected file is not a valid image.")
            self.original_image = image
            self.processed_image = image.copy()
            return self.original_image
        except Exception as e:
            raise e

    def crop_image(self, x1, y1, x2, y2):
        # Crops the currently processed image based on coordinates
        try:
            cropped = self.processed_image[y1:y2, x1:x2]
            self.cropped_image = cropped
            self.processed_image = cropped.copy()
            return cropped
        except Exception as e:
            raise e

    def resize_image(self, scale_percent):
        # Resizes the cropped image using a percentage scale
        try:
            if self.cropped_image is None:
                return self.processed_image
            width = int(self.cropped_image.shape[1] * scale_percent / 100)
            height = int(self.cropped_image.shape[0] * scale_percent / 100)
            resized = cv2.resize(self.cropped_image, (width, height), interpolation=cv2.INTER_AREA)
            self.processed_image = resized
            return resized
        except Exception as e:
            raise e

    def save_image(self, image, path):
        # Saves the provided image to disk
        try:
            cv2.imwrite(path, image)
        except Exception as e:
            raise e

# =====================================================
# Subclass: AdvancedImageEditor
# Handles GUI and inherits functionality from ImageProcessor
# Demonstrates Inheritance and Polymorphism
# =====================================================
