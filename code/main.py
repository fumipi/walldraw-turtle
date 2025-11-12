from machine import Pin
import time
import os
from config import *
from plotter import WallPlotter

def main():
    # Initialize plotter
    plotter = WallPlotter()
    plotter.init()
    
    print("Wall Drawing Plotter - CSV File Reader")
    print("Starting drawing process...")
    
    # Test drawing pattern - you can modify these coordinates freely
    # Default: 100mm x 100mm square pattern (useful for calibration)
    test_drawing = [
        (50.0, 0.0), (50.0, 50.0), (0.0, 50.0), (-50.0, 50.0),
        (-50.0, 0.0), (-50.0, -50.0), (0.0, -50.0), (50.0, -50.0),
        (50.0, 0.0),(0.0,0.0)
    ]
    
    # Check if points.csv exists
    try:
        os.stat("points.csv")
        file_exists = True
        print("points.csv found. Starting drawing process.")
    except:
        file_exists = False
        print("points.csv not found. Drawing test square for calibration.")
    
    # Start drawing
    print("Starting to draw")
    # First make sure pen is up
    plotter.pen_up()
    time.sleep(1)
    
    if file_exists:
        # Process the CSV file
        success = plotter.read_csv_and_plot("points.csv")
    else:
        # Draw the test drawing
        print("Drawing test pattern...")
        # Move to first point with pen up
        plotter.pen_up()
        time.sleep(0.5)
        plotter.goto(test_drawing[0][0], test_drawing[0][1])
        
        # Draw the pattern
        plotter.pen_down()
        time.sleep(0.5)
        for x, y in test_drawing[1:]:
            plotter.goto(x, y)
        
        success = True
    
    if success:
        print("Drawing completed successfully!")
    else:
        print("Error occurred during drawing.")
    
    # Return pen to up position when done
    plotter.pen_up()
    print("Program execution complete")

if __name__ == "__main__":
    main() 