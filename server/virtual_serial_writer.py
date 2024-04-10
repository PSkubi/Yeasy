import serial

n = input("/dev/ttys")
s_name = f"/dev/ttys{n}"

print(f"Connected to virtual serial port: {s_name}")

ser = serial.Serial(s_name)

STX = b'\x02'
ETX = b'\x03'

while True:
    data = input(">>>")#+"\n"
    data = STX+data.encode()+ETX
    print(data)
    ser.write(data)
    