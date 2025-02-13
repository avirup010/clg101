# Bulk Image Resizer

## Overview
A simple tool to resize multiple images in bulk while maintaining aspect ratio.

## Features
- Select source and output folders for images
- Resize images to a specified width and height
- Maintain aspect ratio (optional)
- Progress tracking with a progress bar
- Cancel processing anytime

## Installation
Ensure you have Python installed, then install the required dependencies:
```bash
pip install customtkinter pillow
```

## Usage
Run the script:
```bash
python image_resizer.py
```
1. Select the source folder containing images.
2. Select the output folder.
3. Enter the desired width and height.
4. Click "Start Processing" to resize images.

## How It Works
1. The GUI is built using `customtkinter`.
2. Users select the source and output folders.
3. The width, height, and aspect ratio options are taken as input.
4. When "Start Processing" is clicked, images are resized using the `PIL` (Pillow) library.
5. Resizing maintains quality using the `LANCZOS` filter.
6. Progress is updated dynamically, and users can cancel at any time.

## License
This project is open-source and available under the MIT License.

