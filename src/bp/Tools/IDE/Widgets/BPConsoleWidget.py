from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QObject
from bp.Compiler.Config import *
import sys

class BPLogWidget(QtGui.QPlainTextEdit):
	
	def __init__(self, parent):
		super().__init__(parent)
		
		self.signal = QtCore.SIGNAL("newDataAvailable(QString)")
		self.errorSignal = QtCore.SIGNAL("newErrorAvailable(QString)")
		self.flushSignal = QtCore.SIGNAL("flushRequested()")
		
		self.connect(self, self.signal, self.onNewData)
		self.connect(self, self.errorSignal, self.onNewError)
		self.connect(self, self.flushSignal, self.flushRequested)
		
	def onNewData(self, stri):
		# TODO: Scroll
		cursor = self.textCursor()
		cursor.movePosition(QtGui.QTextCursor.End)
		cursor.insertText(stri)
		self.setTextCursor(cursor)
		self.ensureCursorVisible()
		
	def onNewError(self, stri):
		# TODO: Scroll + red color
		cursor = self.textCursor()
		cursor.movePosition(QtGui.QTextCursor.End)
		cursor.insertText(stri)
		self.setTextCursor(cursor)
		self.ensureCursorVisible()
		
	def flushRequested(self):
		# TODO: ...
		self.ensureCursorVisible()
		
	def flush(self):
		self.emit(self.flushSignal)
		
	def write(self, stri):
		self.emit(self.signal, stri)
		
	def writeError(self, stri):
		self.emit(self.signal, stri)

class BPConsoleWidget(QtGui.QStackedWidget):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.bpIDE = parent
		self.realStdout = sys.stdout
		self.realStderr = sys.stderr
		
		if os.name == "nt":
			self.setMinimumWidth(460)
		else:
			self.setMinimumWidth(390)
		
		#vBox = QtGui.QVBoxLayout(self)
		
		# TODO: Remove font
		#self.setFont(self.bpIDE.config.monospaceFont)
		
		for i in range(3):
			log = BPLogWidget(self)
			log.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
			log.setReadOnly(True)
			self.addWidget(log)
		
		self.log = self.widget(0)
		self.compilerLog = self.widget(1)
		self.outputLog = self.widget(2)
		
		self.log.setObjectName("Log")
		self.compilerLog.setObjectName("CompilerLog")
		self.outputLog.setObjectName("OutputLog")
		
		# Linux / g++ info
		if 0:
			gccVersionCheck = [
				getGCCCompilerName(),
				"--version"
			]
			
			linuxCheck = [
				"uname",
				"-a"
			]
			
			if os.name == "posix":
				startProcess(linuxCheck, self.log.write, self.log.write)
				self.log.write("\n")
				startProcess(gccVersionCheck, self.log.write, self.log.write)
		
		# Intercept sys.stdout and sys.stderr
		self.watch(self.log)
		
		#vBox.addWidget(self.log)
		
		#self.setLayout(vBox)
		
	def clearLog(self):
		self.log.setPlainText("")
		
	def watch(self, newLog):
		sys.stdout = sys.stderr = newLog
		
	def detach(self):
		sys.stdout = self.realStdout
		sys.stderr = self.realStderr
		
	def updateView(self):
		pass
