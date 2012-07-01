import subprocess
import sys
import time
from threading import Thread
from queue import Queue, Empty
from PyQt4 import QtGui
from flua.Compiler.Config import *

ON_POSIX = 'posix' in sys.builtin_module_names

def startProcess(cmd, fhOut, fhErr, thread = None, bytewise = False):
	#fhOut = sys.stdout.write
	#fhErr = sys.stderr.write
	
	envi = None
	#if os.name == "nt":
	if not getDLLDir() in os.environ["PATH"]:
		os.environ["PATH"] = getDLLDir() + ";" + os.environ["PATH"]
	
	if os.name == "nt":
		os.environ["PATH"] = getMinGWDir() + ";" + os.environ["PATH"]
	
	proc = subprocess.Popen(
		cmd,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		stdin = subprocess.PIPE,
		env = os.environ,
		#bufsize = 1,
		close_fds = ON_POSIX
	)
	
	if thread:
		thread.process = proc
		
		# Call programStarted
		thread.programStarted()
	
	if bytewise:
		return handleProcessOutputBytewise(proc, fhOut, fhErr)
	else:
		return handleProcessOutputLinewise(proc, fhOut, fhErr)
	
def handleProcessOutputLinewise(proc, fhOut, fhErr):
	linesThreshold = 2000
	timeThreshold = 1.0 / 25 # seconds
	lastWriteTime = 0
	lastErrWriteTime = 0
	
	while 1:
		# Make the GUI feel more responsive
		#QtGui.QApplication.instance().processEvents()

		combinedLinesStdout = []
		combinedLinesStderr = []
		combinedLinesStdoutCount = 0
		combinedLinesStderrCount = 0

		while 1:
			QtGui.QApplication.instance().processEvents()
			
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
			QtGui.QApplication.instance().processEvents()
			
			errLine = proc.stderr.readline()
			if errLine:
				try:
					decoded = errLine.decode("utf-8")
				except:
					decoded = str(errLine).replace("\xbb", '"').replace("\xba", '"')
				
				combinedLinesStderr.append(decoded)
				combinedLinesStderrCount += 1

				# For programs which produce too much output at once
				if combinedLinesStderrCount > linesThreshold or time.time() - lastErrWriteTime > timeThreshold:
					fhErr(''.join(combinedLinesStderr))
					combinedLinesStderr = []
					combinedLinesStderrCount = 0
					QtGui.QApplication.instance().processEvents()
					lastErrWriteTime = time.time()
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
		lastErrWriteTime = time.time()
	
def enqueue_output(out, queue):
	line = bytearray()
	while 1:
		b = out.read(1)
		
		if not b:
			break
		
		line += b
		try:
			decoded = line.decode("utf-8")
		except:
			continue
		else:
			queue.put(decoded)
			del line[:]
	
	#for line in iter(line, b''):
	#	queue.put(line)
	
	if out:
		out.close()
	
def handleProcessOutputBytewise(proc, fhOut, fhErr):
	q = Queue()
	errQ = Queue()
	
	t = Thread(target=enqueue_output, args=(proc.stdout, q))
	t.daemon = True # thread dies with the program
	t.start()
	
	tErr = Thread(target=enqueue_output, args=(proc.stderr, errQ))
	tErr.daemon = True # thread dies with the program
	tErr.start()
	
	writeEveryXSecs = 1.0 / 10
	lastWrite = time.time()
	
	chars = []
	errChars = []
	
	while 1:
		try:
			char = q.get(timeout=.1)
		except Empty:
			pass
		else: # got line
			chars.append(char)
		
		if not errQ.empty():
			try:
				while 1:
					errChar = errQ.get_nowait()
					errChars.append(errChar)
			except Empty:
				pass
		
		if time.time() - lastWrite > writeEveryXSecs:
			if chars:
				fhOut(''.join(chars))
				del chars[:]
				
			if errChars:
				fhErr(''.join(errChars))
				del errChars[:]
			
			QtGui.QApplication.instance().processEvents()
			
			# Process terminated?
			exitCode = proc.poll()
			
			if (exitCode is not None) and (not t.is_alive()) and (not tErr.is_alive()) and q.empty() and errQ.empty():
				return exitCode
