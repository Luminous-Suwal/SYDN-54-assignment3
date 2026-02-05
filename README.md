# Image Processor - Professional Edition

A robust, object-oriented Python application for image processing and editing. Built with **Tkinter** for the GUI and **OpenCV** for professional-grade image manipulation.

## 📋 Features

### Core Functionality
-   **Open & Save**: Support for common image formats (`.jpg`, `.jpeg`, `.png`, `.bmp`).
-   **Undo/Redo**: Full history stack allowing you to step back and forth through your edits (up to 20 steps).
-   **Reset**: One-click restoration to the original image state.

### Image Filters & Tools
1.  **Grayscale**: Convert colorful images to professional black & white.
2.  **Edge Detection**: Highlight edges and contours using Canny edge detection.
3.  **Blur**: Adjustable Gaussian blur intensity (Slider: 1-15).
4.  **Brightness**: Adjust image brightness levels (Slider: -100 to +100).
5.  **Contrast**: Fine-tune contrast (Slider: 0.5x to 3.0x).
6.  **Rotation**: Quick rotate buttons for 90°, 180°, and 270°.
7.  **Flip**: Mirror images horizontally or vertically.
8.  **Resize**: Scale images from 10% to 200% with high-quality cubic interpolation.

### User Interface
-   **Scrollable Control Panel**: Easy access to all tools on any screen size.
-   **Status Bar**: Real-time display of filename and image dimensions (`WxH pixels`).
-   **Smart Scaling**: Images automatically scale to fit the view window while preserving aspect ratio.

## 🛠️ Installation

### Prerequisites
-   Python 3.6 or higher

### Dependencies
Install the required libraries using pip:

```bash
pip install opencv-python numpy pillow
```
*(Note: `tkinter` is usually included with Python installations)*

## 🚀 How to Run

1.  Navigate to the project directory.
2.  Run the main entry script:

```bash
python main.py
```

## 📖 Usage Guide

1.  **Load an Image**: Click `File > Open` or press `Ctrl+O`.
2.  **Apply Filters**: Use the control panel on the left.
    -   For sliders (Blur, Brightness, etc.), drag to the desired value and click the **Apply** button.
3.  **Resize**:
    -   Select a percentage (e.g., 50% for half size).
    -   Click "Apply Resize".
    -   *Note*: A popup will verify the change in pixel dimensions.
4.  **Save Your Work**:
    -   `File > Save` (`Ctrl+S`) to overwrite.
    -   `File > Save As` (`Ctrl+Shift+S`) to save as a new file.

## 📂 Project Structure

The project follows a modular Object-Oriented Design (OOD):

-   **`main.py`**: The entry point. Initializes the root window and launches the application.
-   **`gui.py`**: Handles the **View** and **Controller** aspects. Manages the Tkinter interface, event handling, and user interactions.
-   **`processor.py`**: The **Model**. Encapsulates all OpenCV logic, image data, and history state management.

## 📝 Author
Developed by Luminous Suwal and Group SYDN 54
