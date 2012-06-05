from PyQt4 import QtGui, QtCore, uic
from bp.Compiler import *

class BPRunThread(QtCore.QThread, Benchmarkable):
	
	def __init__(self, bpIDE):
		super().__init__(bpIDE)
		Benchmarkable.__init__(self)
		self.bpIDE = bpIDE
		self.codeEdit = None
		self.process = None
		self.finished.connect(self.bpIDE.programExited)
		
	def startWith(self, exe, debugMode = False):
		#self.codeEdit = self.bpIDE.codeEdit
		self.outputCompiler = self.bpIDE.outputCompiler
		self.exe = exe
		self.debugMode = debugMode
		
		self.bpIDE.running += 1
		
		if self.bpIDE.threaded:
			self.start()
		else:
			self.run()
			self.finished.emit()
		
	def sendData(self, data):
		if self.bpIDE.running:
			someBytes = data.encode("utf-8")
			#print("Sending " + str(someBytes))
			
			# FLUSH IS NEEDED HERE!
			self.process.stdin.write(someBytes)
			self.process.stdin.flush()
		
	def run(self):
		if not self.debugMode:
			runFunc = self.outputCompiler.execute
		else:
			runFunc = self.outputCompiler.debug
			
		# Start the process
		self.exitCode = runFunc(
			exe = self.exe,
			fhOut = self.bpIDE.console.output.write,
			fhErr = self.bpIDE.console.output.writeError,
			thread = self,
		)
		
		#self.bpIDE.backgroundCompilerRan = True
