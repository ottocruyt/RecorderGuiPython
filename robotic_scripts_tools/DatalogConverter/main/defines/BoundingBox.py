from struct import unpack
from . import Position3d


class BoundingBox:
    def __init__(self, x1=None, x2=None, y1=None, y2=None, z1=None, z2=None,
                 pos=None, pos_valid=None, on=None):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.z1 = z1
        self.z2 = z2
        self.pos = pos
        self.pos_valid = pos_valid
        self.on = on

    def readBinary(self, f):
        self.x1, self.x2, self.y1, self.y2, self.z1, self.z2 = unpack("iiiiii", f.read(24))
        self.pos = Position3d.Position3d()
        self.pos.readBinary(f)
        self.pos_valid, self.on = unpack("BB", f.read(2))

    def parseAscii(self, text):
        if (text == None or len(text) <= 1):
            return None
        self.x1, self.x2, self.y1, self.y2, self.z1, self.z2, text = text.split(" ", 6)
        self.pos = Position3d.Position3d()
        text = self.pos.parseAscii(text)
        try:
            self.pos_valid, self.on, text = text.split(" ", 2)
        except:
            self.pos_valid, self.on = text.split(" ", 2)
            text = ""
        return text

    def writeAscii(self, f):
        f.write("%d %d %d %d %d %d " % (self.x1, self.x2, self.y1, self.y2, self.z1, self.z2))
        self.pos.writeAscii(f)
        f.write(" %d %d" % (self.pos_valid, self.on))

    def castData(self):
        self.x1 = int(self.x1)
        self.x2 = int(self.x2)
        self.y1 = int(self.y1)
        self.y2 = int(self.y2)
        self.z1 = int(self.z1)
        self.z2 = int(self.z2)
        self.pos.castData()
