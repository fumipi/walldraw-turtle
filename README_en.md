[日本語版はこちら → README.md](./README.md)
# 🐢 Kame Plotter

A minimal vertical pen plotter shaped like a turtle, built with Raspberry Pi Pico and MicroPython.  
It draws line art based on coordinates stored in a CSV file.

---

## Project Overview

### **Hardware & Firmware**
- MicroPython control code inspired by turtle graphics  
- Uses **Raspberry Pi Pico**, **two 28BYJ-48 stepper motors**, and **one SG90 servo motor**  
- Powered via USB  
- Includes **3D printed parts (STL)**, **circuit schematics**, and **sample CSV files**

---

## How to Use

### **Turtle Plotter Setup**
1. 3D print the turtle parts in the `stl` folder  
2. Wire the circuit following the schematic in the `schematic` folder  
3. Install [Thonny IDE](https://thonny.org/)  
4. Connect the Raspberry Pi Pico via USB and install MicroPython  
   ([reference guide](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html))  
5. Drag and drop all files from the `code` folder onto the Pico  
6. Open `turtle_plotter/code/main.py` in Thonny and run it  
7. (Optional) Upload `points.csv` to the Pico  

**Operation Modes**
- If `points.csv` exists → draws the path from the CSV file  
- If not → draws a 100mm × 100mm test square defined in `main.py`

---

### Line Data Generator App
Visit [https://vectorizer.streamlit.app/](https://vectorizer.streamlit.app/) and upload your image.  
Download the generated CSV file and save it to your Pico as `points.csv`.

**Main Features**
- Edge detection and centerline extraction  
- Path optimization and simplification  
- Image → CSV conversion  
  (Also supports SVG and G-code output, though not used in this plotter)

---

## More Details
See the full build guide on [note.com](https://note.com/fumi_note/n/n50b205639b7f)

---

## Reference Project
- Based on [Make a Raspberry Pi Pico pen plotter](https://www.raspberrypi.com/news/make-a-raspberry-pi-pico-pen-plotter/)
