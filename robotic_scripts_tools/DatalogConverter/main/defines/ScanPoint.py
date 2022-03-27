from struct import unpack


class ScanPoint:
    def __init__(self, x=None, y=None, z=None, dist=None, type=None, segment=None, intensity=None):
        self.x = x
        self.y = y
        self.z = z
        self.dist = dist
        self.type = type
        self.segment = segment
        self.intensity = intensity

    def readBinary(self, f):
        self.x, self.y, self.z, self.dist, self.type, self.segment, self.intensity = \
            unpack("iiiIihh", f.read(24))

    def writeAscii(self, f):
        f.write("%d %d %d %d %d %d %d" % (self.x, self.y, self.z, self.dist, self.type, self.segment, self.intensity))