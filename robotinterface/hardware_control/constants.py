#TODO: Rename all constants to be Uppercase
# holding pwm without overheating

# max pwm for fast acceleration but will lead to overheating
PWM_MAX = 400
PWM_SOFT = 150
PWM_RETAIN = 50


# DIAMETER_OPEN = 128
# DIAMETER_CLOSED = 32 
# DIAMETER_CLOSE_TO_PETRIDISH = 108

POSITION_OPEN = 3550
POSITION_CLOSED = 800
POSITION_CLOSE_TO_PD =  3000

CURRENT_VIRTUAL_ENDSTOP = 120

TIMEOUT_POSITION_REACHED = 3
TIMEOUT_OBJECT_REACHED = 2

# Ratio between dynamixel and degree
ratio = 4095 / 360

# feedrate robot
FEEDRATE = 15000

# clerance while moving
CLERANCE = 180

