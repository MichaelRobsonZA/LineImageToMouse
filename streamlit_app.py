import streamlit as st
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt

st.title("Mouse Gesture Generator")

# Function to calculate gesture movements
def calculate_movements(points, desired_width, desired_height, screen_width=1920, screen_height=1080):
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
        file.write('            -- Reverse the gesture to loop\n')
        file.write('            for i = #verticalStrength, 1, -1 do\n')
        file.write('                MoveMouseRelative(-horizontalStrength[i] * lengthFactor, -verticalStrength[i] * lengthFactor)\n')
        file.write('                Sleep(loopDelay * speedFactor)\n')
        file.write('            end\n')
        file.write('        until not (IsMouseButtonPressed(1) and IsMouseButtonPressed(3))\n')
        file.write('    end\n')
        file.write('end\n')


# Upload image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "bmp"])
if uploaded_file is not None:
    image = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), cv2.IMREAD_GRAYSCALE)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    # Detect edges
    edges = cv2.Canny(image, 50, 150, apertureSize=3)
    st.image(edges, caption="Edges Detected", use_container_width=True)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        st.error("No contours detected in the image.")
    else:
        # Let the user select the contour
        contour_areas = [cv2.contourArea(contour) for contour in contours]
        selected_contour_idx = st.selectbox("Select a contour", range(len(contours)), format_func=lambda x: f"Contour {x} (Area = {contour_areas[x]})")
        line_contour = contours[selected_contour_idx]

        # Simplify the contour
        epsilon = 0.001 * cv2.arcLength(line_contour, True)
        points = cv2.approxPolyDP(line_contour, epsilon, True).squeeze()

        # Preview the gesture (preserve aspect ratio)
        gesture_width = max(points[:, 0]) - min(points[:, 0])
        gesture_height = max(points[:, 1]) - min(points[:, 1])
        aspect_ratio = gesture_width / gesture_height

        fig, ax = plt.subplots()
        ax.plot(points[:, 0], -points[:, 1], marker='o')
        ax.set_title("Gesture Preview")
        ax.set_xlabel("X Movement")
        ax.set_ylabel("Y Movement")
        ax.set_aspect(aspect_ratio)
        st.pyplot(fig)

        # User inputs for desired width, height, and screen resolution
        desired_width = st.number_input("Desired gesture width (in pixels)", value=500)
        desired_height = st.number_input("Desired gesture height (in pixels)", value=300)
        screen_width = st.number_input("Screen width (in pixels)", value=1920)
        screen_height = st.number_input("Screen height (in pixels)", value=1080)

        # Advanced settings for speed and length
        st.subheader("Advanced Settings")
        number_of_bullets = st.number_input("Number of bullets", value=30)
        fire_rate = st.number_input("Fire rate (bullets per second)", value=10)
        manual_speed = st.number_input("Manual speed adjustment (1 = slow, 10 = fast)", value=5)

        # Calculate loop delay based on fire rate and manual speed
        loop_delay = int((1000 / fire_rate) / manual_speed)  # Convert to milliseconds

        # Generate Lua script
        if st.button("Generate Lua Script"):
            horizontal_strength, vertical_strength = calculate_movements(points, desired_width, desired_height, screen_width, screen_height)
            write_lua_script(horizontal_strength, vertical_strength, loop_delay)
            st.success("Gesture script generated and saved to gesture_script.lua.")