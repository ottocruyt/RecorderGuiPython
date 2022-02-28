# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets

class Config():
    import configparser
    dictionary = {}
    # default values:  
    dictionary['option_name_bool'] = False
    dictionary['veh_xml_path'] = "str"

    config = configparser.ConfigParser()

    def importCfg(self):
        self.config.read("config.ini")
        self.dictionary['veh_xml_path'] = self.config.get("section_name", "veh_xml_path")
        self.dictionary['option_name_bool'] = self.config.getboolean("section_name", "option_name_bool")
        print("\nConfig file loaded.")

    def writeCfg(self):
        f = open("config.ini", 'w')
        self.config.write(f)
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
    agvs = []
    def __init__(self, path):
        tree = self.ET.parse(path)
        root = tree.getroot()
        for agvlist in root:
            for agv in agvlist:
                self.agvs.append(Agv(agv.find('ID').text, agv.find('IP').text))
                print(agv.find('ID').text + " : " + agv.find('IP').text)

    def printAgvs(self):
        print("Agv List:")
        for agv in self.agvs:
            print(agv.ID + " : " + agv.IP)
                


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
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(10, 120, 341, 81))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_3")
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
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Recorder Gui"))
        self.pushButton.setText(_translate("MainWindow", "Convert Recordings"))
        self.pushButton_2.setText(_translate("MainWindow", "Select Recording Folder"))
        self.checkBox.setText(_translate("MainWindow", "Convert ALL"))
        self.label.setText(_translate("MainWindow", "Recordings in selected folder"))
        self.pushButton_3.setText(_translate("MainWindow", "Select AgvToolkit XML"))
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        item = self.listWidget.item(0)
        item.setText(_translate("MainWindow", "Rec1"))
        item = self.listWidget.item(1)
        item.setText(_translate("MainWindow", "Rec2"))
        self.listWidget.setSortingEnabled(__sortingEnabled)


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