import cv2
import numpy as np
import json
import argparse
import tkinter as tk
from tkinter import filedialog
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
import unittest


# Function to select an image using a GUI
def select_image():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(title="Select an image", filetypes=[("Image files", "*.jpg *.png *.bmp")])
    return file_path


# Function to preview the gesture
def preview_gesture(points):
    plt.plot(points[:, 0], -points[:, 1], marker='o')  # Invert y-axis for correct orientation
    plt.title("Gesture Preview")
    plt.xlabel("X Movement")
    plt.ylabel("Y Movement")
    plt.show()


# Function to calculate gesture movements
def calculate_movements(points, desired_width, desired_height):
    horizontal_strength = []
    vertical_strength = []

    # Scale to the desired size
    gesture_width = max(points[:, 0]) - min(points[:, 0])
    gesture_height = max(points[:, 1]) - min(points[:, 1])
    scale_x = desired_width / gesture_width
    scale_y = desired_height / gesture_height

    for i in range(1, len(points)):
        dx = (points[i][0] - points[i - 1][0]) * scale_x
        dy = (points[i][1] - points[i - 1][1]) * scale_y
        horizontal_strength.append(int(dx))
        vertical_strength.append(int(dy))

    # Smooth the movements
    horizontal_strength = gaussian_filter(horizontal_strength, sigma=1)
    vertical_strength = gaussian_filter(vertical_strength, sigma=1)

    return horizontal_strength, vertical_strength


# Function to write movements to a Lua script
def write_lua_script(horizontal_strength, vertical_strength, loop_delay):
    with open('gesture_script.lua', 'w') as file:
        file.write('local verticalStrength = {' + ', '.join(map(str, vertical_strength)) + '}\n')
        file.write('local horizontalStrength = {' + ', '.join(map(str, horizontal_strength)) + '}\n')
        file.write('local defaultLength = 700 -- Default length scale\n')
        file.write('local defaultSpeed = 3 -- Default speed scale\n')
        file.write(f'local loopDelay = {loop_delay}\n\n')

        file.write('function OnEvent(event, arg)\n')
        file.write('    if event == "PROFILE_ACTIVATED" then\n')
        file.write('        EnablePrimaryMouseButtonEvents(true)\n')
        file.write('    end\n\n')

        file.write('    if event == "MOUSE_BUTTON_PRESSED" and arg == 1 and IsMouseButtonPressed(3) then\n')
        file.write('        local startTime = GetRunningTime()\n')
        file.write('        local lengthFactor = defaultLength / 700\n')
        file.write('        local speedFactor = defaultSpeed / 3\n')
        file.write('        repeat\n')
        file.write('            for i = 1, #verticalStrength do\n')
        file.write('                MoveMouseRelative(horizontalStrength[i] * lengthFactor, verticalStrength[i] * lengthFactor)\n')
        file.write('                Sleep(loopDelay * speedFactor)\n')
        file.write('            end\n')
        file.write('        until not (IsMouseButtonPressed(1) and IsMouseButtonPressed(3))\n')
        file.write('    end\n')
        file.write('end\n')


# Main function
def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate a mouse gesture from an image.")
    parser.add_argument("--image", help="Path to the image file")
    parser.add_argument("--contour", type=int, default=0, help="Index of the contour to use")
    parser.add_argument("--width", type=int, default=500, help="Desired gesture width")
    parser.add_argument("--height", type=int, default=300, help="Desired gesture height")
    parser.add_argument("--speed", type=float, default=5, help="Gesture speed (1 = slow, 10 = fast)")
    args = parser.parse_args()

    # Load the image
    image_path = args.image if args.image else select_image()
    try:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise FileNotFoundError("Image not found or could not be loaded.")
    except Exception as e:
        print(f"Error: {e}")
        exit()

    # Resize the image for faster processing
    image = cv2.resize(image, (640, 480))

    # Detect edges
    edges = cv2.Canny(image, 50, 150, apertureSize=3)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("Error: No contours detected in the image.")
        exit()

    # Let the user select the contour
    print("Detected contours:")
    for idx, contour in enumerate(contours):
        print(f"Contour {idx}: Area = {cv2.contourArea(contour)}")
    selected_contour_idx = args.contour if args.contour else int(input("Enter the index of the contour to use: "))
    line_contour = contours[selected_contour_idx]

    # Simplify the contour
    epsilon = 0.001 * cv2.arcLength(line_contour, True)
    points = cv2.approxPolyDP(line_contour, epsilon, True).squeeze()

    # Calculate gesture movements
    horizontal_strength, vertical_strength = calculate_movements(points, args.width, args.height)

    # Preview the gesture
    preview_gesture(points)

    # Write movements to a Lua script
    loop_delay = int(14 / args.speed)  # Adjust the delay based on speed
    write_lua_script(horizontal_strength, vertical_strength, loop_delay)

    print("Gesture script generated and saved to gesture_script.lua.")


# Unit tests
class TestGestureGenerator(unittest.TestCase):
    def test_image_loading(self):
        self.assertIsNotNone(cv2.imread("test_image.jpg", cv2.IMREAD_GRAYSCALE))


if __name__ == "__main__":
    main()