# -*- coding: utf-8 -*-

import configparser
import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets, QtNetwork
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QUrl
from pathlib import Path
from robotic_scripts_tools.DatalogConverter import Recog3dToVideo
import requests

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
    def __init__(self, ID, IP='', guiPort='', rackPort='', remoteRackLogPath='', remoteRackRecordPath='', remoteRackConfigPath='', remoteRackCalibrationPath=''):
        self.ID = ID
        self.IP = IP
        self.guiPort = guiPort
        self.rackPort = rackPort
        self.remoteRackLogPath = remoteRackLogPath
        self.remoteRackRecordPath = remoteRackRecordPath
        self.remoteRackConfigPath = remoteRackConfigPath
        self.remoteRackCalibrationPath = remoteRackCalibrationPath

class RackConnection():
    def __init__(self, IP=''):
        self.IP = IP

    def doRequest(self, IP, model, callback):   
        self.IP = IP
        self.model = model
        self.callback = callback
        print("Initializing connection with " + str(IP))
        url = 'http://' + str(IP) + '/cgi-bin/listTarFiles.cgi/logdata/'
        req = QtNetwork.QNetworkRequest(QUrl(url))
        self.nam = QtNetwork.QNetworkAccessManager()
        self.nam.finished.connect(self.handleResponse)
        self.nam.get(req)
        self.model.remoteRecordings.clear()
    
    def download(self, IP, file, callback, progress):
        self.IP = IP
        self.callback = callback
        self.progress = progress
        print("Initializing connection with " + str(IP))
        url = 'http://' + str(IP) + '/logdata/' + str(file)
        req = requests.get(url, allow_redirects=True, stream=True)
        out_path = os.path.join(str(self.model.localRecFolder), str(file)) 
        print("Writing downloaded file to: " + str(out_path))
        with open(out_path, 'wb') as f:
            total_length = int(req.headers.get('content-length'))
            expected_chunks=(total_length/1024) + 1
            i = 0
            for chunk in req.iter_content(chunk_size=1024): 
                if chunk:
                    i = i+1
                    #print("Percentage completed: " + str(100*i/expected_chunks), end='\r')
                    self.progress.emit(100*i/expected_chunks)
                    f.write(chunk)
                    f.flush()

        self.callback()

    def handleResponse(self, reply):

        er = reply.error()

        if er == QtNetwork.QNetworkReply.NoError:
            print("Connected to vehicle " + str(self.IP) + " RACK PC.")
            bytes_string = reply.readAll()
            bytes_string_decoded = str(bytes_string, 'utf-8') 
            #print(bytes_string_decoded)
            bytes_string_decoded_split = bytes_string_decoded.split("\n")
            remoteRackRecordings = []
            remoteRackRecordings.clear()
            for remoteRackRecording in bytes_string_decoded_split:
                if(remoteRackRecording is not ''):
                    print("recording from " + str(self.IP) + ": " + str(remoteRackRecording))
                    remoteRackRecordings.append(remoteRackRecording)
            if(len(remoteRackRecordings) <= 0):
                print("No recordings on vehicle "  + str(self.IP))
            self.model.remoteRecordings = remoteRackRecordings
        else:
            print("Error occured: ", er)
            print(reply.errorString())
            dlg = QtWidgets.QMessageBox()
            dlg.setWindowTitle("Problem Connecting")
            dlg.setText("No connection could be made with " + str(self.IP))
            dlg.exec()
        
        self.callback()

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
        self.agvs.clear()
        self.parseXml(path)
        

    def printAgvs(self):
        print("Agv List:")
        for agv in self.agvs:
            print(agv.ID + " : " + agv.IP)

    def parseXml(self, path):
        self.path = path
        try:
            tree = self.ET.parse(path)
            root = tree.getroot()
            for agvlist in root:
                for agv in agvlist:
                    if(agv.find('CameraEnabled').text.upper() == 'TRUE'):
                        ID = agv.find('ID').text
                        IP = agv.find('IP').text
                        guiPort = agv.find('GuiPort').text
                        rackPort = agv.find('RackPort').text
                        remoteRackLog = agv.find('RemoteRackLog').text
                        remoteRackRecord = agv.find('RemoteRackRecord').text
                        remoteRackConfig = agv.find('RemoteRackConfig').text
                        remoteRackCalibration = agv.find('RemoteRackCalibration').text
                        self.agvs.append(Agv(ID=ID, 
                            IP=IP, 
                            guiPort=guiPort, 
                            rackPort=rackPort, 
                            remoteRackLogPath=remoteRackLog, 
                            remoteRackRecordPath=remoteRackRecord, 
                            remoteRackConfigPath=remoteRackConfig, 
                            remoteRackCalibrationPath=remoteRackCalibration))
        except Exception as inst:
            print('Oops...problem loading vehicle XML...')
            print('Used path: ' + str(path))
            print(str(inst))


    def setPath(self, path):
        print('Setting path to vehXml to: ' + str(path))
        print('Previous path: ' + str(self.path))
        self.agvs.clear()
        self.parseXml(path)

