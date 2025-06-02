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
SERVO_PIN = 14

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
INVERT_M1_DIR = -1
INVERT_M2_DIR = 1  
STEPS_PER_TURN = 2048  # 28BYJ-48 stepper motor (with gear reduction)
SPOOL_DIAMETER = 28    # mm
SPOOL_CIRC = SPOOL_DIAMETER * 3.1416  # Line spool circumference
DEFAULT_XY_MM_PER_STEP = SPOOL_CIRC / STEPS_PER_TURN  # Min step resolution

# Motor speeds
STEPS_PER_SEC = 600
ACCELERATION = 10000

# Movement parameters
LINE_DELAY = 1           # Microseconds between steps
MM_PER_ARC_SEGMENT = 1   # Arc segment length
N_ARC_CORRECTION = 25    # Correction frequency for arcs

# Axes definitions
X_AXIS = 0
Y_AXIS = 1
Z_AXIS = 2
XY = 2
XYZ = 3

# Mathematical constants
import math
M_PI = math.pi
RADIANS = lambda d: (d * M_PI / 180.0)
ATAN2 = math.atan2
SQRT = math.sqrt
HYPOT2 = lambda x, y: (x**2 + y**2)
HYPOT = lambda x, y: SQRT(HYPOT2(x, y))

# Jog size for manual control
JOG_SIZE = 100

# Serial communication
BAUDRATE = 115200 