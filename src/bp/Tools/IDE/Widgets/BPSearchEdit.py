from PyQt4 import QtGui, QtCore
from bp.Tools.IDE.Widgets.BPReplaceEdit import *

class BPSearchEdit(QtGui.QLineEdit):

	def __init__(self, parent = None):
		super().__init__(parent)
		self.bpIDE = parent
		self.regExSearch = False
		self.setPlaceholderText("Ctrl + F (search), Arrow Down (next result), Arrow Up (previous result), Esc (leave search)")
		self.textChanged.connect(self.searchForward)
		
	def focusNormal(self):
		self.regExSearch = False
		self.selectAll()
		self.setFocus()
		
	def focusRegex(self):
		self.focusNormal()
		self.regExSearch = True
		
	def keyPressEvent(self, event):
		key = event.key()
		if key == QtCore.Qt.Key_Escape:
			if self.bpIDE.codeEdit:
				#self.bpIDE.codeEdit.setTextCursor(self.bpIDE.codeEdit.textCursor())
				self.bpIDE.codeEdit.setFocus()
		elif key == QtCore.Qt.Key_Down:
			self.searchForward(self.text(), True)
		elif key == QtCore.Qt.Key_Up:
			self.searchBackward(self.text(), True)
		else:
			super().keyPressEvent(event)
		
	def searchForward(self, text, nextResult = False, findFlags = None):
		ce = self.bpIDE.codeEdit
		if not ce:
			return
		
		if not findFlags:
			findFlags = QtGui.QTextDocument.FindFlags()
		
		qdoc = ce.qdoc
		cursor = ce.textCursor()
		replaceEdit = self.bpIDE.replaceEdit
		
		if not text:
			cursor.clearSelection()
			ce.setTextCursor(cursor)
			replaceEdit.hide()
			return
		
		if not self.regExSearch:
			pyCount = ce.toPlainText().count(text)
			
			if pyCount == 0:
				replaceEdit.hide()
				return
			else:
				if pyCount == 1:
					replaceEdit.setPlaceholderText("Replace %d occurence with..." % pyCount)
				else:
					replaceEdit.setPlaceholderText("Replace %d occurences with..." % pyCount)
		else:
			replaceEdit.setPlaceholderText("Replace with...")
		
		replaceEdit.show()
		
		#cursor.clearSelection()
		if not nextResult:
			cursor.movePosition(QtGui.QTextCursor.PreviousCharacter)
		
		findFlags |= QtGui.QTextDocument.FindCaseSensitively
		
		if self.regExSearch:
			nextResult = qdoc.find(QtCore.QRegExp(text), cursor, findFlags)
		else:
			nextResult = qdoc.find(text, cursor, findFlags)
		
		if nextResult.position() != -1:
			# Found
			ce.setTextCursor(nextResult)
		else:
			# Start search again from the start of the document
			if findFlags & QtGui.QTextDocument.FindBackward:
				cursor.movePosition(QtGui.QTextCursor.End)
			else:
				cursor.movePosition(QtGui.QTextCursor.Start)
			
			if self.regExSearch:
				nextResult = qdoc.find(QtCore.QRegExp(text), cursor, findFlags)
			else:
				nextResult = qdoc.find(text, cursor, findFlags)
				
			if nextResult.position() != -1:
				ce.setTextCursor(nextResult)
			
	def searchBackward(self, text, nextResult = False):
		self.searchForward(text, nextResult, QtGui.QTextDocument.FindBackward)

