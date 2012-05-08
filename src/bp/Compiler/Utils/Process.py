import subprocess
from PyQt4 import QtGui

def startProcess(cmd, fhOut, fhErr):
	proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	while 1:
		# Make the GUI feel more responsive
		QtGui.QApplication.instance().processEvents()
		
		line = proc.stdout.readline()
		errLine = proc.stderr.readline()
		exitCode = proc.poll()
		if (not line) and (not errLine) and (exitCode is not None):
			break
		
		if line:
			fhOut(line.decode("utf-8"))
		
		if errLine:
			fhErr(errLine.decode("utf-8"))
