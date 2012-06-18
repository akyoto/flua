from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QObject
from bp.Compiler.Config import *
from bp.Compiler.Utils.Debug import *
from bp.Tools.IDE.Syntax import *
import sys

class BPLogWidget(QtGui.QPlainTextEdit):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.bpIDE = parent.bpIDE
		self.highlighter = CLogHighlighter(self.document(), self.bpIDE)
		self.inputEnabled = False
		
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
		
		#self.bpIDE.console.realStdout.write(stri)
		
		if "Traceback (most recent call last):" in stri:
			self.bpIDE.consoleDock.setMinimumHeight(200)
			self.bpIDE.consoleDock.show()
		
	def onNewError(self, stri):
		# TODO: Scroll + red color
		cursor = self.textCursor()
		cursor.movePosition(QtGui.QTextCursor.End)
		cursor.insertText(stri)
		self.setTextCursor(cursor)
		self.ensureCursorVisible()
		
		# Visible on error
		self.bpIDE.consoleDock.setMinimumHeight(200)
		self.bpIDE.consoleDock.show()
		
	def flushRequested(self):
		# TODO: ...
		self.ensureCursorVisible()
		
	def flush(self):
		self.emit(self.flushSignal)
		
	def write(self, stri):
		self.emit(self.signal, stri)
		
	def writeError(self, stri):
		self.emit(self.errorSignal, stri)
		
	def enableInput(self):
		self.inputEnabled = True
		
	def keyPressEvent(self, event):
		if self.inputEnabled:
			data = event.text()
			if data == '\r':
				self.bpIDE.sendToRunningProgram('\n')
			else:
				self.bpIDE.sendToRunningProgram(data)
		super().keyPressEvent(event)

class BPConsoleWidget(QtGui.QTabWidget):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.bpIDE = parent
		self.realStdout = sys.stdout
		self.realStderr = sys.stderr
		self.setObjectName("BPConsoleWidget")
		self.setDocumentMode(True)
		self.names = ["Log", "Compiler", "Output"]
		
		#if os.name == "nt":
		#self.setMinimumWidth(450)
		#else:
		#	self.setMinimumWidth(390)
		
		#vBox = QtGui.QVBoxLayout(self)
		
		# TODO: Remove font
		#self.setFont(self.bpIDE.config.monospaceFont)
		
		for i in range(len(self.names)):
			log = BPLogWidget(self)
			log.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
			
			if not i == 2:
				log.setReadOnly(True)
			else:
				log.enableInput()
			
			log.setObjectName(self.names[i])
			self.addTab(log, self.names[i])
		
		self.log = self.widget(0)
		#self.irc = self.widget(1)
		self.compiler = self.widget(1)
		self.output = self.widget(2)
		
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
		
		#vBox.addWidget(self.log)
		
		#self.setLayout(vBox)
		
	def minimumSizeHint(self):
		return QtCore.QSize(450, 232)
		
	def activate(self, logName):
		for i in range(len(self.names)):
			if self.names[i] == logName:
				self.setCurrentIndex(i)
				return
		
	def getCurrentLog(self):
		return self.widget(self.currentIndex())
		
	def watch(self, newLog):
		sys.stdout = sys.stderr = newLog
		
	def detach(self):
		sys.stdout = self.realStdout
		sys.stderr = self.realStderr
		
	def updateView(self):
		pass
