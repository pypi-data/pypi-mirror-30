# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 12:11:08 2013

@author: Joel
"""



# Python Qt4 bindings for GUI objects
from PyQt5.QtWidgets import QWidget, QVBoxLayout
# import the Qt4Agg FigureCanvas object, that binds Figure to
# Qt4Agg backend. It also inherits from QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
# Matplotlib Figure object
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):
    """Class to represent the FigureCanvas widget"""
    def __init__(self):
        # setup Matplotlib Figure and Axis
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
#        self.fig.tight_layout()
        self.ax.get_yaxis().set_visible(False)
        self.ax.axes.get_xaxis().set_visible(False)
        # initialization of the canvas
        FigureCanvas.__init__(self, self.fig)
        # we define the widget as expandable
#        FigureCanvas.setSizePolicy(self,
#            QtGui.QSizePolicy.Expanding,
#            QtGui.QSizePolicy.Expanding)
#        # notify the system of updated policy
#        FigureCanvas.updateGeometry(self)

class MplWidget(QWidget):
    """Widget defined in Qt Designer"""
    def __init__(self, parent = None):
        # initialization of Qt MainWindow widget
        QWidget.__init__(self, parent)
        # set the canvas to the Matplotlib widget
        self.canvas = MplCanvas()
        self.toolbar = NavigationToolbar(self.canvas, self)
        # create a vertical box layout
        self.vbl = QVBoxLayout()
        # add mpl widget to vertical box
        self.vbl.addWidget(self.canvas)
        self.vbl.addWidget(self.toolbar)
        # set the layout to th vertical box
        self.setLayout(self.vbl)
