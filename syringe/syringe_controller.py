"""Syringe controller class."""

class SyringeController:
    def __init__(self):
        self.syringes = []
        return
    
    def GetAll(self):
        return self.syringes

    def Get(self, address):
        syringe = self.syringes[address]
        return syringe
    
    def AddPhase(self, address, phase):
        syringe = self.Get(address)
        syringe. 
        return
    