import math
import time
from stepper import SimpleStepper
from servo import SimpleServo
from config import *

class WallPlotter:
    """Wall drawing plotter implementation"""
    
    def __init__(self):
        # Initialize stepper motors
        self.m1 = SimpleStepper()
        self.m2 = SimpleStepper()
        
        # Initialize servo
        self.pen = SimpleServo(SERVO_PIN)
        
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
        self.m2.set_speed_in_steps_per_second(STEPS_PER_SEC)
        
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
        """Move to the specified target position with coordinated stepping."""
        print(f"\n--- Coordinated moveto: ({self.current_position[X_AXIS]}, {self.current_position[Y_AXIS]}) -> ({target_X}, {target_Y})")

        # Convert XY to motor steps
        target_steps_m1, target_steps_m2 = self.ik(target_X, target_Y)

        # Compute deltas
        delta_m1 = target_steps_m1 - self.current_steps_M1
        delta_m2 = target_steps_m2 - self.current_steps_M2

        # Determine directions
        dir1 = 1 if delta_m1 * INVERT_M1_DIR >= 0 else -1  
        dir2 = 1 if delta_m2 * INVERT_M2_DIR >= 0 else -1

        # Absolute steps to move
        abs_m1 = abs(delta_m1)
        abs_m2 = abs(delta_m2)

        print(f"Steps needed: M1={abs_m1} (dir {dir1}), M2={abs_m2} (dir {dir2})")

        # Use Bresenham line stepping
        steps_major = max(abs_m1, abs_m2)
        steps_minor = min(abs_m1, abs_m2)

        major_motor = self.m1 if abs_m1 >= abs_m2 else self.m2
        minor_motor = self.m2 if major_motor == self.m1 else self.m1

        dir_major = dir1 if major_motor == self.m1 else dir2
        dir_minor = dir2 if major_motor == self.m1 else dir1

        error = 0

        # Delay per step pair
        delay = 1 / self.m1.steps_per_second

        for i in range(steps_major):
            major_motor.step(dir_major)
            error += steps_minor
            if error >= steps_major:
                minor_motor.step(dir_minor)
                error -= steps_major
            time.sleep(delay)

        # Update positions
        self.current_steps_M1 = target_steps_m1
        self.current_steps_M2 = target_steps_m2
        self.current_position[X_AXIS] = target_X
        self.current_position[Y_AXIS] = target_Y

        print(f"--- Move complete: M1={self.current_steps_M1}, M2={self.current_steps_M2}, Pos=({self.current_position[X_AXIS]}, {self.current_position[Y_AXIS]})")
    
    def read_csv_and_plot(self, filename="points.csv"):
        """Read coordinates from CSV file and control the plotter to draw them"""
        print(f"Opening file: {filename}")
        try:
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
                            if first_point:
                                self.pen_up()
                                time.sleep(0.5)
                                self.moveto(x, y)
                                self.pen_down()
                                time.sleep(0.5)
                                first_point = False
                            else:
                                self.moveto(x, y)
                        except ValueError as e:
                            print(f"Error parsing point {point_str}: {e}")
                    self.pen_up()
                    time.sleep(0.5)
            print("Drawing complete")
            print("Returning to home position (0,0)")
            self.moveto(100,0)
            print("Returned to home position")
            return True
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
    