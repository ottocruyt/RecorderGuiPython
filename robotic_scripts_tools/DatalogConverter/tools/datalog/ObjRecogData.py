from ...main.defines import Position3d, ObjRecogObj


class ObjRecogData:
    def __init__(self, recording_time: int = None,
                 ref_pos: Position3d = None,
                 expecting_object: int = None,
                 expected_object: ObjRecogObj = None,
                 object_num: int = None,
                 object_file_num: int = None):
        self.recording_time = recording_time
        self.ref_pos = ref_pos
        self.expecting_object = expecting_object
        self.expected_object = expected_object
        self.object_num = object_num
        self.object_file_num = object_file_num

    def readAscii(self, f):
        line = f.readline()
        if (line == None or len(line) <= 1):
            return False
        self.recording_time, line = line.split(" ", 1)
        self.ref_pos = Position3d.Position3d()
        line = self.ref_pos.parseAscii(line)
        self.expecting_object, line = line.split(" ", 1)
        self.expected_object = ObjRecogObj.ObjRecogObj()
        line = self.expected_object.parseAscii(line)
        try:
            self.object_num, self.object_file_num, text = line.split()
        except:
            self.object_num, self.object_file_num = line.split()
            line = ""
        return True

    def writeAscii(self, f):
        f.write("%d ", self.recording_time)
        self.ref_pos.writeAscii(f)
        f.write(" %d " % self.expecting_object)
        self.expected_object.writeAscii(f)
        f.write(" %d %d\n" % (self.object_num, self.object_file_num))

    def castData(self):
        self.recording_time = int(self.recording_time)
        self.ref_pos.castData()
        self.expecting_object = int(self.expecting_object)
        self.expected_object.castData()
        self.object_num = int(self.object_num)
        self.object_file_num = int(self.object_file_num)
