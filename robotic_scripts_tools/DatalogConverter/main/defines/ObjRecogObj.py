from ..defines import Position3d, Dimension3d, ImageArea


class ObjRecogObj:
    def __init__(self, object_id: int = None, \
                 pos: Position3d = None, \
                 vel: Position3d = None, \
                 dim: Dimension3d = None, \
                 prob: float = None, \
                 image_area: ImageArea = None, \
                 object_type: int = None, \
                 last_recog_time: int = None):
        self.object_id = object_id
        self.pos = pos
        self.vel = vel
        self.prob = prob
        self.image_area = image_area
        self.object_type = object_type
        self.last_recog_time = last_recog_time
        self.dim = dim

    def readAscii(self, f):
        line = f.readline()
        line = line.strip()
        if (line == None or len(line) <= 1):
            return False
        self.object_id, line = line.split(" ", 1)
        self.pos = Position3d.Position3d()
        line = self.pos.parseAscii(line)
        self.vel = Position3d.Position3d()
        line = self.vel.parseAscii(line)
        self.dim = Dimension3d.Dimension3d()
        line = self.dim.parseAscii(line)
        self.prob, line = line.split(" ", 1)
        self.image_area = ImageArea.ImageArea()
        line = self.image_area.parseAscii(line)
        try:
            self.object_type, self.last_recog_time, line = line.split(" ", 2)
        except:
            self.object_type, self.last_recog_time = line.split(" ", 2)
        return True

    def parseAscii(self, text):
        self.object_id, text = text.split(" ", 1)
        self.pos = Position3d.Position3d()
        text = self.pos.parseAscii(text)
        self.vel = Position3d.Position3d()
        text = self.vel.parseAscii(text)
        self.dim = Dimension3d.Dimension3d()
        text = self.dim.parseAscii(text)
        self.prob, text = text.split(" ", 1)
        self.image_area = ImageArea.ImageArea()
        text = self.image_area.parseAscii(text)
        try:
            self.object_type, self.last_recog_time, text = text.split(" ", 2)
        except:
            self.object_type, self.last_recog_time = text.split(" ", 2)
            text = ""
        return text

    def writeAscii(self, f):
        f.write("%d ", self.object_id)
        self.pos.writeAscii(f)
        f.write(" ")
        self.vel.writeAscii(f)
        f.write(" ")
        self.dim.writeAscii(f)
        f.write(" %d " % self.prob)
        self.image_area.writeAscii(f)
        f.write(" %d %d" % (self.object_type, self.last_recog_time))

    def castData(self):
        self.object_id = int(self.object_id)
        self.pos.castData()
        self.vel.castData()
        self.prob = float(self.prob)
        self.image_area.castData()
        self.object_type = int(self.object_type)
        self.last_recog_time = int(self.last_recog_time)
        self.dim.castData()
