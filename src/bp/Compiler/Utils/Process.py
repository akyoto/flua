import subprocess
import sys
from PyQt4 import QtGui

def startProcess(cmd, fhOut, fhErr):
	#fhOut = sys.stdout.write
	#fhErr = sys.stderr.write
	line = ""
	errLine = ""
	proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	linesThreshold = 2000
	
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
				if combinedLinesStdoutCount > linesThreshold:
					fhOut(''.join(combinedLinesStdout))
					combinedLinesStdout = []
					combinedLinesStdoutCount = 0
					QtGui.QApplication.instance().processEvents()
			else:
				break
			
		while 1:
			errLine = proc.stderr.readline()
			if errLine:
				combinedLinesStderr.append(errLine.decode("utf-8"))
				combinedLinesStderrCount += 1
				
				# For programs which produce too much output at once
				if combinedLinesStderrCount > linesThreshold:
					fhErr(''.join(combinedLinesStderr))
					combinedLinesStderr = []
					combinedLinesStderrCount = 0
					QtGui.QApplication.instance().processEvents()
			else:
				break
		
		exitCode = proc.poll()
			
		if (not combinedLinesStdoutCount) and (not combinedLinesStderrCount) and (exitCode is not None):
			break
		
		if combinedLinesStdout:
			fhOut(''.join(combinedLinesStdout))
		
		if combinedLinesStderr:
			fhErr(''.join(combinedLinesStderr))
