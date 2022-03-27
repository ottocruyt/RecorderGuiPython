from struct import unpack
from ...main.defines import Position3d, BoundingBox


class Scan3dData:
    def __init__(self, recording_time=None, duration=None, max_range=None, scan_num=None, scan_point_num=None,
                 scan_mode=None, scan_hardware=None, sector_num=None, sector_index=None, ref_pos=None,
                 bounding_box=None, point_num=None, compressed=None, dataset_num=None):
        self.recording_time = recording_time
        self.duration = duration
        self.max_range = max_range
        self.scan_num = scan_num
        self.scan_point_num = scan_point_num
        self.scan_mode = scan_mode
        self.scan_hardware = scan_hardware
        self.sector_num = sector_num
        self.sector_index = sector_index
        self.ref_pos = ref_pos
        self.bounding_box = bounding_box
        self.point_num = point_num
        self.compressed = compressed
        self.dataset_num = dataset_num

    def readBinary(self, f):
        self.recording_time, self.duration, self.max_range, self.scan_num, self.scan_point_num, self.scan_mode, \
        self.scan_hardware, self.sector_num, self.sector_index \
            = unpack("QQiiiiiii", f.read(44))
        self.ref_pos = Position3d.Position3d()
        self.ref_pos.readBinary(f)
        self.bounding_box = BoundingBox.BoundingBox()
        self.bounding_box.readBinary(f)
        self.point_num, self.compressed = unpack("ii", f.read(8))

    def parseAscii(self, text):
        if (text == None or len(text) <= 1):
            return None
        self.recording_time, self.duration, self.max_range, self.scan_num, self.scan_point_num, self.scan_mode, \
        self.scan_hardware, self.sector_num, self.sector_index, text = text.split(" ", 9)
        self.ref_pos = Position3d.Position3d()
        text = self.ref_pos.parseAscii(text)
        self.bounding_box = BoundingBox.BoundingBox()
        text = self.bounding_box.parseAscii(text)
        try:
            self.point_num, self.compressed, self.dataset_num, text = text.split(" ", 3)
        except:
            self.point_num, self.compressed, self.dataset_num = text.split(" ", 3)
            text = ""
        return text

    def writeAscii(self, f):
        f.write("%d %d %d %d %d %d %d %d %d " % (self.recording_time, self.duration, self.max_range, self.scan_num,
                self.scan_point_num, self.scan_mode, self.scan_hardware, self.sector_num, self.sector_index))
        self.ref_pos.writeAscii(f)
        f.write(" ")
        self.bounding_box.writeAscii(f)
        f.write(" %d %d %d\n" % (self.point_num, self.compressed, self.dataset_num))

    def writeAsciiHeader(self, f, instance):
        f.write("%% Scan3d(0/%d)\n" % instance)
        f.write("% recordingTime duration maxRange scanNum scanPointNum scanMode scanHardware sectorNum sectorIndex " +
                "refPos.x refPos.y refPos.z refPos.phi refPos.psi refPos.rho boundBox.x1 boundBox.x2 boundBox.y1 " +
                "boundBox.y2 boundBox.z1 boundBox.z2 boundBox.pos.x boundBox.pos.y boundBox.pos.z boundBox.pos.phi " +
                "boundBox.pos.psi boundBox.pos.rho  boundBox.posValid boundBox.on pointNum compressed scan3dFileNum\n")

    def castData(self):
        self.recording_time = int(self.recording_time)
        self.duration = int(self.duration)
        self.max_range = int(self.max_range)
        self.scan_num = int(self.scan_num)
        self.scan_point_num = int(self.scan_point_num)
        self.scan_mode = int(self.scan_mode)
        self.scan_hardware = int(self.scan_hardware)
        self.sector_num = int(self.sector_num)
        self.sector_index = int(self.sector_index)
        self.ref_pos.castData()
        self.bounding_box.castData()
        self.point_num = int(self.point_num)
        self.compressed = int(self.compressed)
        self.dataset_num = int(self.dataset_num)
