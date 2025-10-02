# Configuration for Wall Drawing Plotter

# Hardware pins
M1_PIN1 = 6
M1_PIN2 = 7
M1_PIN3 = 8
M1_PIN4 = 9
M2_PIN1 = 0
M2_PIN2 = 1
M2_PIN3 = 3
M2_PIN4 = 4
SERVO_PIN = 18

# Drawing area configuration
START_X = 0
START_Y = 0
X_SEPARATION = 250  # x cm apart motors
X_MAX_POS = X_SEPARATION * 0.5  
X_MIN_POS = -X_SEPARATION * 0.5  
Y_MAX_POS = -200 # Bottom of drawing area 
Y_MIN_POS = 200  # Top of drawing area 

# Pen servo configuration
PEN_UP_ANGLE = 110
PEN_DOWN_ANGLE = 50

# Motor configuration
INVERT_M1_DIR = 1  
INVERT_M2_DIR = -1
STEPS_PER_TURN = 2048  # 28BYJ-48 stepper motor (with gear reduction)
SPOOL_DIAMETER = 28    # mm
SPOOL_CIRC = SPOOL_DIAMETER * 3.1416  # Line spool circumference
DEFAULT_XY_MM_PER_STEP = SPOOL_CIRC / STEPS_PER_TURN  # Min step resolution

# Motor speeds
STEPS_PER_SEC = 600

# Axes definitions
X_AXIS = 0
Y_AXIS = 1 