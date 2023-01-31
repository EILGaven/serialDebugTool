# _*_ coding: utf-8 _*_
#import os
import struct
import sys
import time

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog,\
    QMessageBox, QLabel, QPushButton, QPlainTextEdit, QTextEdit, QVBoxLayout, QHBoxLayout
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QThread, pyqtSignal, qDebug, QSettings, QVariant, Qt, QObject, QPoint
from PyQt5.QtGui import QIcon, QPixmap
#from qt_material import appl_stylesheet

#import mySerialUI
# from mySerialUI import Ui_MainWindow
from Ui_mySerialUI import Ui_MainWindow
from serialUtils import get_ports, open_port


class serialThread(QThread):
    data_arrivce_signal = pyqtSignal(name='serial_data')

    def __init__(self, ser=None):
        super().__init__()
        self.ser = ser
        self.data = ''

    def run(self):
        while True:
            if self.ser and self.ser.inWaiting():
                self.data = self.ser.read(self.ser.inWaiting())
                self.data_arrivce_signal.emit()

# class serialThread(QThread):
#     data_arrivce_signal = pyqtSignal(name='serial_data')
#     def __init__(self,ser):
#         super().__init__()
#         self.ser = ser
#     def run(self):
#         while True:
#             if self.ser.inWaiting():
#                 data = []
#                 for i in range(ser.inWaiting()):
#                     s = ser.read(1).hex()
#                     data.append(s)
#                 print(data)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # mySerialUI.QtCore.seria
        self.initialize_ui()
        self.read_setting()
        self.currentPort = None
        self.serial_thread = serialThread()
        self.serial_thread.start()
        self.serial_thread.data_arrivce_signal.connect(self.show_data)
        self.ui.openPort.clicked.connect(self.open_port)
        self.ui.closePort.clicked.connect(self.close_port)
        self.ui.sendData.clicked.connect(self.send_data)
        self.ui.clearData.clicked.connect(self.clear_data)

    def hex2object(x, codes):
        return struct.unpack(codes, bytes.fromhex(x))[0]

    def clear_data(self):
        self.ui.receiveData.setText('')

    def show_data(self):
        data = self.serial_thread.data
        dataText = self.ui.receiveData.toPlainText()
        self.ui.receiveData.setText(dataText + data.decode('utf-8'))

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.currentPort is not None:
            self.close_port()
        self.save_setting()
        self.serial_thread.terminate()

    def read_setting(self):
        setting = QSettings('serial_config', 'serial_app')
        # window
        if setting.value('geometry') is not None:
            self.restoreState(setting.value('geometry'))
        if setting.value('windowState') is not None:
            self.restoreState(setting.value('windowState'))
        if setting.value('port_name') is not None:
            self.ui.serialSelection.setCurrentIndex(
                int(setting.value('port_name')))
        if setting.value('baudrate') is not None:
            self.ui.baudrateSelection.setCurrentIndex(
                int(setting.value('baudrate')))
        if setting.value('byteSize') is not None:
            self.ui.byteSize.setCurrentIndex(int(setting.value('byteSize')))
        if setting.value('stopBit') is not None:
            self.ui.stopBit.setCurrentIndex(int(setting.value('stopBit')))
        if setting.value('parity') is not None:
            self.ui.parity.setCurrentIndex(int(setting.value('parity')))

    def save_setting(self):
        setting = QSettings('serial_config', 'serial_app')
        # window
        setting.setValue('geometry', self.saveGeometry())
        setting.setValue('windowState', self.saveState())
        setting.setValue('port_name', self.ui.serialSelection.currentIndex())
        setting.setValue('baudrate', self.ui.baudrateSelection.currentIndex())
        setting.setValue('byteSize', self.ui.byteSize.currentIndex())
        setting.setValue('stopBit', self.ui.stopBit.currentIndex())
        setting.setValue('parity', self.ui.parity.currentIndex())

    def send_data(self):
        """:param data: str"""
        input_data = self.ui.inputData.toPlainText()
        print(input_data)
        self.currentPort.write(input_data.encode('utf-8'))  # ('abc')

    def close_port(self):
        if self.currentPort is not None:
            self.serial_thread.ser = None
            self.currentPort.close()
            # self.serial_thread.terminate()
            self.ui.portStatus.setText(self.currentPort.port + ' ' + 'Closed')
            self.ui.openPort.setEnabled(True)
            self.ui.closePort.setEnabled(False)
            self.ui.sendData.setEnabled(False)
            self.currentPort = None

    def open_port(self):
        if self.ui.serialSelection.count() == 0:
            print('currentPortName is none')
            self.ui.portStatus.setText('没有找到串口设备!')
            return
        else:
            print('Port count:', self.ui.serialSelection.count())
        if self.currentPort is None:
            # portName, baudrate, byteSize, stopBit, parity
            currentPortName = self.ui.serialSelection.currentText()
            currentBaudrate = int(self.ui.baudrateSelection.currentText())
            # print(self.ui.byteSize.currentText())
            currentByteSize = int(self.ui.byteSize.currentText())
            print('currentByteSize:', currentByteSize,
                  'type:', type(currentByteSize))
            index = self.ui.stopBit.currentIndex()
            stopBitList = [1, 1.5, 2]
            currentStopBit = stopBitList[index]
            currentParity = self.ui.parity.currentText()[0]
            #print(currentByteSize, currentStopBit, currentParity)
            self.currentPort = open_port(
                currentPortName, currentBaudrate, currentByteSize, currentStopBit, currentParity)
            # print(self.currentPort.baudrate,type(self.currentPort.baudrate))
            # self.currentPort.
            if self.currentPort.isOpen():
                self.serial_thread.ser = self.currentPort
                self.ui.openPort.setEnabled(False)
                self.ui.closePort.setEnabled(True)
                self.ui.sendData.setEnabled(True)
                self.ui.portStatus.setText(currentPortName+' '+'Opened')
                self.ui.receiveData.setText('')
            else:
                self.ui.openPort.setEnabled(True)
                self.ui.closePort.setEnabled(False)
                self.ui.sendData.setEnabled(False)
                self.ui.portStatus.setText(currentPortName + ' ' + 'Closed')

    def initialize_ui(self):
        availablePorts = get_ports()
        for port in availablePorts:
            self.ui.serialSelection.addItem(port)

        baudrateList = ['1200', '2400', '4800',
                        '9600', '19200', '38400', '115200']
        for baudrate in baudrateList:
            self.ui.baudrateSelection.addItem(baudrate)
        self.ui.baudrateSelection.setCurrentText('9600')


if __name__ == '__main__':
    # get_ports()
    app = QApplication(sys.argv)
    w = MainWindow()
    w.setWindowTitle("串口调试助手")
    w.show()
    sys.exit(app.exec_())
