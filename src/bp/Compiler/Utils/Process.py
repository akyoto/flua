import subprocess
import sys
import time
from threading import Thread
from queue import Queue, Empty
from PyQt4 import QtGui
from bp.Compiler.Config import *

ON_POSIX = 'posix' in sys.builtin_module_names

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

def startProcess(cmd, fhOut, fhErr, thread = None):
	#fhOut = sys.stdout.write
	#fhErr = sys.stderr.write
	
	envi = None
	if os.name == "nt":
		envi = {
			"PATH" : getDLLDir()
		}
	
	proc = subprocess.Popen(
		cmd,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE,
		stdin = subprocess.PIPE,
		env = envi,
		bufsize = 1,
		close_fds = ON_POSIX
	)
	
	if thread:
		thread.process = proc
	
	q = Queue()
	errQ = Queue()
	
	t = Thread(target=enqueue_output, args=(proc.stdout, q))
	t.daemon = True # thread dies with the program
	t.start()
	
	tErr = Thread(target=enqueue_output, args=(proc.stderr, errQ))
	tErr.daemon = True # thread dies with the program
	tErr.start()
	
	writeEveryXSecs = 1.0 / 25
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

#def disabled():
	#timeThreshold = 1.0 / 10 # seconds
	#start = 0
	
	#line = bytearray()
	#lineError = bytearray()
	#count = 0
	
	#while 1:
		## Make the GUI feel more responsive
		#QtGui.QApplication.instance().processEvents()
		
		#exitByTimeout = False
		
		## Stdout
		#start = time.time()
		#while 1:
			#byte = proc.stdout.read(1)
			
			#if not byte:
				#break
				
			#line += byte
			#try:
				#fhOut(line.decode("utf-8"))
				#del line[:]
				
				#if time.time() - start > timeThreshold:
					#exitByTimeout = True
					#break
			#except:
				#continue
		
		#QtGui.QApplication.instance().processEvents()
		
		## Stderr
		#start = time.time()
		#while 1:
			#byte = proc.stderr.read(1)
			
			#if not byte:
				#break
				
			#lineError += byte
			#try:
				#fhErr(lineError.decode("utf-8"))
				#del lineError[:]
				
				#if time.time() - start > timeThreshold:
					#exitByTimeout = True
					#break
			#except:
				#continue
		#QtGui.QApplication.instance().processEvents()
		
		## Process terminated?
		#exitCode = proc.poll()
		
		#if (exitCode is not None) and (not exitByTimeout):
			#return exitCode
