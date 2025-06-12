from machine import Pin
import time
import math
from config import *

class Stepper:
    
    # Full step sequence for 28BYJ-48
    STEP_SEQUENCE = [
        [1, 1, 0, 0],  # A+B
        [0, 1, 1, 0],  # B+C
        [0, 0, 1, 1],  # C+D
        [1, 0, 0, 1],  # D+A
]
    
    def __init__(self):
        self.pins = [None, None, None, None]
        self.position = 0
        self.current_step = 0
        self.steps_per_second = 1000
        self.acceleration = 10000
        
    def connect_to_pins(self, pin1, pin2, pin3, pin4):
        """Connect the stepper to the specified pins"""
        self.pins[0] = Pin(pin1, Pin.OUT)
        self.pins[1] = Pin(pin2, Pin.OUT)
        self.pins[2] = Pin(pin3, Pin.OUT)
        self.pins[3] = Pin(pin4, Pin.OUT)
        
        # Initialize pins to 0
        for pin in self.pins:
            pin.value(0)
            
    def set_speed_in_steps_per_second(self, steps_per_second):
        """Set the stepper speed in steps per second"""
        self.steps_per_second = steps_per_second
        
    def set_acceleration_in_steps_per_second_per_second(self, acceleration):
        """Set the stepper acceleration"""
        self.acceleration = acceleration
        
    def step(self, direction):
        """Move one step in the specified direction (1 or -1)"""
        # Update current step based on direction
        self.current_step = (self.current_step + direction) % 4
        
        # Set pins according to sequence
        for i in range(4):
            self.pins[i].value(self.STEP_SEQUENCE[self.current_step][i])
        
        # Update position
        self.position += direction
        
        # Delay to maintain speed (simplified - no acceleration)
        time.sleep(1 / self.steps_per_second)
        
    def move_relative_in_steps(self, steps):
        """Move relative number of steps (can be positive or negative)"""
        direction = 1 if steps > 0 else -1
        steps = abs(steps)
        
        for _ in range(steps):
            self.step(direction)
            
    def get_position(self):
        """Return the current position in steps"""
        return self.position 
    
    def disable_motor(self):
        for pin in self.pins:
            pin.value(0)
    