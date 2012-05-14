from PyQt4 import QtGui, QtCore, uic
from bp.Compiler import *
from bp.Tools.IDE.Utils import *

class BPGitThread(QtCore.QThread):
	
	def __init__(self, bpIDE):
		super().__init__(bpIDE)
		self.bpIDE = bpIDE
		self.logWidget = None
		self.finished.connect(self.bpIDE.gitPullFinished)
		self.finished.connect(self.gitCmdFinished)
		self.cmd = None
		
	def gitCmdFinished(self):
		if self.logWidget:
			vScrollBar = self.logWidget.verticalScrollBar()
			vScrollBar.triggerAction(QtGui.QScrollBar.SliderToMinimum)
		
	def startCmd(self, cmd, logWidget = None):
		if self.isRunning():
			return
		
		self.cmd = cmd
		self.logWidget = logWidget
		self.start()
		
	def run(self):
		try:
			if self.logWidget:
				fhOut = self.logWidget.write
				fhErr = self.logWidget.writeError
			else:
				fhOut = self.bpIDE.console.realStdout.write
				fhErr = self.bpIDE.console.realStderr.write
			startProcess(self.cmd, fhOut, fhErr)
		except Exception as e:
			errorMessage = str(e)
			print(errorMessage)
