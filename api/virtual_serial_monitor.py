import serial, os, pty

class VirtualPort:
    def __init__(self, monitor=True):
        self.monitor = monitor
        # create a virtual serial port
        self.master, self.slave = pty.openpty()
        self.s_name = os.ttyname(self.slave)
        print(f"Created virtual serial port: {self.s_name}")

    def write(self, data):
        r = os.write(self.master, data)
        if self.monitor:
            print(f"w: {data}")
        return r

    def read(self, size):
        r = os.read(self.master, size)
        if self.monitor:
            print(f"r: {r}")
        return r


"""
print(f"Listening...")

while True:
    data = os.read(master, 1)
    print(data)
"""