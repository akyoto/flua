from PyQt4 import QtGui, QtCore

class BPWorkspacesView(QtGui.QWidget):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.bpIDE = parent
		
		self.group = QtGui.QButtonGroup(self)
		
		hBox = QtGui.QHBoxLayout()
		for i in range(len(self.bpIDE.workspaces)):
			wsNumber = i + 1
			button = QtGui.QPushButton(str(wsNumber))
			button.setCheckable(True)
			button.setAutoExclusive(True)
			button.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
			button.setMaximumWidth(36)
			shortCutInfo = self.getShortcutInfo(wsNumber)
			button.setToolTip("<strong>Workspace %d</strong><br/>%s" % (wsNumber, shortCutInfo))
			button.setShortcut("Alt+%d" % (wsNumber))
			if i == 0:
				button.setChecked(True)
			hBox.addWidget(button)
			self.group.addButton(button, i)
		
		self.setLayout(hBox)
		
		self.group.buttonClicked.connect(self.setCurrentWorkspace)
		
		self.setMaximumHeight(24)
		
		hBox.setContentsMargins(0, 0, 0, 0)
		self.setContentsMargins(0, 0, 0, 0)
		
	def getShortcutInfo(self, number):
		return "<em style='font-size: 10px;'>Alt + %d</em>" % number
		
	def setCurrentWorkspace(self, button):
		index = int(button.text()) - 1
		self.bpIDE.setCurrentWorkspace(index)
		
	def updateCurrentWorkspace(self):
		fileList = self.bpIDE.currentWorkspace.getTabNameList()
		wsID = self.bpIDE.currentWorkspace.getWorkspaceID()
		fileListHTML = "</li><li>".join(fileList)
		
		if fileList:
			self.group.button(wsID).setToolTip("<strong>Workspace %d</strong><br/>%s<ul style='padding: 0; margin: 0;'><li>%s</li></ul>" % (wsID + 1, self.getShortcutInfo(wsID + 1), fileListHTML))
		else:
			self.group.button(wsID).setToolTip("Workspace %d<br/>%s" % (wsID + 1, self.getShortcutInfo(wsID + 1)))
