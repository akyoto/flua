import subprocess
import sys
import time
from PyQt4 import QtGui

def startProcess(cmd, fhOut, fhErr):
	#fhOut = sys.stdout.write
	#fhErr = sys.stderr.write
	line = ""
	errLine = ""
	proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	linesThreshold = 2000
	timeThreshold = 1.0 / 25 # seconds
	lastWriteTime = 0
	
	while 1:
		# Make the GUI feel more responsive
		QtGui.QApplication.instance().processEvents()
		
		combinedLinesStdout = []
		combinedLinesStderr = []
		combinedLinesStdoutCount = 0
		combinedLinesStderrCount = 0
		
		while 1:
			line = proc.stdout.readline()
			if line:
				combinedLinesStdout.append(line.decode("utf-8"))
				combinedLinesStdoutCount += 1
				
				# For programs which produce too much output at once
				if combinedLinesStdoutCount > linesThreshold or time.time() - lastWriteTime > timeThreshold:
					fhOut(''.join(combinedLinesStdout))
					combinedLinesStdout = []
					combinedLinesStdoutCount = 0
					QtGui.QApplication.instance().processEvents()
					lastWriteTime = time.time()
			else:
				break
			
		while 1:
			errLine = proc.stderr.readline()
			if errLine:
				combinedLinesStderr.append(errLine.decode("utf-8"))
				combinedLinesStderrCount += 1
				
				# For programs which produce too much output at once
				if combinedLinesStderrCount > linesThreshold or time.time() - lastWriteTime > timeThreshold:
					fhErr(''.join(combinedLinesStderr))
					combinedLinesStderr = []
					combinedLinesStderrCount = 0
					QtGui.QApplication.instance().processEvents()
					lastWriteTime = time.time()
			else:
				break
		
		exitCode = proc.poll()
		QtGui.QApplication.instance().processEvents()
		
		if (not combinedLinesStdoutCount) and (not combinedLinesStderrCount) and (exitCode is not None):
			return exitCode
		
		if combinedLinesStdout:
			fhOut(''.join(combinedLinesStdout))
		
		if combinedLinesStderr:
			fhErr(''.join(combinedLinesStderr))
			
		lastWriteTime = time.time()
