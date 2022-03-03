# -*- coding: utf-8 -*-

import configparser
from PyQt5 import QtCore, QtGui, QtWidgets

class Config():
    import configparser
    dictionary = {}
    # default values:  
    dictionary['veh_xml_path'] = ""

    config = configparser.ConfigParser()

    def importCfg(self):
        try:
            self.config.read("config.ini")
            self.dictionary['veh_xml_path'] = self.config.get("paths", "veh_xml_path")
            print("\nConfig file loaded.")
        except configparser.NoSectionError as inst:
            print('Expected section missing in config: ' + str(inst))
        except Exception as inst:
            print('Oops...problem openning config file...')
           # print(inst) 


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
            print(str(inst))

    def printAgvs(self):
        print("Agv List:")
        for agv in self.agvs:
            print(agv.ID + " : " + agv.IP)

    def setPath(self, path):
        self.path = path
        try:
            tree = self.ET.parse(path)
            root = tree.getroot()
            for agvlist in root:
                for agv in agvlist:
                    self.agvs.append(Agv(agv.find('ID').text, agv.find('IP').text))
        except Exception as inst:
            print('Oops...problem loading vehicle XML...')
            print(str(inst))

class Model()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(False)
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(10, 300, 341, 81))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(10, 210, 341, 81))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setEnabled(False)
        self.progressBar.setGeometry(QtCore.QRect(10, 510, 771, 31))
        self.progressBar.setProperty("value", 100)
        self.progressBar.setObjectName("progressBar")
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setGeometry(QtCore.QRect(520, 100, 81, 17))
        self.checkBox.setObjectName("checkBox")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(380, 100, 141, 16))
        self.label.setObjectName("label")
        self.setVehXmlBtn = QtWidgets.QPushButton(self.centralwidget)
        self.setVehXmlBtn.setGeometry(QtCore.QRect(10, 120, 341, 81))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.setVehXmlBtn.setFont(font)
        self.setVehXmlBtn.setObjectName("setVehXmlBtn")
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(380, 120, 221, 251))
        self.listWidget.setObjectName("listWidget")
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.connectListeners(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Recorder Gui"))
        self.pushButton.setText(_translate("MainWindow", "Convert Recordings"))
        self.pushButton_2.setText(_translate("MainWindow", "Select Recording Folder"))
        self.checkBox.setText(_translate("MainWindow", "Convert ALL"))
        self.label.setText(_translate("MainWindow", "Recordings in selected folder"))
        self.setVehXmlBtn.setText(_translate("MainWindow", "Select AgvToolkit XML"))
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        item = self.listWidget.item(0)
        item.setText(_translate("MainWindow", "Rec1"))
        item = self.listWidget.item(1)
        item.setText(_translate("MainWindow", "Rec2"))
        self.listWidget.setSortingEnabled(__sortingEnabled)

    def connectListeners(self, MainWindow):
        self.setVehXmlBtn.clicked.connect()

    def selectVehXml():

        

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    config = Config()
    config.importCfg()
    vehXml = VehXml(config.dictionary['veh_xml_path'])
    vehXml.printAgvs()
    config.writeCfg()
    MainWindow.show()
    sys.exit(app.exec_())
