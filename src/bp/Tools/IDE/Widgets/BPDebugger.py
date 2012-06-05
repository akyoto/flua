from PyQt4 import QtGui, QtCore

class BPDebugger(QtGui.QWidget):
	
	def __init__(self, parent, bpIDE):
		super().__init__(parent)
		self.ce = parent
		self.bpIDE = bpIDE
		self.setObjectName("Debugger")
		self.hide() 
		
		#self.icon = QtGui.QIcon("images/icons/status/dialog-warning.png")
		
	def updateView(self):
		pass
