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
    
    # Initialize buttons with PULL_UP since buttons are wired to connect to GND
    pen_up_btn = Pin(PEN_UP_BUTTON, Pin.IN, Pin.PULL_UP)
    pen_down_btn = Pin(PEN_DOWN_BUTTON, Pin.IN, Pin.PULL_UP)
    m1_up_btn = Pin(M1_UP_BUTTON, Pin.IN, Pin.PULL_UP)
    m1_down_btn = Pin(M1_DOWN_BUTTON, Pin.IN, Pin.PULL_UP)
    m2_up_btn = Pin(M2_UP_BUTTON, Pin.IN, Pin.PULL_UP)
    m2_down_btn = Pin(M2_DOWN_BUTTON, Pin.IN, Pin.PULL_UP)
    start_btn = Pin(START_BUTTON, Pin.IN, Pin.PULL_UP)
    
    print("Wall Drawing Plotter - CSV File Reader")
    print("CALIBRATION MODE: Use buttons to adjust position.")
    
    # Check if points.csv exists
    try:
        os.stat("points.csv")
        file_exists = True
        print("points.csv found. Press START button to begin drawing.")
    except:
        file_exists = False
        print("WARNING: points.csv not found! Drawing will not be possible.")
    
    time.sleep(1)
    
    # Initialize last button states by reading current values
    last_button_states = {
        "pen_up": pen_up_btn.value(),
        "pen_down": pen_down_btn.value(),
        "m1_up": m1_up_btn.value(),
        "m1_down": m1_down_btn.value(),
        "m2_up": m2_up_btn.value(),
        "m2_down": m2_down_btn.value(),
        "start": start_btn.value()
    }
    
    print("Entering calibration loop. Press buttons to test...")
    
    # Wait for start button with calibration options available
    debug_counter = 0
    while True:
        # Occasionally print button states for debugging
        debug_counter += 1
        if debug_counter > 50:  # Print every ~5 seconds
            print(f"Button states: PU:{pen_up_btn.value()} PD:{pen_down_btn.value()} " +
                  f"M1U:{m1_up_btn.value()} M1D:{m1_down_btn.value()} " +
                  f"M2U:{m2_up_btn.value()} M2D:{m2_down_btn.value()} " +
                  f"ST:{start_btn.value()}")
            debug_counter = 0
        
        # Check start button with debouncing - looking for 0 (pressed) 
        current_start = start_btn.value()
        if current_start == 0 and last_button_states["start"] == 1:
            if file_exists:
                print("START button pressed - Beginning drawing from points.csv")
                time.sleep(0.5)  # Small delay to ensure button release
                break  # Exit calibration mode
            else:
                print("No points.csv file available to draw")
        last_button_states["start"] = current_start
        
        # Manual control options - looking for 0 (pressed) 
        current_pen_up = pen_up_btn.value()
        if current_pen_up == 0 and last_button_states["pen_up"] == 1:
            print("Pen up button pressed")
            plotter.pen_up()
        last_button_states["pen_up"] = current_pen_up
        
        current_pen_down = pen_down_btn.value()
        if current_pen_down == 0 and last_button_states["pen_down"] == 1:
            print("Pen down button pressed")
            plotter.pen_down()
        last_button_states["pen_down"] = current_pen_down
        
        current_m1_up = m1_up_btn.value()
        if current_m1_up == 0 and last_button_states["m1_up"] == 1:
            print("M1 up button pressed")
            try:
                print(f"Jogging M1 by +{JOG_SIZE} steps")
                plotter.jog_m1(JOG_SIZE)
                print("M1 jog completed")
            except Exception as e:
                print(f"Error jogging M1: {e}")
        last_button_states["m1_up"] = current_m1_up
        
        current_m1_down = m1_down_btn.value()
        if current_m1_down == 0 and last_button_states["m1_down"] == 1:
            print("M1 down button pressed")
            try:
                print(f"Jogging M1 by -{JOG_SIZE} steps")
                plotter.jog_m1(-JOG_SIZE)
                print("M1 jog completed")
            except Exception as e:
                print(f"Error jogging M1: {e}")
        last_button_states["m1_down"] = current_m1_down
        
        current_m2_up = m2_up_btn.value()
        if current_m2_up == 0 and last_button_states["m2_up"] == 1:
            print("M2 up button pressed")
            try:
                print(f"Jogging M2 by +{JOG_SIZE} steps")
                plotter.jog_m2(JOG_SIZE)
                print("M2 jog completed")
            except Exception as e:
                print(f"Error jogging M2: {e}")
        last_button_states["m2_up"] = current_m2_up
        
        current_m2_down = m2_down_btn.value()
        if current_m2_down == 0 and last_button_states["m2_down"] == 1:
            print("M2 down button pressed")
            try:
                print(f"Jogging M2 by -{JOG_SIZE} steps")
                plotter.jog_m2(-JOG_SIZE)
                print("M2 jog completed")
            except Exception as e:
                print(f"Error jogging M2: {e}")
        last_button_states["m2_down"] = current_m2_down
        
        time.sleep(0.1)  # Small delay to prevent excessive CPU usage
    
    # Start drawing from CSV file if file exists
    if file_exists:
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