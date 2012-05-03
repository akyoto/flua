from PyQt4 import QtGui, QtCore

class BPMessageView(QtGui.QListWidget):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.bpIDE = parent
		self.setWordWrap(True)
		#self.setContentsMargins(0, 0, 0, 0)
		#self.setMaximumHeight(0)
		#self.setScrollBarPolicy(QtGui.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.icon = QtGui.QIcon("images/tango/status/dialog-warning.svg")
		self.itemClicked.connect(self.goToLineOfItem)
		
	def goToLineOfItem(self, item):
		lineNum = int(item.statusTip())
		if lineNum != -1:
			self.bpIDE.goToLineEnd(lineNum)
		
	def addMessage(self, msg):
		newItem = QtGui.QListWidgetItem(self.icon, msg)
		newItem.setStatusTip(str(-1))
		self.addItem(newItem)
		
	def addLineBasedMessage(self, lineNumber, msg):
		newItem = QtGui.QListWidgetItem(self.icon, msg)
		newItem.setStatusTip(str(lineNumber))
		#self.setSizeHint(QtCore.QSize(0, 10))
		self.addItem(newItem)
		
	def updateView(self):
		if self.bpIDE.intelliEnabled:
			itemNum = self.count()
			if itemNum:
				#self.adjustSize()#resize(0, 0)
				#self.setMaximumHeight(self.count() * 50)
				
				maxHeight = 13
				for i in range(itemNum):
					maxHeight += self.visualItemRect(self.item(i)).height() + 2
				self.setMaximumHeight(maxHeight)
				
				if self.isHidden():
					self.show()
			else:
				if self.isVisible():
					self.hide()
