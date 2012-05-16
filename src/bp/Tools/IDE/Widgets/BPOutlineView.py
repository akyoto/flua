from PyQt4 import QtGui, QtCore

class BPOutlineView(QtGui.QWidget):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.bpIDE = parent
		
		self.setFont(self.bpIDE.config.standardFont)
		
	def updateView(self):
		pass
