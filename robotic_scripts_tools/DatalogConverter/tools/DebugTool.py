class DebugTool:
    def __init__(self, verbose=True):
        self.verbose = verbose

    def printDebug(self, txt):
        if (self.verbose):
            print(txt)