class Model():
    cfg = Config()
    vehXml = VehXml(cfg.dictionary['veh_xml_path'])
    localRecFolder = cfg.dictionary['rec_folder_path']
    rackConnection = RackConnection()
    remoteRecordings = []
    def __init__(self):
        #self.cfg.writeCfg()
        self.vehXml.printAgvs()

class ViewLoadedVehXml(QtWidgets.QMainWindow):
    def __init__(self, model, parent=None):
        super(ViewLoadedVehXml, self).__init__(parent)
        self.setWindowTitle("Loaded Vehicle XML")
        self.setObjectName("ViewLoadedVehXml")
        self.resize(400, 600)
        central_widget = QtWidgets.QWidget() 
        self.setCentralWidget(central_widget)
        mainLayout = QtWidgets.QVBoxLayout()
        for agv in model.vehXml.agvs:
            label = QtWidgets.QLabel(self)
            label.setText(agv.ID + ": " + agv.IP)
            mainLayout.addWidget(label)
            label = QtWidgets.QLabel(self)
            label.setText("     GUI port: " + agv.guiPort)
            mainLayout.addWidget(label)
            label = QtWidgets.QLabel(self)
            label.setText("     RACK port: " + agv.rackPort)
            mainLayout.addWidget(label)
            label = QtWidgets.QLabel(self)
            label.setText("     RACK Log Path: " + agv.remoteRackLogPath)
            mainLayout.addWidget(label)
            label = QtWidgets.QLabel(self)
            label.setText("     RACK Record Path: " + agv.remoteRackRecordPath)
            mainLayout.addWidget(label)
            label = QtWidgets.QLabel(self)
            label.setText("     RACK Config Path: " + agv.remoteRackConfigPath)
            mainLayout.addWidget(label)
            label = QtWidgets.QLabel(self)
            label.setText("     RACK Calibration Path: " + agv.remoteRackCalibrationPath)
            mainLayout.addWidget(label)
        
        mainLayout.addStretch()
        central_widget.setLayout(mainLayout)

class ConverterWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
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
            error = Recog3dToVideo.RecordConverter(str(item.data(PATH_ROLE).resolve()))
            if(error):
                print("Error converting " + str(item.data(PATH_ROLE)))
            current_item += 1
            self.progress.emit(int(current_item/max(len(self.selected_items),1)*100))
        self.finished.emit()

class DownloadWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    sub_progress = pyqtSignal(int)
    selected_items = []

    def __init__(self, IP, model, selected_items, callback):
        super().__init__()
        self.selected_items = selected_items
        self.model = model
        self.IP = IP
        self.callback = callback

    def run(self):
        #ptvsd.debug_this_thread()
        current_item = 0
        self.progress.emit(0)
        for item in self.selected_items:
            print("Downloading recording: " + str(item.data(PATH_ROLE)))
            # download
            self.model.rackConnection.download(self.IP, item.data(PATH_ROLE), self.callback, self.sub_progress)
            current_item += 1
            self.progress.emit(int(current_item))
        self.finished.emit()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow, model):
        self.subProgress = 0
        self.downloadedItems = 0
        self.model = model
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowIcon(QtGui.QIcon("resources/cam.png"))
        MainWindow.setEnabled(True)
        MainWindow.resize(400, 600)
        gridLayout = QtWidgets.QGridLayout()
        listLabelLayout = QtWidgets.QHBoxLayout()
        font = QtGui.QFont()
        font.setPointSize(16)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.convertRecsBtn = QtWidgets.QPushButton(self.centralwidget)
        self.convertRecsBtn.setFont(font)
        self.convertRecsBtn.setObjectName("convertRecsBtn")
        self.getRemoteRecsBtn = QtWidgets.QPushButton(self.centralwidget)
        self.getRemoteRecsBtn.setFont(font)
        self.getRemoteRecsBtn.setObjectName("getRemoteRecsBtn")

        self.downloadRemoteRecsBtn = QtWidgets.QPushButton(self.centralwidget)
        self.downloadRemoteRecsBtn.setFont(font)
        self.downloadRemoteRecsBtn.setObjectName("downloadRemoteRecsBtn")

        self.selectAgvComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.selectAgvComboBox.setObjectName("selectAgvComboBox")
        self.selectAgvComboBox.setEditable(True)
        self.selectAgvComboBox.lineEdit().setPlaceholderText("Select AGV")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setEnabled(False)
        self.progressBar.setProperty("value", 100)
        self.progressBar.setObjectName("progressBar")
        self.progressBar2 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar2.setEnabled(False)
        self.progressBar2.setProperty("value", 100)
        self.progressBar2.setObjectName("progressBar2")
        self.AllcheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.AllcheckBox.setGeometry(QtCore.QRect(250, 100, 80, 20))
        self.AllcheckBox.setObjectName("AllcheckBox")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 100, 141, 16))
        self.label.setObjectName("label")
        self.listWidgetLocal = QtWidgets.QListWidget(self.centralwidget)
        self.listWidgetLocal.setGeometry(QtCore.QRect(10, 130, 350, 350))
        self.listWidgetLocal.setObjectName("listWidget")
        self.listWidgetLocal.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidgetRemote = QtWidgets.QListWidget(self.centralwidget)
        self.listWidgetRemote.setGeometry(QtCore.QRect(10, 130, 350, 350))
        self.listWidgetRemote.setObjectName("listWidgetRemote")
        self.listWidgetRemote.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        fileMenu = self.menubar.addMenu('&File')
        viewMenu = self.menubar.addMenu('&View')
        self.SelectVehXmlAction = fileMenu.addAction("Select AGV Toolkit Vehicle XML")
        self.SelectRecFolderAction = fileMenu.addAction("Select Recording Folder")
        self.ViewLoadedVehXML = viewMenu.addAction("View loaded Vehicle XML")
        self.OpenRecordFolder = viewMenu.addAction("Open recordings folder")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        gridLayout.addWidget(self.convertRecsBtn, 0, 0)
        listLabelLayout.addWidget(self.label, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        listLabelLayout.addWidget(self.AllcheckBox, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        gridLayout.addLayout(listLabelLayout, 1, 0)
        gridLayout.addWidget(self.listWidgetLocal, 2, 0)
        gridLayout.addWidget(self.progressBar, 3, 0)
        gridLayout.addWidget(self.getRemoteRecsBtn, 0, 1)
        gridLayout.addWidget(self.downloadRemoteRecsBtn, 0, 2)
        gridLayout.addWidget(self.selectAgvComboBox, 1, 1)
        gridLayout.addWidget(self.listWidgetRemote, 2, 1)
        gridLayout.addWidget(self.progressBar2, 3, 1)
        self.centralwidget.setLayout(gridLayout)
        self.retranslateUi(MainWindow)
        self.connectListeners()
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.updateRecordingsOverview(model.localRecFolder)
        self.updateAgvList()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Recorder Gui"))
        self.convertRecsBtn.setText(_translate("MainWindow", "Convert Recordings"))
        self.getRemoteRecsBtn.setText(_translate("MainWindow", "List Remote Recordings"))
        self.downloadRemoteRecsBtn.setText(_translate("MainWindow", "Download"))
        self.AllcheckBox.setText(_translate("MainWindow", "Convert ALL"))
        self.label.setText(_translate("MainWindow", "Recordings in local folder:"))
        __sortingEnabled = self.listWidgetLocal.isSortingEnabled()
        self.listWidgetLocal.setSortingEnabled(False)
        self.listWidgetLocal.setSortingEnabled(__sortingEnabled)

    def connectListeners(self):
        self.convertRecsBtn.clicked.connect(self.convertRecordings)
        self.getRemoteRecsBtn.clicked.connect(self.getRemoteRecordings)
        self.downloadRemoteRecsBtn.clicked.connect(self.downloadRecordings)
        self.SelectRecFolderAction.triggered.connect(self.selectRecFolder)
        self.ViewLoadedVehXML.triggered.connect(self.viewLoadedVehXML)
        self.SelectVehXmlAction.triggered.connect(self.selectVehXml)
        self.AllcheckBox.stateChanged.connect(self.checkBoxChanged)
        self.OpenRecordFolder.triggered.connect(self.openRecordFolder)

    def selectVehXml(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setNameFilter("XML files (*.xml)")
        if dlg.exec_():
            filename = dlg.selectedFiles()
            print("Newly selected Vehicle xml: " + str(filename))
            self.model.vehXml.setPath(filename[0])
            print("New agv list:")
            self.model.vehXml.printAgvs()
            self.model.cfg.set("paths", "veh_xml_path",filename[0])
            self.updateAgvList()
        else:
            print("Nothing Selected")

    def checkBoxChanged(self):
        if self.AllcheckBox.isChecked():
            self.listWidgetLocal.selectAll()

    def selectRecFolder(self):
        folder = str(QtWidgets.QFileDialog.getExistingDirectory(None,directory=self.model.localRecFolder, caption="Select Recording Directory"))
        if folder:
            print('Newly selected recordings folder: ' + folder)
            self.model.localRecFolder = folder
            self.model.cfg.set("paths", "rec_folder_path", str(folder))
            self.updateRecordingsOverview(model.localRecFolder)
        else:
            print('No folder selected.')

    def viewLoadedVehXML(self):
        self.viewLoadedVehXMLWindow = ViewLoadedVehXml(self.model)
        self.viewLoadedVehXMLWindow.show()

    def openRecordFolder(self):
        if(os.path.isdir(self.model.localRecFolder)):
            os.startfile(self.model.localRecFolder)
        else:
            print("Recording folder doesn't exist: " + str(self.model.localRecFolder))

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
        self.listWidgetLocal.clear()
        for recording in recordings_in_folder:
            item = QtWidgets.QListWidgetItem()
            item.setText(recording.fileName)
            item.setData(PATH_ROLE, recording.path)
            self.listWidgetLocal.addItem(item)       
            print(recording.fileName)
            print(recording.path)
            count += 1

    def updateRemoteRecordingsOverview(self):
        count = 0
        self.listWidgetRemote.clear()
        for recording in self.model.remoteRecordings:
            item = QtWidgets.QListWidgetItem()
            item.setText(recording)
            item.setData(PATH_ROLE, recording)
            self.listWidgetRemote.addItem(item)       
            count += 1

    def convertRecordings(self):
        if self.AllcheckBox.isChecked():
            selected_items = self.listWidgetLocal.selectAll()
        selected_items = self.listWidgetLocal.selectedItems()
        print("Selected recordings: " + str(len(selected_items)))
        self.convertRecordingsTask(selected_items)

    def downloadRecordingsTask(self, IP, model, selected_items, callback):
            self.selectedItems2 = selected_items
            # Step 2: Create a QThread object
            self.thread2 = QThread()
            # Step 3: Create a worker object
            self.worker2 = DownloadWorker(IP, model, selected_items, callback)
            # Step 4: Move worker to the thread
            self.worker2.moveToThread(self.thread2)
            # Step 5: Connect signals and slots
            self.thread2.started.connect(self.worker2.run)
            self.worker2.finished.connect(self.thread2.quit)
            self.worker2.finished.connect(self.worker2.deleteLater)
            self.thread2.finished.connect(self.thread2.deleteLater)
            self.worker2.progress.connect(self.setDownloadProgressTotal)
            self.worker2.sub_progress.connect(self.setDownloadSubProgress)


            # Step 6: Start the thread
            self.thread2.start()
            self.downloadRemoteRecsBtn.setEnabled(False)
            # Final resets
            self.thread2.finished.connect(
                lambda: print("Download thread finished")
            )
            self.thread2.finished.connect(
                lambda: self.setProgressbar2(100)
            )
            self.thread2.finished.connect(
                lambda: self.downloadRemoteRecsBtn.setEnabled(True)
            )

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
        callback = self.updateRemoteRecordingsOverview
        print("Getting remote recording list from " + str(self.selectAgvComboBox.currentText()))
        IP = str(self.selectAgvComboBox.currentData()) # IP is stored in the data
        self.listWidgetRemote.clear()
        self.model.rackConnection.doRequest(IP, self.model, callback)

    def downloadRecordings(self):
        callback = self.updateLocalRecordingsOverview
        print("Downloading remote recording list from " + str(self.selectAgvComboBox.currentText()))
        IP = str(self.selectAgvComboBox.currentData()) # IP is stored in the data
        selected_items = self.listWidgetRemote.selectedItems()
        print("Selected recordings: " + str(len(selected_items)))
        self.downloadRecordingsTask(IP, self.model, selected_items, callback)
        

    def updateLocalRecordingsOverview(self):
        self.updateRecordingsOverview(model.localRecFolder)


    def updateAgvList(self):
        self.selectAgvComboBox.clear()
        for agv in self.model.vehXml.agvs:
            self.selectAgvComboBox.addItem(str(agv.ID) + ": " + agv.IP, agv.IP)


    def setProgressbar(self, percent):
        #print("\nSet progress to: " + str(percent) + "\n")
        self.progressBar.setProperty("value", percent)
    
    def setDownloadProgressTotal(self, downloadedItems):
        print("Downloaded items: " + str(downloadedItems))
        self.downloadedItems = downloadedItems
        self.subProgress = 0
        self.combineProgressBar2()

    def setDownloadSubProgress(self, percent):
        self.subProgress = percent
        self.combineProgressBar2()

    def combineProgressBar2(self):
        self.setProgressbar2(self.subProgress/len(self.selectedItems2) + 100*self.downloadedItems/len(self.selectedItems2))

    def setProgressbar2(self, percent):
        #print("\nSet progress 2 to: " + str(percent) + "\n")
        self.progressBar2.setProperty("value", percent)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    model = Model()
    ui.setupUi(MainWindow, model)
    MainWindow.show()
    sys.exit(app.exec_())
