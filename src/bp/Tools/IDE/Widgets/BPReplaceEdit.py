from PyQt4 import QtGui, QtCore

class BPReplaceEdit(QtGui.QLineEdit):

	def __init__(self, parent = None):
		super().__init__(parent)
		self.bpIDE = parent
		self.searchEdit = self.bpIDE.searchEdit
		self.setPlaceholderText("Replace occurences with...")
		self.hide()
		
	def replaceAll(self, ce):
		qdoc = ce.qdoc
		text = self.searchEdit.text()
		cursor = ce.textCursor()
		findFlags = QtGui.QTextDocument.FindCaseSensitively
		
		if self.searchEdit.regExSearch:
			text = QtCore.QRegExp(text)
			
		# Start of document
		cursor.movePosition(QtGui.QTextCursor.Start)
		
		cursor.beginEditBlock()
		
		# Begin replacing
		while 1:
			nextResult = qdoc.find(text, cursor, findFlags)
			if nextResult.position() == -1:
				break
			
			
			nextResult.removeSelectedText()
			nextResult.insertText(self.text())
		
		cursor.endEditBlock()
		
	def keyPressEvent(self, event):
		key = event.key()
		if key == QtCore.Qt.Key_Escape:
			self.searchEdit.setFocus()
		elif key == QtCore.Qt.Key_Down:
			self.searchEdit.searchForward(self.bpIDE.searchEdit.text(), True)
		elif key == QtCore.Qt.Key_Up:
			self.searchEdit.searchBackward(self.bpIDE.searchEdit.text(), True)
		elif key == QtCore.Qt.Key_Return:
			if self.bpIDE.codeEdit:
				self.replaceAll(self.bpIDE.codeEdit)
			self.hide()
		else:
			super().keyPressEvent(event)
