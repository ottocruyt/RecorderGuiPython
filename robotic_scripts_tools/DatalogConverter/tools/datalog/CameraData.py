class CameraData:
    def __init__(self, recording_time=None, width=None, height=None, depth=None, mode=None,
                 color_filter_id=None, camera_file_num=None):
        self.recording_time = recording_time
        self.width = width
        self.height = height
        self.depth = depth
        self.mode = mode
        self.color_filter_id = color_filter_id
        self.camera_file_num = camera_file_num

    def readAscii(self, f):
        line = f.readline()
        if (line == None or len(line) <= 1):
            return False
        try:
            self.recording_time, self.width, self.height, self.depth, self.mode, self.color_filter_id, self.camera_file_num, text = line.split()
        except:
            self.recording_time, self.width, self.height, self.depth, self.mode, self.color_filter_id, self.camera_file_num = line.split()
            line = ""
        return True

    def castData(self):
        self.recording_time = int(self.recording_time)
        self.width = int(self.width)
        self.height = int(self.height)
        self.depth = int(self.depth)
        self.mode = int(self.mode)
        self.color_filter_id = int(self.color_filter_id)
        self.camera_file_num = int(self.camera_file_num)