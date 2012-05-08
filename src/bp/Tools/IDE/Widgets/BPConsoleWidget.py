from PyQt4 import QtGui, QtCore

class BPLogWidget(QtGui.QPlainTextEdit):
	
	def __init__(self, parent):
		super().__init__(parent)

class BPConsoleWidget(QtGui.QStackedWidget):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.bpIDE = parent
		
		#vBox = QtGui.QVBoxLayout(self)
		
		# TODO: Remove font
		self.setFont(self.bpIDE.config.monospaceFont)
		
		for i in range(3):
			log = BPLogWidget(self)
			log.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
			log.setReadOnly(True)
			self.addWidget(log)
		
		#vBox.addWidget(self.log)
		
		#self.setLayout(vBox)
		
	def updateView(self):
		pass
