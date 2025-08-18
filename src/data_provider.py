class DataProvider:
    def __init__(self):
        # Hier später ODrive oder andere Quellen anbinden
        self.angle = 0

    def get_angle(self):
        # Dummy: Zähler hochzählen
        self.angle += 1
        if self.angle > 360:
            self.angle = 0
        return self.angle
