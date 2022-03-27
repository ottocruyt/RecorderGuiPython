from struct import unpack


class BinarySubHeader:
    def __init__(self, magic=None, package_number=None):
        self.magic = magic
        self.package_number = package_number

    def read(self, f):
        magicword = f.read(4)
        buf = f.read(4)
        self.magic = magicword.decode('ASCII')
        self.package_number = unpack("i", buf)
