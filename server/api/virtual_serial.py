import os, pty, serial

STX = b'\x02'
ETX = b'\x03'

class VirtualPort:
    def __init__(self, monitor=True, autoreply=False):
        self.monitor = monitor
        self.autoreply = autoreply
        # create a virtual serial port
        self.master, self.slave = pty.openpty()
        self.s_name = os.ttyname(self.slave)
        print(f"Created virtual serial port: {self.s_name}")
        self.syringe_serial = serial.Serial(self.s_name)

    def write(self, data):
        r = os.write(self.master, data)
        if self.monitor:
            print(f"w: {data}")
        if self.autoreply: # act as syringe status reply
            self.syringe_reply("A")
        return r

    def read(self, size):
        r = os.read(self.master, size)
        if self.monitor:
            print(f"r: {r}")
        return r

    def syringe_reply(self, data):
        data = STX+data.encode()+ETX
        self.syringe_serial.write(data)
    
    