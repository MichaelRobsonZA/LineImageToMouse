import cv2
import pyautogui
import numpy as np

# Load the image
image = cv2.imread('path_to_your_image.png', cv2.IMREAD_GRAYSCALE)

# Find the edges of the line
edges = cv2.Canny(image, 50, 150, apertureSize=3)

# Find contours
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Assuming the largest contour is the line
line_contour = max(contours, key=cv2.contourArea)

# Get the points along the line
points = cv2.approxPolyDP(line_contour, 0.01 * cv2.arcLength(line_contour, True), True)

# Move the mouse along the points
for point in points:
    pyautogui.moveTo(point[0][0], point[0][1])
    pyautogui.sleep(0.01)  # Adjust the sleep time as needed

print("Mouse path tracing complete.")
