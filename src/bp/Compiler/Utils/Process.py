import subprocess
from PyQt4 import QtGui

def startProcess(cmd, fhOut, fhErr):
	line = ""
	errLine = ""
	proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	
	while 1:
		# Make the GUI feel more responsive
		QtGui.QApplication.instance().processEvents()
		
		combinedLinesStdout = []
		combinedLinesStderr = []
		
		while 1:
			line = proc.stdout.readline()
			if line:
				combinedLinesStdout.append(line.decode("utf-8"))
			else:
				break
			
		while 1:
			errLine = proc.stderr.readline()
			if errLine:
				combinedLinesStderr.append(errLine.decode("utf-8"))
			else:
				break
		
		exitCode = proc.poll()
			
		if (not combinedLinesStdout) and (not combinedLinesStderr) and (exitCode is not None):
			break
		
		if combinedLinesStdout:
			fhOut(''.join(combinedLinesStdout))
		
		if combinedLinesStderr:
			fhErr(''.join(combinedLinesStderr))
