from PyQt4 import QtGui, QtCore

class BPWorkspacesView(QtGui.QWidget):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.bpIDE = parent
		
		self.group = QtGui.QButtonGroup(self)
		
		hBox = QtGui.QHBoxLayout()
		for i in range(len(self.bpIDE.workspaces)):
			button = QtGui.QPushButton(str(i + 1))
			button.setCheckable(True)
			button.setAutoExclusive(True)
			button.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
			button.setMaximumWidth(36)
			if i == 0:
				button.setChecked(True)
			hBox.addWidget(button)
			self.group.addButton(button)
		
		self.setLayout(hBox)
		
		self.group.buttonClicked.connect(self.setCurrentWorkspace)
		
		self.setMaximumHeight(24)
		
		hBox.setContentsMargins(0, 0, 0, 0)
		self.setContentsMargins(0, 0, 0, 0)
		
	def setCurrentWorkspace(self, button):
		index = int(button.text()) - 1
		self.bpIDE.setCurrentWorkspace(index)
		
	def updateView(self):
		pass
