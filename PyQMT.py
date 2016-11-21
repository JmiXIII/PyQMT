import sys
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns
sns.set(style='ticks', palette='Set2')
sns.despine()
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
import pandas as pd
import numpy as np


class PandasModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = np.array(data.values)
        self._cols = data.columns
        self.r, self.c = np.shape(self._data)

    def rowCount(self, parent=None):
        return self.r

    def columnCount(self, parent=None):
        return self.c

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return self._data[index.row(), index.column()]
        return None


    def headerData(self, p_int, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._cols[p_int]
            elif orientation == QtCore.Qt.Vertical:
                return p_int
        return None



class QMT(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(QMT, self).__init__(parent)
        # Create Qtable view widget
        self.view = QtGui.QTableView(self)
        self.view.clicked.connect(self.viewClicked)

        # Get the header to catch clicked on it
        self.header = self.view.horizontalHeader()
        self.header.sectionClicked.connect(self.headerClicked)
        self.view.setSortingEnabled(True)

        # Create Canvas for graph
        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.graph = self.fig.add_subplot(111)

        # Create Series Datas
        self.QStat=QtGui.QLabel("Stats",self)

        # File browser
        self.treeView = QtGui.QTreeView(self)
        self.fileSystemModel = QtGui.QFileSystemModel(self.treeView)
        self.fileSystemModel.setReadOnly(True)
        root = self.fileSystemModel.setRootPath('Z:/resultats/807677')
        self.treeView.setModel(self.fileSystemModel)
        self.treeView.setRootIndex(root)
        self.treeView.clicked.connect(self.treeView_clicked)

        #Layout management
        #Initiate splitter
        splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter2 = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter1.addWidget(self.treeView)
        splitter1.addWidget(self.canvas)
        splitter1.addWidget(self.QStat)

        splitter2.addWidget(splitter1)
        splitter2.addWidget(self.view)

        #Horizontal Layout Box
        hbox = QtGui.QVBoxLayout()
        hbox.addWidget(splitter2)

        #initiate widget to be shown
        widget = QtGui.QWidget(self)
        widget.setLayout(hbox)

        #Set widget as central widget
        self.setCentralWidget(widget)

        # Windows & Menu stuff
        self.initUI()


    def initUI(self):
        # GUI init
        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        openFile = QtGui.QAction(QtGui.QIcon('open.png'), 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showDialog)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        fileMenu.addAction(openFile)

        self.statusBar()
        self.setGeometry(200, 200, 400, 400)
        self.setWindowTitle('Menubar')
        self.show()
        self.view.show()

    def showDialog(self):
        #Used to open a file and initiate model
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                'Z:/resultats/807677')
        return fname

    def viewClicked(self, clickedIndex):
        column=clickedIndex.column()
        #data=self.pdata.iloc[:, column]
        try:
            data = self.pdata.iloc[:, column]
            self.csv2hist(self.pdata, column)
            self.view.update()
            self.PStatUpdate(data)
        except:
            pass

    def headerClicked(self, logicalIndex):
        self.order = self.header.sortIndicatorOrder()
        self.pdata.sort(self.pdata.columns[logicalIndex],
                        ascending=self.order, inplace = True)
        self.model = PandasModel(self.pdata)
        self.view.setModel(self.model)
        self.view.update()

    def treeView_clicked(self, index):
        indexItem = self.fileSystemModel.index(index.row(), 0, index.parent())
        fileName = self.fileSystemModel.fileName(indexItem)
        filePath = self.fileSystemModel.filePath(indexItem)
        self.csv2data(filePath)
        self.csv2hist(self.pdata, 5)

    def csv2data(self, fname):
        self.pdata = self.file2df(fname)
        self.model = PandasModel(self.pdata)
        self.view.setModel(self.model)

    def file2df(self, elmnt):
        data = pd.read_csv(elmnt, header = None,
                     sep='\t+',
                     index_col = False,)
        data = data[data[3]==True]
        return data

    def csv2hist(self, df, index):
        self.graph.cla()
        print(index)
        data = self.pdata.iloc[:, index]
        print(data)
        sns.distplot(data.dropna().astype(np.float),
                    ax = self.graph)
        self.canvas.draw()

    def PStatUpdate(self, data):
        stat = data.dropna().apply(np.float)
        stat_desc=str(stat.describe())
        self.QStat.setText(stat_desc)

    def PDataScrap(self, data):
        '''
        Calculate scrap rate of a series
        '''
        Pass


def main(args):
    app = QApplication(args)
    win = QMT()
    win.show()
    app.exec_()



if __name__=="__main__":
    main(sys.argv)
