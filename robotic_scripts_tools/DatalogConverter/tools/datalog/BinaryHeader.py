from struct import unpack


class BinaryHeader:
    def __init__(self, magic=None, version=None, flags=None, module_id=None, dummy=None):
        self.magic = magic
        self.version = version
        self.flags = flags
        self.module_id = module_id
        self.dummy = dummy

    def read(self, f):
        magicword = f.read(4);
        buf = f.read(4);
        self.magic = magicword.decode('ASCII')
        (self.version, self.flags, self.module_id, self.dummy) = unpack("BBBB", buf);
