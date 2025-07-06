# Turtle Plotter - Hardware & Firmware

A minimal vertical pen plotter based on the Hackaday "Minimal pico vertical plotter" project, further optimized and simplified.

## Hardware Components

### Electronics
- **Raspberry Pi Pico** - Main controller
- **2x 28BYJ-48 stepper motors** - Control drawing gondola movement
- **1x SG90 servo motor** - Controls pen up/down movement
- **Power supply** - USB from PC (no external power needed)

### Mechanical Parts
- **3D printed components** (see `stl/` folder):
  - `turtle_bottom.stl` - Base plate
  - `turtle_cover.stl` - Top cover
  - `motor_mount.stl` - Motor mounting brackets
  - `spur.stl` - Spur gears
  - `weight.stl` - Counterweight

## Assembly

1. **Print all STL files** with appropriate settings for your printer
2. **Assemble mechanical parts** following the schematic in `schematic/`
3. **Wire electronics** according to the breadboard layout
4. **Mount motors and servo** using the 3D printed brackets

## Software Setup

### Requirements
- **Thonny IDE** - Download from https://thonny.org/
- **MicroPython firmware** - Already included as `z_RPI_PICO-20250415-v1.25.0.uf2`

### Installation
1. **Connect Raspberry Pi Pico** to your computer via USB
2. **Open Thonny IDE**
3. **Select MicroPython (Raspberry Pi Pico)** as the interpreter
4. **Upload all files** from the `code/` folder to the Pico

## Operation

### Running the Plotter
1. **Open `main.py`** in Thonny
2. **Click the "Run" button** (green play button)
3. **The plotter will automatically start**

### Drawing Behavior
- **With `points.csv`**: Draws the path specified in the CSV file
- **Without `points.csv`**: Draws a 100mm × 100mm test square

### CSV File Format
The `points.csv` file should contain coordinates in this format:
```
x1,y1;x2,y2;x3,y3
x4,y4;x5,y5;x6,y6
```
Where:
- Each line represents a continuous path
- Coordinates are in millimeters
- Origin (0,0) is at the center of the paper
- Positive X is right, positive Y is up

### Creating CSV Files
Use the **Vectorizer Web App** in the `../vectorizer_web_app/` folder to convert:
- SVG files
- Images (edge detection)
- Images (centerline extraction)

## File Structure

```
turtle_plotter/
├── code/              # MicroPython source files
│   ├── main.py        # Main program (run this!)
│   ├── plotter.py     # Plotter control functions
│   ├── stepper.py     # Stepper motor control
│   ├── servo.py       # Servo motor control
│   └── config.py      # Configuration settings
├── schematic/         # Circuit diagrams
├── stl/              # 3D printable parts
├── sample/           # Example CSV files
└── BOM.md            # Bill of materials
```

## Troubleshooting

### Common Issues
- **Plotter not moving**: Check motor connections and power
- **Incorrect positioning**: Verify stepper motor wiring
- **Pen not lifting**: Check servo connections and calibration
- **File not found**: Ensure `points.csv` is uploaded to the Pico

### Calibration
- Adjust `config.py` settings for your specific setup
- Calibrate servo angles for pen up/down positions

## Current Features
- ✅ Basic movement with `goto(x, y)`
- ✅ Automatic pen up/down
- ✅ CSV file reading
- ✅ Test pattern when no CSV present

## Planned Features
- More turtle graphics functions (circle, line, etc.)
- Advanced path optimization

## Credits
Based on the Hackaday project: https://hackaday.io/project/193338-minimal-pico-vertical-plotter 