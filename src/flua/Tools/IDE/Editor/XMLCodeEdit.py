from PyQt4 import QtGui, QtCore, uic

class XMLCodeEdit(QtGui.QPlainTextEdit):
	
	def __init__(self, parent = None):
		super().__init__(parent)
		self.setTabStopWidth(4 * 8)
		self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
		self.node = None
		
	def setNode(self, node):
		self.node = node
		
	def showEvent(self, event):
		self.updateView()
		event.accept()
		
	def updateView(self):
		if self.node:
			self.setPlainText(self.node.toprettyxml())
		else:
			self.clear()
