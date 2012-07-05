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
			if text == ".*":
				return
			
			text = QtCore.QRegExp(text)
			
		# Start of document
		if self.searchEdit.usingSelection:
			#cursor.setPosition(cursor.selectionStart() - 1)
			endSearch = cursor.selectionEnd()
			startSearch = cursor.selectionStart()
			cursor.setPosition(startSearch)
			#print(" START: " + str(startSearch))
			#print(" END: " + str(endSearch))
		else:
			cursor.movePosition(QtGui.QTextCursor.Start)
			endSearch = -1
		
		newText = self.text()
		newTextLen = len(newText)
		
		cursor.beginEditBlock()
		
		# Begin replacing
		while 1:
			nextResult = qdoc.find(text, cursor, findFlags)
			
			if nextResult.position() == -1 or (endSearch != -1 and nextResult.position() > endSearch):
				#print(nextResult.position())
				break
			
			oldText = nextResult.selectedText()
			nextResult.removeSelectedText()
			nextResult.insertText(newText)
			
			if endSearch != -1:
				endSearch += newTextLen - len(oldText)
			
			cursor.setPosition(nextResult.position())
		
		cursor.endEditBlock()
		
	def keyPressEvent(self, event):
		key = event.key()
		if key == QtCore.Qt.Key_Escape:
			self.setText("")
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
