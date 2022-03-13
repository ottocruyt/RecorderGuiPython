# -*- coding: utf-8 -*-

import configparser
from fileinput import filename
import sys
import os
import time
from PyQt5 import QtCore, QtGui, QtWidgets

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
    recFolder = ""
    def __init__(self):
        self.vehXml.printAgvs()
        #self.cfg.writeCfg()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow, model):
        self.model = model
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.convertRecsBtn = QtWidgets.QPushButton(self.centralwidget)
        self.convertRecsBtn.setGeometry(QtCore.QRect(10, 300, 341, 81))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.convertRecsBtn.setFont(font)
        self.convertRecsBtn.setObjectName("convertRecsBtn")
        self.selectRecFolderBtn = QtWidgets.QPushButton(self.centralwidget)
        self.selectRecFolderBtn.setGeometry(QtCore.QRect(10, 210, 341, 81))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.selectRecFolderBtn.setFont(font)
        self.selectRecFolderBtn.setObjectName("selectRecFolderBtn")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setEnabled(False)
        self.progressBar.setGeometry(QtCore.QRect(10, 510, 771, 31))
        self.progressBar.setProperty("value", 100)
        self.progressBar.setObjectName("progressBar")
        self.AllcheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.AllcheckBox.setGeometry(QtCore.QRect(520, 100, 81, 17))
        self.AllcheckBox.setObjectName("AllcheckBox")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(380, 100, 141, 16))
        self.label.setObjectName("label")
        self.setVehXmlBtn = QtWidgets.QPushButton(self.centralwidget)
        self.setVehXmlBtn.setGeometry(QtCore.QRect(10, 120, 341, 81))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.setVehXmlBtn.setFont(font)
        self.setVehXmlBtn.setObjectName("setVehXmlBtn")
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(380, 120, 221, 251))
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.connectListeners()
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Recorder Gui"))
        self.convertRecsBtn.setText(_translate("MainWindow", "Convert Recordings"))
        self.selectRecFolderBtn.setText(_translate("MainWindow", "Select Recording Folder"))
        self.AllcheckBox.setText(_translate("MainWindow", "Convert ALL"))
        self.label.setText(_translate("MainWindow", "Recordings in folder:"))
        self.setVehXmlBtn.setText(_translate("MainWindow", "Select AgvToolkit XML"))
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        #item = self.listWidget.item(0)
        #item.setText(_translate("MainWindow", "Rec1"))
        #item = self.listWidget.item(1)
        #item.setText(_translate("MainWindow", "Rec2"))
        self.listWidget.setSortingEnabled(__sortingEnabled)

    def connectListeners(self):
        self.setVehXmlBtn.clicked.connect(self.selectVehXml)
        self.selectRecFolderBtn.clicked.connect(self.selectRecFolder)
        self.convertRecsBtn.clicked.connect(self.convertRecordings)

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
        else:
            print("Nothing Selected")

    def selectRecFolder(self):
        folder = str(QtWidgets.QFileDialog.getExistingDirectory(None, "Select Recording Directory"))
        if folder:
            print('Newly selected recordings folder: ' + folder)
            model.recFolder = folder
            self.updateRecordingsOverview(model.recFolder)
        else:
            print('No folder selected.')

    def updateRecordingsOverview(self, recFolder):
        count = 0
        recordings_in_folder = []
        recordings_in_folder.clear()

        # scan folder for recordings and populate the recordings array
        for entry in os.scandir(recFolder):
            if not (entry.is_file() and entry.name.endswith('.tar.gz')):
                continue
            else:
                recordings_in_folder.append(Recording(entry.path))
                print("Rec: " + entry.name + " at " + entry.path)

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
        current_item = 0
        self.setProgressbar(current_item/max(len(selected_items),1)*100)
        print("Selected recordings: " + str(len(selected_items)))
        for item in selected_items:
            print("Item selected text: " + item.text())
            print("Item selected: " + str(item))
            print("Item path: " + str(item.data(PATH_ROLE)))
            self.convertRecording(item.data(PATH_ROLE))
            current_item += 1
            self.setProgressbar(current_item/max(len(selected_items),1)*100)
            
        self.setProgressbar(100)


    
    def convertRecording(self, path):
        print("Converting recording at: " + str(path))
        time.sleep(5)

    def setProgressbar(self, percent):
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
