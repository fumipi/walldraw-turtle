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
        
        # dir1 = -1 * INVERT_M1_DIR if steps_diff_m1 > 0 else INVERT_M1_DIR
        # dir2 = -1 * INVERT_M2_DIR if steps_diff_m2 > 0 else INVERT_M2_DIR

        # Alternative approach 意味は同じ
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
    
    def buffer_line_to_destination(self):
        """Draw a line to the destination coordinates"""
        # Handle Z axis (pen up/down)
        if self.destination[Z_AXIS] == 1:
            self.pen_down()
        elif self.destination[Z_AXIS] > 1:
            self.pen_up()
        
        # Calculate distance to move
        cartesian_mm = math.sqrt(
            (self.current_position[X_AXIS] - self.destination[X_AXIS])**2 +
            (self.current_position[Y_AXIS] - self.destination[Y_AXIS])**2
        )
        
        # If distance is very small, just do a direct move
        if cartesian_mm <= DEFAULT_XY_MM_PER_STEP:
            self.moveto(self.destination[X_AXIS], self.destination[Y_AXIS])
            return
        
        # Break long moves into smaller segments
        steps = math.floor(cartesian_mm / DEFAULT_XY_MM_PER_STEP)
        init_X = self.current_position[X_AXIS]
        init_Y = self.current_position[Y_AXIS]
        
        for s in range(steps + 1):
            scale = s / steps
            self.moveto(
                (self.destination[X_AXIS] - init_X) * scale + init_X,
                (self.destination[Y_AXIS] - init_Y) * scale + init_Y
            )
        
        # Ensure we reach the exact destination
        self.moveto(self.destination[X_AXIS], self.destination[Y_AXIS])
    
    def buffer_arc_to_destination(self, offset, clockwise):
        """Draw an arc to the destination coordinates"""
        r_P = -offset[0]
        r_Q = -offset[1]
        p_axis = X_AXIS
        q_axis = Y_AXIS
        
        radius = HYPOT(r_P, r_Q)
        center_P = self.current_position[p_axis] - r_P
        center_Q = self.current_position[q_axis] - r_Q
        rt_X = self.destination[p_axis] - center_P
        rt_Y = self.destination[q_axis] - center_Q
        
        angular_travel = ATAN2(r_P * rt_Y - r_Q * rt_X, r_P * rt_X + r_Q * rt_Y)
        print(angular_travel)
        
        if angular_travel < 0:
            angular_travel += RADIANS(360)
        if clockwise:
            angular_travel -= RADIANS(360)
        
        print(angular_travel)
        
        # Handle complete circles
        if (angular_travel == 0 and 
            self.current_position[p_axis] == self.destination[p_axis] and 
            self.current_position[q_axis] == self.destination[q_axis]):
            angular_travel = RADIANS(360)
        
        # Calculate arc length
        mm_of_travel = HYPOT(angular_travel * radius, 0)
        if mm_of_travel < 0.001:
            return
        
        print(mm_of_travel)
        
        # Divide arc into segments
        segments = math.floor(mm_of_travel / MM_PER_ARC_SEGMENT)
        if segments < 1:
            segments = 1
        
        theta_per_segment = angular_travel / segments
        sin_T = math.sin(theta_per_segment)
        cos_T = math.cos(theta_per_segment)
        
        arc_recalc_count = N_ARC_CORRECTION
        
        for i in range(1, segments):
            if arc_recalc_count == 0:
                arc_recalc_count = N_ARC_CORRECTION
                cos_Ti = math.cos(i * theta_per_segment)
                sin_Ti = math.sin(i * theta_per_segment)
                r_P = -offset[0] * cos_Ti + offset[1] * sin_Ti
                r_Q = -offset[0] * sin_Ti - offset[1] * cos_Ti
            else:
                r_new_Y = r_P * sin_T + r_Q * cos_T
                r_P = r_P * cos_T - r_Q * sin_T
                r_Q = r_new_Y
                arc_recalc_count -= 1
            
            # Calculate next point on arc
            X = center_P + r_P
            Y = center_Q + r_Q
            
            # Move to this point
            self.moveto(X, Y)
            
            print(f"G0 X{X} Y{Y}") 