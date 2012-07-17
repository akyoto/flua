from PyQt4 import QtGui, QtCore

class BPWorkspacesView(QtGui.QWidget):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.bpIDE = parent
		
		self.setObjectName("WorkspaceSwitcher")
		self.group = QtGui.QButtonGroup(self)
		
		shortcuts = ["1", "2", "3", "4", "Q", "W", "E", "R"]
		self.indexForWorkspace = {
			"1" : 0,
			"2" : 1,
			"3" : 2,
			"4" : 3,
			"Q" : 4,
			"W" : 5,
			"E" : 6,
			"R" : 7,
		}
		
		hBox = QtGui.QHBoxLayout()
		
		for i in range(len(self.bpIDE.workspaces)):
			wsNumber = i + 1
			button = QtGui.QPushButton(str(shortcuts[i]))
			button.setCheckable(True)
			button.setAutoExclusive(True)
			button.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
			#button.setMaximumWidth(24)
			shortCutInfo = self.getShortcutInfo(wsNumber)
			
			button.setToolTip("<strong>Workspace %s</strong><br/>%s" % (shortcuts[i], shortCutInfo))
			#button.setShortcut("Alt+%s" % shortcuts[i])
			button.setObjectName("WorkspaceSwitcherButton")
			
			if i == 0:
				button.setChecked(True)
			
			hBox.addWidget(button)
			self.group.addButton(button, i)
		
		self.setLayout(hBox)
		
		self.group.buttonClicked.connect(self.setCurrentWorkspaceByButton)
		
		#self.setMaximumHeight(20)
		
		hBox.setContentsMargins(0, 0, 0, 0)
		self.setContentsMargins(0, 0, 0, 0)
		
	def hideGroup(self, num):
		start = num * 4
		end = start + 4
		
		for i in range(len(self.bpIDE.workspaces)):
			if i >= start and i < end:
				self.group.button(i).hide()
			else:
				self.group.button(i).show()
		
	def getShortcutInfo(self, number):
		return "<em style='font-size: 10px;'>Alt + %d</em>" % number
		
	def setCurrentWorkspaceByButton(self, button):
		#if not self.bpIDE.loadingFinished:
		#	return
		
		index = self.indexForWorkspace[button.text()]
		self.hideGroup(index < 4)
		self.bpIDE.setCurrentWorkspace(index, activateButton = False)
		
	def updateCurrentWorkspace(self):
		fileList = self.bpIDE.currentWorkspace.getTabNameList()
		wsID = self.bpIDE.currentWorkspace.getWorkspaceID()
		fileListHTML = "</li><li>".join(fileList)
		
		if fileList:
			self.group.button(wsID).setToolTip("<strong>Workspace %d</strong><br/>%s<ul style='padding: 0; margin: 0;'><li>%s</li></ul>" % (wsID + 1, self.getShortcutInfo(wsID + 1), fileListHTML))
		else:
			self.group.button(wsID).setToolTip("Workspace %d<br/>%s" % (wsID + 1, self.getShortcutInfo(wsID + 1)))
