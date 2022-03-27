class FileTool:
    # store all open files here to close in error case
    open_files = []

    def __init__(self):
        self.open_files = []

    # use this functions to open and close files - thus we can remember which files are open
    def openFile(self, f, args):
        file = open(f, args)
        self.open_files.append(file)
        # print("opened %s, %d open" % (str(f), len(self.open_files)))
        return file

    def closeFile(self, f):
        f.close()
        self.open_files.remove(f)
        # print("closed %s, %d open" % (str(f), len(self.open_files)))

    def closeAllFiles(self):
        success = True
        # print("closing %d files" % len(self.open_files))
        # make a copy to safely iterate -- open_files will be modified due to removal of elements
        files = self.open_files.copy()
        for f in files:
            try:
                self.closeFile(f)
            except:
                success = False
        return success