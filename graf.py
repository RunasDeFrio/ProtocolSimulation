# ------------------------------------------------------
# -------------------- mplwidget.py --------------------
# ------------------------------------------------------
from PyQt5.QtWidgets import*

from matplotlib.backends.backend_qt5agg import FigureCanvas

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

    
class MplWidget(QWidget):
    
    def __init__(self, parent = None):

        QWidget.__init__(self, parent)
        
        self.canvas = FigureCanvas(Figure())
        
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        self.legends = list()
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.ploter = self.canvas.axes
        self.setLayout(vertical_layout)
        
    def Clear(self):
        self.legends = list()
        self.ploter.clear()

    def AddFunc(self, x, y, legend = None):
        self.ploter.plot(x, y)
        if not legend is None:
            self.legends.append(legend)

    def CreateHist(self, x, num_bins, legend = None):
        n, bins, patches = self.ploter.hist(x, num_bins, density=True, stacked = True, facecolor='blue', alpha=0.5)
        if not legend is None:
            self.legends.append(legend)
        return n, bins, patches

    def AddHist(self, counts, bins, legend = None):
        self.ploter.hist(bins[:-1], bins, weights=counts)
        if not legend is None:
            self.legends.append(legend)
    
    def Draw(self, title):
        self.ploter.legend(self.legends, loc='upper right')
        self.ploter.set_title(title)
        self.canvas.draw()