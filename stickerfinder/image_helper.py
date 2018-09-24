"""Some static stuff or helper functions for sticker finder bot."""
import cv2
import numpy as np
from PIL import Image


def preprocess_image(image):
    """Preprocessing the Image for tesseract."""
    # Upscale an image x2
    image = image.resize((4*image.size[0], 4*image.size[1]), resample=Image.LANCZOS)
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.GaussianBlur(image, (5, 5), 0)

    return image
