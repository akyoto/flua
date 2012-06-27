from PyQt4 import QtGui, QtCore

class BPIntelliView(QtGui.QWidget):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.vBox = QtGui.QVBoxLayout()
		#self.vBox.addStretch(1)
		self.setLayout(self.vBox)
		self.setContentsMargins(0, 0, 0, 0)
		self.vBox.setContentsMargins(-1, -1, -1, -1)
		self.vBox.setSpacing(-1)
		self.setMinimumWidth(300)
		#self.vBox.setSizeConstraint(QtGui.QLayout.SetFixedSize)
		
	def addIntelligentWidget(self, widget, stretch = 0):
		self.vBox.addWidget(widget, stretch)
