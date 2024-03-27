import serial
from syringe_controller import SyringeController
from virtual_serial_monitor import VirtualPort

port = VirtualPort()
#port = serial.Serial(s_name) # creates an empty port, should usually have a string as argument
controller = SyringeController(port) # create a syringe controller and tell it what connection/port to work with

controller.AddSyringe() # adds a syringe for the controller to work with, should give a msg
controller.AddSyringe() # adds a syringe for the controller to work with, should give a msg

# example testing set phase
syringe = controller.Get(0)
response = syringe.set_phase(1)
print(f"set_phase response:{response}")
print()

# test sending a pumping instruction
rate = 5.0 # mL implied by units
units = "MM" # mL/min
volume = 10.0 # mL implied by units
syringe = controller.Get(0)
response = syringe.create_pumping_phase(rate, units, volume)
print(f"create_pumping_phase  response:{response}")



