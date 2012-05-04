from PyQt4 import QtGui, QtCore
import codecs
import os

class BPScribbleWidget(QtGui.QPlainTextEdit):
	
	def __init__(self, parent, filePath):
		super().__init__(parent)
		self.bpIDE = parent
		self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
		self.setFont(QtGui.QFont("monospace", 9))
		self.filePath = filePath
		self.loadScribble()
		
	def loadScribble(self):
		if os.path.isfile(self.filePath):
			with codecs.open(self.filePath, "r", "utf-8") as inStream:
				scribbleText = inStream.read()
			
			self.setPlainText(scribbleText)
		
	def saveScribble(self):
		scribbleText = self.toPlainText()
		
		with codecs.open(self.filePath, "w", encoding="utf-8") as outStream:
			outStream.write(scribbleText)
		
	def updateView(self):
		pass
