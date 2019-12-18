class Extraction():
    def __init__(self):
        # Extraction Layer
        self.Primativelist = []
        self.Dronenumberlist = []
        self.targetpositionlist = []
        self.Drone_posuav = []
        self.Drone_posugv = []

        return None

    def Primative(self, action, ps):
        self.Primativelist.append(action)
        ps.set_action(action)

    def targetpostion(self, x, y, ps):
        self.targetpositionlist.append([x, y])
