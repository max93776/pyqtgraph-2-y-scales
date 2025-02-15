# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets
from pyqtgraph import PlotWidget, ViewBox, PlotCurveItem
from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime
import sys
from random import randint
import time

class Ui_MainWindow(object):    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("mainwindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Main layout
        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # TabWidget 
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.main_layout.addWidget(self.tabWidget)

        # Tab 1: 
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tab_layout = QtWidgets.QHBoxLayout(self.tab)

        # Plot 1
        self.widget = PlotWidget(self.tab)
        self.widget.setObjectName("widget")
        self.widget.setBackground('w')

        # Plot 2
        self.pi = self.widget.plotItem
        self.pi.showGrid(x=True, y=True, alpha=0.5)
        self.pi.setLabels(left='value1')
        self.pii = ViewBox()
        self.pi.showAxis('right')
        self.pi.scene().addItem(self.pii)
        self.pi.getAxis('right').linkToView(self.pii)
        self.pii.setXLink(self.pi)
        self.pi.getAxis('right').setLabel('value2', color='#ff0000') 
        self.tab_layout.addWidget(self.widget)
        
        # Textedit
        self.scrollArea = QtWidgets.QTextEdit(self.tab)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setReadOnly(True)
        self.log("Log...")
        self.tab_layout.addWidget(self.scrollArea)

        self.tabWidget.addTab(self.tab, "")
        MainWindow.setCentralWidget(self.centralwidget)

        # Menubar
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        # Diagram
        self.data1 = []  
        self.data2 = []  
        self.x_values = []  
        self.counter = 0

    def add_data_point(self, value1, value2):
        self.counter += 1 
        self.x_values.append(self.counter)  
        self.data1.append(float(value1)) 
        self.data2.append(float(value2)) 
        
        if len(self.x_values) > 100:
                self.x_values = self.x_values[-100:]  
                self.data1 = self.data1[-100:]  
                self.data2 = self.data2[-100:]
        self.widget.clear()
        self.pii.clear()
        self.widget.plot(self.x_values, self.data1, pen='b') 
        self.pii.setGeometry(self.pi.vb.sceneBoundingRect())       
        self.pii.linkedViewChanged(self.pi.vb, self.pii.XAxis)
        self.pii.addItem(PlotCurveItem(self.x_values, self.data2, pen='r'))
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "2-Y-scales"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Tab 1"))
        
    def log(self, text):
        self.scrollArea.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": " + text)
        

class DataCreator(QThread):
    diagram_signal = pyqtSignal(float, float) 
    text_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        while self.running:
            try:
                val1 = randint(0, 1000) / 100
                val2 = randint(0, 100) / 100
                self.diagram_signal.emit(val1, val2)
                self.text_signal.emit("Val1: " + str(val1) + " Val2: " + str(val2))
            except Exception as e:
                self.text_signal.emit(str("Error: " + str(e)))
            
            time.sleep(0.1) 

    def stop(self):
        self.running = False
        self.wait()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    data_thread = DataCreator()
    data_thread.diagram_signal.connect(ui.add_data_point)
    data_thread.text_signal.connect(ui.log)
    data_thread.start()

    def on_exit():
        data_thread.stop()

    app.aboutToQuit.connect(on_exit)
    sys.exit(app.exec_())
