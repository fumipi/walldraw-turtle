# Simple Pico and MicroPython Vertical Plotter

A minimal vertical plotter built with Raspberry Pi Pico and MicroPython that draws pictures from coordinates provided in CSV format or Python lists.

## Project Structure

### 🐢 Turtle Plotter (`turtle_plotter/`)
Hardware and firmware components for Raspberry Pi Pico:
- **MicroPython code** with turtle graphics functions
- **3D printed parts** (STL files) and circuit schematics
- **Hardware**: 28BYJ-48 stepper motors, SG90 servo, USB power
- **Sample CSV files** for testing
- Based on [Make a Raspberry Pi Pico pen plotter]( https://www.raspberrypi.com/news/make-a-raspberry-pi-pico-pen-plotter/) 

### 🌐 Vectorizer Web App (`vectorizer_web_app/`)
A Streamlit web application for converting images and SVG files to plotter coordinates:
- **SVG to CSV conversion**
- **Image edge detection**
- **Centerline extraction**
- **Path optimization and simplification**
- **🌐 Live Demo**: https://vectorizer.streamlit.app/



## Quick Start

### Turtle Plotter Setup
1. **Set up the hardware**: See `turtle_plotter/` for assembly instructions
2. **Install Thonny IDE**: Download from https://thonny.org/
3. **Connect Raspberry Pi Pico** to your computer via USB
4. **Open `turtle_plotter/code/main.py`** in Thonny and run it
5. **Upload `points.csv`** to the Pico (optional - will draw test square if not present)

**Operation Modes:**
- **CSV Mode**: If `points.csv` is present → draws the specified path from CSV
- **Test Mode**: If no CSV file → draws coordinates from the `test_drawing` Python list in `main.py` (default: 100mm × 100mm square - you can modify these coordinates freely)

### Vectorizer Web App Setup
**Option 1: Use the Live App (Recommended)**
- Visit https://vectorizer.streamlit.app/ to use the app immediately

**Option 2: Run Locally**
1. **Install the web app**: 
   ```bash
   cd vectorizer_web_app
   pip install -r requirements.txt
   streamlit run vectorizer_app.py
   ```
2. **Convert your images/SVGs** to CSV format
3. **Download the CSV** and upload to the Pico as `points.csv`

## To Do
- Implement more turtle functions

## License

This project is licensed under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)** or later.

This means you are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made

For more details, see: https://creativecommons.org/licenses/by/4.0/




