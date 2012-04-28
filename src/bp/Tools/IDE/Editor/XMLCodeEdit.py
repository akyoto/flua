from PyQt4 import QtGui, QtCore, uic

class XMLCodeEdit(QtGui.QTextEdit):
	
	def __init__(self, parent = None):
		super(XMLCodeEdit, self).__init__(parent)
		self.setFont(QtGui.QFont("monospace", 10))
		self.setTabStopWidth(4 * 8)
		self.setLineWrapMode(QtGui.QTextEdit.NoWrap)