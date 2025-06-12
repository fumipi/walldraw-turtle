import math
import time
from stepper import Stepper
from servo import Servo
from config import *

class WallPlotter:
    """Wall drawing plotter implementation"""
    
    def __init__(self):
        # Initialize stepper motors
        self.m1 = Stepper()
        self.m2 = Stepper()
        
        # Initialize servo
        self.pen = Servo(SERVO_PIN)
        
        # Initialize position tracking
        self.current_position = [START_X, START_Y, 0]
        self.destination = [START_X, START_Y, 0]
        self.current_steps_M1 = 0
        self.current_steps_M2 = 0
        
    def init(self):
        """Initialize hardware"""
        # Calculate initial steps
        target_steps_m1, target_steps_m2 = self.ik(START_X, START_Y)
        self.current_steps_M1 = target_steps_m1
        self.current_steps_M2 = target_steps_m2
        
        # Connect to stepper pins
        self.m1.connect_to_pins(M1_PIN1, M1_PIN2, M1_PIN3, M1_PIN4)
        self.m2.connect_to_pins(M2_PIN1, M2_PIN2, M2_PIN3, M2_PIN4)
        
        # Set stepper parameters
        self.m1.set_speed_in_steps_per_second(STEPS_PER_SEC)
        self.m1.set_acceleration_in_steps_per_second_per_second(ACCELERATION)
        self.m2.set_speed_in_steps_per_second(STEPS_PER_SEC)
        self.m2.set_acceleration_in_steps_per_second_per_second(ACCELERATION)
        
        # Initialize pen position
        self.pen.write(PEN_UP_ANGLE)

    def calc_direction(diff, invert):
        """
        Given a step difference and an inversion factor,
        return a direction value that is properly corrected.
        """
        if diff == 0:
            return 0
        return int(math.copysign(1, diff)) * invert
        
    def ik(self, x, y):
        """Calculate inverse kinematics (convert XY to motor steps)"""
        dy = y - Y_MIN_POS
        dx = x - X_MIN_POS
        target_steps_m1 = round(math.sqrt(dx*dx + dy*dy) / DEFAULT_XY_MM_PER_STEP)
        
        dx = x - X_MAX_POS
        target_steps_m2 = round(math.sqrt(dx*dx + dy*dy) / DEFAULT_XY_MM_PER_STEP)
        
        return target_steps_m1, target_steps_m2
    
    def pen_up(self):
        """Move the pen up"""
        self.pen.write(PEN_UP_ANGLE)
        print("Pen up")
    
    def pen_down(self):
        """Move the pen down"""
        self.pen.write(PEN_DOWN_ANGLE)
        print("Pen down")
    
    def jog_m1(self, steps):
        """Jog motor M1 by the specified number of steps"""
        self.m1.move_relative_in_steps(steps * INVERT_M1_DIR)
    
    def jog_m2(self, steps):
        """Jog motor M2 by the specified number of steps"""
        self.m2.move_relative_in_steps(steps * INVERT_M2_DIR)
    
    def moveto(self, target_X, target_Y):
        """Move to the specified target position"""
        print(f"Moving from ({self.current_position[X_AXIS]}, {self.current_position[Y_AXIS]}) to ({target_X}, {target_Y})")
        
        target_steps_m1, target_steps_m2 = self.ik(target_X, target_Y)
        
        print(f"Current steps - M1: {self.current_steps_M1}, M2: {self.current_steps_M2}")
        print(f"Target steps - M1: {target_steps_m1}, M2: {target_steps_m2}")
        
        steps_diff_m1 = target_steps_m1 - self.current_steps_M1
        steps_diff_m2 = target_steps_m2 - self.current_steps_M2
        
        print(f"Step differences - M1: {steps_diff_m1}, M2: {steps_diff_m2}")
        
        dir1 = -1 if steps_diff_m1 * INVERT_M1_DIR > 0 else 1
        dir2 = -1 if steps_diff_m2 * INVERT_M2_DIR > 0 else 1
    
        print(f"Direction calculations - M1: {dir1}, M2: {dir2}")
        
        over = 0

        dif_abs_steps_run_m1 = abs(target_steps_m1 - self.current_steps_M1)
        dif_abs_steps_run_m2 = abs(target_steps_m2 - self.current_steps_M2)
        
        # Bresenham line algorithm for coordinated movement
        if dif_abs_steps_run_m1 > dif_abs_steps_run_m2:
            print(f"More steps on M1: {dif_abs_steps_run_m1} vs {dif_abs_steps_run_m2}")
            for i in range(dif_abs_steps_run_m1):
                self.m1.move_relative_in_steps(dir1)
                over += dif_abs_steps_run_m2
                if over >= dif_abs_steps_run_m1:
                    over -= dif_abs_steps_run_m1
                    self.m2.move_relative_in_steps(dir2)
        else:
            print(f"More steps on M2: {dif_abs_steps_run_m2} vs {dif_abs_steps_run_m1}")
            for i in range(dif_abs_steps_run_m2):
                self.m2.move_relative_in_steps(dir2)
                over += dif_abs_steps_run_m1
                if over >= dif_abs_steps_run_m2:
                    over -= dif_abs_steps_run_m2
                    self.m1.move_relative_in_steps(dir1)
        
        # Update position trackers
        self.current_steps_M1 = target_steps_m1
        self.current_steps_M2 = target_steps_m2
        self.current_position[X_AXIS] = target_X
        self.current_position[Y_AXIS] = target_Y
        
        print(f"Move completed - now at ({self.current_position[X_AXIS]}, {self.current_position[Y_AXIS]})")
        print(f"Updated steps - M1: {self.current_steps_M1}, M2: {self.current_steps_M2}")
    
    def read_csv_and_plot(self, filename="points.csv", target_width=100, target_height=100):
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
            
            # Scaling factor to maintain aspect ratio
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
                                self.pen_up()
                                time.sleep(0.5)  # Allow time for pen to move up
                                self.moveto(x, y)
                                self.pen_down()
                                time.sleep(0.5)  # Allow time for pen to move down
                                first_point = False
                            else:
                                # For subsequent points, draw lines
                                self.moveto(x, y)
                        except ValueError as e:
                            print(f"Error parsing point {point_str}: {e}")
                    
                    # Lift pen at the end of each path
                    self.pen_up()
                    time.sleep(0.5)
                    
            print("Drawing complete")
            
            # Return to home position (0,0) after drawing is complete
            print("Returning to home position (0,0)")
            self.moveto(0, 0)
            print("Returned to home position")
            
            return True
            
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
    