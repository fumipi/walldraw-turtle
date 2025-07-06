# Walldraw - Pen Plotter Project

A complete pen plotter system with hardware and software components for creating beautiful drawings.

## Project Structure

### 🐢 Turtle Plotter (`turtle_plotter/`)
The hardware and firmware components:
- **MicroPython code** for Raspberry Pi Pico
- **3D printed parts** (STL files)
- **Circuit schematics** and breadboard layouts
- **Sample CSV files** for testing

### 🌐 Vectorizer Web App (`vectorizer_web_app/`)
A Streamlit web application for converting images and SVG files to plotter coordinates:
- **SVG to CSV conversion**
- **Image edge detection**
- **Centerline extraction**
- **Path optimization and simplification**

## Features

### Turtle plotter
- Based on Hackaday "Minimal pico vertical plotter" project but further minimized : https://hackaday.io/project/193338-minimal-pico-vertical-plotter
- Uses 28BYJ-48 stepper motors to control drawing gondola up and down
- Uses SG90 servo to control pen up/down
- Power supply from PC USB port
- MicroPython implementation with turtle graphics like library functions (currently goto() only)
- **Simple operation**: Just run `main.py` in Thonny IDE
- **Automatic behavior**: 
  - If `points.csv` is present → draws the specified path
  - If no CSV file → draws a 100mm × 100mm test square

### Vectorizer web app
- Web-based vectorizer with real-time preview
- Multiple input methods (SVG, edge detection, centerline extraction)
- Path optimization for efficient plotting
- Coordinate system centered on paper

## Quick Start

### Turtle Plotter Setup
1. **Set up the hardware**: See `turtle_plotter/` for assembly instructions
2. **Install Thonny IDE**: Download from https://thonny.org/
3. **Connect Raspberry Pi Pico** to your computer via USB
4. **Open `turtle_plotter/code/main.py`** in Thonny and run it
5. **Upload `points.csv`** to the Pico (optional - will draw test square if not present)

### Vectorizer Web App Setup
1. **Install the web app**: 
   ```bash
   cd vectorizer_web_app
   pip install -r requirements.txt
   streamlit run vectorizer_app.py
   ```
2. **Convert your images/SVGs** to CSV format
3. **Download the CSV** and upload to the Pico as `points.csv`

## To Do
- Update more turtle functions

## License

This project is licensed under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)** or later.

This means you are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made

For more details, see: https://creativecommons.org/licenses/by/4.0/

---

*Made with ❤️ by Craft Robot Workshop*




