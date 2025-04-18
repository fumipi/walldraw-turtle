# CSV-based plotter for wall drawing machine
import time
from plotter import WallPlotter
from config import *

def read_csv_and_plot(plotter, filename="points.csv", target_width=100, target_height=100):
    """Read coordinates from CSV file and control the plotter to draw them"""
    print(f"Opening file: {filename}")
    
    try:
        # First pass: determine bounds of input data
        min_x, max_x, min_y, max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
        
        with open(filename, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                
                points_str = line.split(';')
                for point_str in points_str:
                    try:
                        x_str, y_str = point_str.split(',')
                        x = float(x_str)
                        y = float(y_str)
                        
                        min_x = min(min_x, x)
                        max_x = max(max_x, x)
                        min_y = min(min_y, y)
                        max_y = max(max_y, y)
                    except ValueError:
                        pass  # Skip invalid points in first pass
        
        if min_x == float('inf') or max_x == float('-inf') or min_y == float('inf') or max_y == float('-inf'):
            print("No valid points found in file")
            return False
            
        # Calculate scaling factors
        input_width = max_x - min_x
        input_height = max_y - min_y
        
        # Use the more restrictive scaling factor to maintain aspect ratio
        scale_factor = min(target_width / input_width, target_height / input_height)
        
        input_center_x = (min_x + max_x) / 2
        input_center_y = (min_y + max_y) / 2
        
        print(f"Input bounds: X: {min_x} to {max_x}, Y: {min_y} to {max_y}")
        print(f"Scaling factor: {scale_factor}")
        
        # Second pass: read and plot with proper scaling
        with open(filename, "r") as file:
            for line_num, line in enumerate(file):
                line = line.strip()
                if not line:
                    continue
                
                print(f"Processing line {line_num+1}")
                points_str = line.split(';')
                first_point = True
                
                for point_str in points_str:
                    try:
                        x_str, y_str = point_str.split(',')
                        x = float(x_str)
                        y = float(y_str)
                        
                        # Transform coordinates:
                        # 1. Shift relative to input center
                        # 2. Scale to fit within target dimensions
                        # 3. Result is centered at (0,0)
                        x = (x - input_center_x) * scale_factor
                        y = (y - input_center_y) * scale_factor
                        
                        if first_point:
                            # For the first point, move with pen up
                            plotter.pen_up()
                            time.sleep(0.5)  # Allow time for pen to move up
                            plotter.moveto(x, y)
                            plotter.pen_down()
                            time.sleep(0.5)  # Allow time for pen to move down
                            first_point = False
                        else:
                            # For subsequent points, draw lines
                            plotter.moveto(x, y)
                    except ValueError as e:
                        print(f"Error parsing point {point_str}: {e}")
                
                # Lift pen at the end of each path
                plotter.pen_up()
                time.sleep(0.5)
                
        print("Drawing complete")
        
        # Return to home position (0,0) after drawing is complete
        print("Returning to home position (0,0)")
        plotter.moveto(0, 0)
        print("Returned to home position")
        
        return True
        
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
