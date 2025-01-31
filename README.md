# LineImageToMouse
convert a line in an image into a path for mouse movements
Mouse Gesture Generator

This project allows users to upload an image, trace a contour, and convert the traced motion into a Lua script for use with gaming macros.

Features

Upload an image and detect edges

Select a contour and generate a gesture

Adjust gesture width, height, and speed settings

Generate a Lua script for mouse movement automation

Requirements

Ensure you have the following installed:

Python 3.8+

pip (Python package manager)

Streamlit

OpenCV

NumPy

SciPy

Matplotlib

Installation

Clone this repository:

git clone https://github.com/your-repository/LineImageToMouse.git
cd LineImageToMouse

Install dependencies:

pip install -r requirements.txt

Running the Streamlit App

To start the application, run:

streamlit run streamlit_app.py

This will launch the Streamlit interface in your web browser.

Usage

Upload an image (JPG or PNG format)

Select a detected contour

Adjust movement settings

Generate and download the Lua script

Use the Lua script for mouse automation

Notes

Ensure the Lua script is placed in the correct directory for use with your gaming setup.

Modify streamlit_app.py if additional customization is needed.

License

This project is licensed under the MIT License.