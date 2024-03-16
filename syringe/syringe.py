"""Control syringe through PySerial."""

import serial

CR = b'\x0D'
STX = b'\x02'
ETX = b'\x03'

class Syringe:
    def __init__(self, conn, address):
        self.conn = conn
        self.address = address

        self.status = ""
        self.history = []
        self.phase_count = 0
        return
    
    def _check_float(self, f):
        """Validate floating point number. 
        Maximum of 4 digits plus 1 decimal point.
        Maximum of 3 digits to the right of the decimal point."""
        try:
            f = float(f)
        except ValueError:
            return None
        
        if f < 0:
            return None
        
        # TODO length and rounding checks
        return f
    
    def send_command(self, command, *parameters, mode="basic"):
        parameters = [str(p) for p in parameters] # convert all parameters to strings with list comprehension (adds new list in place of old list)
        command_string = f"{self.address}{command}{''.join(parameters)}" # format string joins address and command data together
        command_data = command_string.encode('utf-8') + CR # encodes into bytes and adds carriage return
        self.conn.write(command_data) # sends command to syringe

        # receives syringes response
        buffer = b''
        while not buffer.endswith(ETX): # keep listening until you receive ETX byte
            response_byte = self.conn.read(1)
            buffer += response_byte
        
        response = buffer.split(STX)[-1].split(ETX)[0]
        return response
    
    def run(self, phase_number=1):
        response = self.send_command("RUN", phase_number)
        return response

    def stop(self):
        # TODO implement clear and check status before sending STP
        response = self.send_command("STP")
        return response

    def clear(self):
        # send stop twice to pause and then clear
        self.send_command("STP")
        response = self.send_command("STP")
        self.phase_count = 0
        return response

    def get_diameter(self):
        response = self.send_command("DIA")
        return response

    def get_rate(self):
        response = self.send_command("RAT")
        return response

    def set_diameter(self, diameter: float):
        diameter = self._check_float(diameter)
        if diameter is None:
            return # TODO add an error statement

        response = self.send_command("DIA", diameter)
        return response

    def set_volume(self, volume: float):
        volume = self._check_float(volume)
        if volume is None:
            return # TODO add an error statement

        response = self.send_command("VOL", volume)
        return response
    
    def set_direction(self, direction: str):
        valid_directions= ["INF", "WDR"] # infuse, withdraw
        if direction not in valid_directions:
            return # TODO add an error statement 

        response = self.send_command("DIR", direction)
        return response

    def set_rate(self, rate: float, units: str):
        valid_units = ["UM", "MM", "UH", "MH"] # µL/min, mL/min, µL/hr, mL/hr
        if units not in valid_units:
            return # TODO add an error statement 
        
        rate = self._check_float(rate)
        if rate is None:
            return # TODO add an error statement
        
        response = self.send_command("RAT", rate, units)
        return response

    def set_phase(self, phase_number: int):
        response = self.send_command("PHN", phase_number)
        return response

    def set_dir(self, direction):
        response = self.send_command("DIR", direction)
        return response

    def create_pumping_phase(self, rate, units, vol, dir="INF", phase_number=-1):
        if phase_number == -1:
            # just do next phase
            phase_number = self.phase_count+1

        self.set_phase(phase_number)        
        self.set_rate(rate, units)
        self.set_volume(vol) # volume units are determined by rate units
        self.set_dir(dir)

        self.phase_count += 1
        return
