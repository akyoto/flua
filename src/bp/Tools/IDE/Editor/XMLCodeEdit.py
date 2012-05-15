from PyQt4 import QtGui, QtCore, uic

class XMLCodeEdit(QtGui.QTextEdit):
	
	def __init__(self, parent = None):
		super(XMLCodeEdit, self).__init__(parent)
		self.setTabStopWidth(4 * 8)
		self.setLineWrapMode(QtGui.QTextEdit.NoWrap)
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
