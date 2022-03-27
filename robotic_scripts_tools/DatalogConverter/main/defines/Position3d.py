from struct import unpack


class Position3d:
    def __init__(self, x: int = None, y: int = None, z: int = None, phi: float = None, psi: float = None,
                 rho: float = None):
        self.x = x
        self.y = y
        self.z = z
        self.phi = phi
        self.psi = psi
        self.rho = rho

    def readBinary(self, f):
        self.x, self.y, self.z, \
        self.phi, self.psi, self.rho = unpack("iiifff", f.read(24))

    def parseAscii(self, text):
        if (text == None or len(text) <= 1):
            return None
        try:
            self.x, self.y, self.z, self.phi, self.psi, self.rho, text = text.split(" ", 6)
        except:
            self.x, self.y, self.z, self.phi, self.psi, self.rho = text.split(" ", 6)
            text = ""
        return text

    def writeAscii(self, f):
        f.write("%d %d %d %f %f %f" % (self.x, self.y, self.z, self.phi, self.psi, self.rho))

    def castData(self):
        self.x = int(self.x)
        self.y = int(self.y)
        self.z = int(self.z)
        self.phi = float(self.phi)
        self.psi = float(self.psi)
        self.rho = float(self.rho)
