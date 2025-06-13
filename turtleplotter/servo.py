from machine import Pin, PWM
import time

class SimpleServo:
    """A simplified servo motor control library.
    This is a basic implementation that provides simple angle control (0-180 degrees)
    using PWM signals. It lacks advanced features like speed control, position feedback,
    and calibration support that are common in more comprehensive servo libraries.
    """
    
    def __init__(self, pin_num):
        """Initialize servo on the specified pin"""
        self.pwm = PWM(Pin(pin_num))
        self.pwm.freq(50)  # Standard 50Hz for servos
        self.min_duty = 1000  # Minimum duty cycle (0 degrees)
        self.max_duty = 9000  # Maximum duty cycle (180 degrees)
        self.current_angle = 0
        
    def attach(self, pin_num=None):
        """Attach the servo (or reattach to a new pin)"""
        if pin_num is not None:
            self.pwm = PWM(Pin(pin_num))
            self.pwm.freq(50)
        
    def detach(self):
        """Detach the servo"""
        self.pwm.deinit()
        
    def write(self, angle):
        """Set the servo to the specified angle (0-180 degrees)"""
        if angle < 0:
            angle = 0
        elif angle > 180:
            angle = 180
            
        # Convert angle to duty cycle
        duty = int(self.min_duty + (self.max_duty - self.min_duty) * angle / 180)
        self.pwm.duty_u16(duty)
        self.current_angle = angle
        
    def read(self):
        """Return the current angle"""
        return self.current_angle 