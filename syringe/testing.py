import serial
from syringe_controller import SyringeController

port = serial.Serial() # creates an empty port, should usually have a string as argument
controller = SyringeController(port) # create a syringe controller and tell it what connection/port to work with

controller.AddSyringe() # adds a syringe for the controller to work with, should give a msg
controller.AddSyringe() # adds a syringe for the controller to work with, should give a msg
controller.AddSyringe() # adds a syringe for the controller to work with, should give a msg

syringes = controller.GetAll()
print("syringes:", syringes)