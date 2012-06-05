from PyQt4 import QtGui, QtCore
import codecs
import os

class BPScribbleWidget(QtGui.QPlainTextEdit):
	
	def __init__(self, parent, filePath):
		super().__init__(parent)
		self.bpIDE = parent
		self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
		
		# TODO: Remove font
		self.setFont(self.bpIDE.config.standardFont)
		self.filePath = filePath
		self.loadScribble()
		
	def minimumSizeHint(self):
		return QtCore.QSize(400, 200)
		
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
