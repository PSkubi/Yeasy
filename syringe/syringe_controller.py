"""Syringe controller class."""
from syringe import Syringe

class SyringeController:
    def __init__(self, conn):
        self.conn = conn
        self.syringes = []
        return

    def AddSyringe(self):
        new_address = len(self.syringes)
        new_syringe = Syringe(self.conn, new_address)
        self.syringes.append(new_syringe)
        print(f"Added syringe with address {new_address}.")
        return
    
    def GetAll(self):
        return self.syringes

    def Get(self, address):
        syringe = self.syringes[address]
        return syringe
    
    def AddPhase(self, address, phase):
        syringe = self.Get(address)
        return
    