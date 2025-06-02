from machine import Pin
import time
import os
from config import *
from plotter import WallPlotter
from csv_plotter import read_csv_and_plot

def main():
    # Initialize plotter
    plotter = WallPlotter()
    plotter.init()
    
    print("Wall Drawing Plotter - CSV File Reader")
    print("Starting drawing process...")
    
    # Check if points.csv exists
    try:
        os.stat("points.csv")
        file_exists = True
        print("points.csv found. Starting drawing process.")
    except:
        file_exists = False
        print("WARNING: points.csv not found! Drawing will not be possible.")
        return
    
    # Start drawing from CSV file
    print("Starting to draw from points.csv")
    # First make sure pen is up
    plotter.pen_up()
    time.sleep(1)
    
    # Process the CSV file
    success = read_csv_and_plot(plotter)
    
    if success:
        print("Drawing completed successfully!")
    else:
        print("Error occurred during drawing.")
    
    # Return pen to up position when done
    plotter.pen_up()
    print("Program execution complete")

if __name__ == "__main__":
    main() 