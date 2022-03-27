class ImageArea:
    def __init__(self, x: int = None, y: int = None, width: int = None, height: int = None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def parseAscii(self, text):
        if (text == None or len(text) <= 1):
            return None
        try:
            self.x, self.y, self.width, self.height, text = text.split(" ", 4)
        except:
            self.x, self.y, self.width, self.height = text.split(" ", 4)
            text = ""
        return text

    def writeAscii(self, f):
        f.write("%d %d %d %d" % (self.x, self.y, self.width, self.height))

    def castData(self):
        self.x = int(self.x)
        self.y = int(self.y)
        self.width = int(self.width)
        self.height = int(self.height)
