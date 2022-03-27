class Dimension3d:
    def __init__(self, x: int = None, y: int = None, z: int = None):
        self.x = x
        self.y = y
        self.z = z

    def parseAscii(self, text):
        if (text == None or len(text) <= 1):
            return None
        try:
            self.x, self.y, self.z, text = text.split(" ", 3)
        except:
            self.x, self.y, self.z = text.split(" ", 3)
            text = ""
        return text

    def writeAscii(self, f):
        f.write("%d %d %d" % (self.x, self.y, self.z))

    def castData(self):
        self.x = int(self.x)
        self.y = int(self.y)
        self.z = int(self.z)
