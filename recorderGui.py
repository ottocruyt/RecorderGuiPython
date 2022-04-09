# -*- coding: utf-8 -*-

import configparser
import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from pathlib import Path
from robotic_scripts_tools.DatalogConverter import Recog3dToVideo
#import ptvsd


PATH_ROLE = 32

class Config():
    import configparser
    dictionary = {}
    # default values:  
    dictionary['veh_xml_path'] = ""
    dictionary['rec_folder_path'] = ""


    config = configparser.ConfigParser()

    def __init__(self):
        self.importCfg()

    def importCfg(self):
        try:
            self.config.read("config.ini")
            self.dictionary['veh_xml_path'] = self.config.get("paths", "veh_xml_path")
            self.dictionary['rec_folder_path'] = self.config.get("paths", "rec_folder_path")
            print("\nConfig file loaded.")
        except configparser.NoSectionError as inst:
            print('Expected section missing in config: ' + str(inst))
        except Exception as inst:
            print('Oops...problem opening config file...')
            print(inst) 


    def writeCfg(self):
        try:
            f = open("config.ini", 'w')
            self.config.write(f)
        except Exception as inst:
            print('Oops...problem writing to config file...')
        finally:
            f.close()
    
    def set(self, section, setting, value):
        self.config.set(section, setting, value)
        self.writeCfg()

class Agv():
    ID = ''
    IP = ''
    def __init__(self, ID, IP):
        self.ID = ID
        self.IP = IP

class Recording():
    fileName = ''
    path = ''
    def __init__(self, path):
        self.path = path
        self.fileName = os.path.basename(path)

class VehXml():
    import xml.etree.ElementTree as ET
    path = ""
    agvs = []
    def __init__(self, path):
        self.path = path
        try:
            tree = self.ET.parse(path)
            root = tree.getroot()
            for agvlist in root:
                for agv in agvlist:
                    self.agvs.append(Agv(agv.find('ID').text, agv.find('IP').text))
        except Exception as inst:
            print('Oops...problem loading vehicle XML...')
            print('Used path: ' + str(path))
            print(str(inst))

    def printAgvs(self):
        print("Agv List:")
        for agv in self.agvs:
            print(agv.ID + " : " + agv.IP)

    def setPath(self, path):
        print('Setting path to vehXml to: ' + str(path))
        print('Previous path: ' + str(self.path))
        self.path = path
        try:
            tree = self.ET.parse(path)
            root = tree.getroot()
            self.agvs.clear()
            for agvlist in root:
                for agv in agvlist:
                    self.agvs.append(Agv(agv.find('ID').text, agv.find('IP').text))
        except Exception as inst:
            print('Oops...problem loading vehicle XML...')
            print(str(inst))

class Model():
    cfg = Config()
    vehXml = VehXml(cfg.dictionary['veh_xml_path'])
    recFolder = cfg.dictionary['rec_folder_path']
    def __init__(self):
        #self.cfg.writeCfg()
        self.vehXml.printAgvs()
        
class ConverterWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    sub_progress = pyqtSignal(int)
    selected_items = []

    def __init__(self, selected_items):
        super().__init__()
        self.selected_items = selected_items

    def run(self):
        #ptvsd.debug_this_thread()
        current_item = 0
        self.progress.emit(0)
        for item in self.selected_items:
            print("Converting recording at: " +  str(item.data(PATH_ROLE)))
            Recog3dToVideo.RecordConverter(str(item.data(PATH_ROLE).resolve()))
            current_item += 1
            self.progress.emit(int(current_item/max(len(self.selected_items),1)*100))
        self.finished.emit()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow, model):
        self.model = model
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowIcon(QtGui.QIcon("resources/cam.png"))
        MainWindow.setEnabled(True)
        MainWindow.resize(400, 600)
        mainLayout = QtWidgets.QHBoxLayout()
        mainLayoutLocal = QtWidgets.QVBoxLayout()
        mainLayoutRemote = QtWidgets.QVBoxLayout()
        listLabelLayout = QtWidgets.QHBoxLayout()


        font = QtGui.QFont()
        font.setPointSize(16)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.convertRecsBtn = QtWidgets.QPushButton(self.centralwidget)
        #self.convertRecsBtn.setGeometry(QtCore.QRect(10, 10, 350, 80))
        self.convertRecsBtn.setFont(font)
        self.convertRecsBtn.setObjectName("convertRecsBtn")
        self.getRemoteRecsBtn = QtWidgets.QPushButton(self.centralwidget)
        self.getRemoteRecsBtn.setFont(font)
        self.getRemoteRecsBtn.setObjectName("getRemoteRecsBtn")
        self.selectAgvComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.selectAgvComboBox.setObjectName("selectAgvComboBox")
        self.selectAgvComboBox.setEditable(True)
        self.selectAgvComboBox.lineEdit().setPlaceholderText("Select AGV")

        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setEnabled(False)
        #self.progressBar.setGeometry(QtCore.QRect(10, 510, 350, 30))
        self.progressBar.setProperty("value", 100)
        self.progressBar.setObjectName("progressBar")
        self.AllcheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.AllcheckBox.setGeometry(QtCore.QRect(250, 100, 80, 20))
        self.AllcheckBox.setObjectName("AllcheckBox")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 100, 141, 16))
        self.label.setObjectName("label")
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(10, 130, 350, 350))
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        fileMenu = self.menubar.addMenu('&File')
        self.SelectVehXmlAction = fileMenu.addAction("Select AGV Toolkit Vehicle XML")
        self.SelectRecFolderAction = fileMenu.addAction("Select Recording Folder")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        mainLayoutLocal.addWidget(self.convertRecsBtn)
        listLabelLayout.addWidget(self.label, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        listLabelLayout.addWidget(self.AllcheckBox, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        mainLayoutLocal.addLayout(listLabelLayout)
        mainLayoutLocal.addWidget(self.listWidget)
        mainLayoutLocal.addWidget(self.progressBar)
        mainLayoutRemote.addWidget(self.getRemoteRecsBtn, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        mainLayoutRemote.addWidget(self.selectAgvComboBox, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        mainLayoutRemote.addStretch()
        mainLayout.addLayout(mainLayoutLocal, stretch=50)
        mainLayout.addLayout(mainLayoutRemote, stretch=50)
        self.centralwidget.setLayout(mainLayout)

        self.retranslateUi(MainWindow)
        self.connectListeners()
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.updateRecordingsOverview(model.recFolder)
        self.updateAgvList()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Recorder Gui"))
        self.convertRecsBtn.setText(_translate("MainWindow", "Convert Recordings"))
        self.getRemoteRecsBtn.setText(_translate("MainWindow", "Get Remote Recordings"))
        self.AllcheckBox.setText(_translate("MainWindow", "Convert ALL"))
        self.label.setText(_translate("MainWindow", "Recordings in folder:"))
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        #item = self.listWidget.item(0)
        #item.setText(_translate("MainWindow", "Rec1"))
        #item = self.listWidget.item(1)
        #item.setText(_translate("MainWindow", "Rec2"))
        self.listWidget.setSortingEnabled(__sortingEnabled)

    def connectListeners(self):
        self.convertRecsBtn.clicked.connect(self.convertRecordings)
        self.getRemoteRecsBtn.clicked.connect(self.getRemoteRecordings)
        self.SelectRecFolderAction.triggered.connect(self.selectRecFolder)
        self.SelectVehXmlAction.triggered.connect(self.selectVehXml)
        self.AllcheckBox.stateChanged.connect(self.checkBoxChanged)

    def selectVehXml(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setNameFilter("XML files (*.xml)")
        if dlg.exec_():
            filename = dlg.selectedFiles()
            print("Newly selected Vehicle xml: " + str(filename))
            model.vehXml.setPath(filename[0])
            print("New agv list:")
            model.vehXml.printAgvs()
            model.cfg.set("paths", "veh_xml_path",filename[0])
            self.updateAgvList()
        else:
            print("Nothing Selected")

    def checkBoxChanged(self):
        if self.AllcheckBox.isChecked():
            self.listWidget.selectAll()

    def selectRecFolder(self):
        folder = str(QtWidgets.QFileDialog.getExistingDirectory(None,directory=self.model.recFolder, caption="Select Recording Directory"))
        if folder:
            print('Newly selected recordings folder: ' + folder)
            model.recFolder = folder
            model.cfg.set("paths", "rec_folder_path", str(folder))
            self.updateRecordingsOverview(model.recFolder)
        else:
            print('No folder selected.')

    def scanForTarFiles(self, dir):
        return Path(dir).rglob("*.tar.gz")

    def updateRecordingsOverview(self, recFolder):
        count = 0
        recordings_in_folder = []
        recordings_in_folder.clear()

        # scan folder for recordings and populate the recordings array
        for entry in self.scanForTarFiles(recFolder):
            recordings_in_folder.append(Recording(entry.resolve()))
            print("Rec: " + entry.name + " at " + str(entry.resolve()))

        # show the recordings in the view
        self.listWidget.clear()
        for recording in recordings_in_folder:
            item = QtWidgets.QListWidgetItem()
            item.setText(recording.fileName)
            item.setData(PATH_ROLE, recording.path)
            self.listWidget.addItem(item)       
            print(recording.fileName)
            print(recording.path)
            count += 1

    def convertRecordings(self):
        if self.AllcheckBox.isChecked():
            selected_items = self.listWidget.selectAll()
        selected_items = self.listWidget.selectedItems()
        print("Selected recordings: " + str(len(selected_items)))
        self.convertRecordingsTask(selected_items)

    def convertRecordingsTask(self, selected_items):
            self.selectedItems = selected_items
            self.convertRecsBtn.setEnabled(True)
            # Step 2: Create a QThread object
            self.thread = QThread()
            # Step 3: Create a worker object
            self.worker = ConverterWorker(selected_items)
            # Step 4: Move worker to the thread
            self.worker.moveToThread(self.thread)
            # Step 5: Connect signals and slots
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.progress.connect(self.setProgressbar)

            # Step 6: Start the thread
            self.thread.start()

            # Final resets
            self.convertRecsBtn.setEnabled(False)
            self.thread.finished.connect(
                lambda: print("Converter thread finished")
            )
            self.thread.finished.connect(
                lambda: self.setProgressbar(100)
            )
            self.thread.finished.connect(
                lambda: self.convertRecsBtn.setEnabled(True)
            )
    
    def getRemoteRecordings(self):
        print("Get Remote recs")

    def updateAgvList(self):
        self.selectAgvComboBox.clear()
        for agv in model.vehXml.agvs:
            self.selectAgvComboBox.addItem(str(agv.ID) + ": " + agv.IP)


    def setProgressbar(self, percent):
        print("\nSet progress to: " + str(percent) + "\n")
        self.progressBar.setProperty("value", percent)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    model = Model()
    ui.setupUi(MainWindow, model)
    MainWindow.show()
    sys.exit(app.exec_())
