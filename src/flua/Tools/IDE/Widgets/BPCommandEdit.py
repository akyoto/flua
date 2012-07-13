from PyQt4 import QtGui, QtCore

class BPCommandEdit(QtGui.QLineEdit):
	
	def __init__(self, parent = None):
		super().__init__(parent)
		self.bpIDE = parent
		self.lastCmd = ""
		
	def keyPressEvent(self, event):
		key = event.key()
		
		if key == QtCore.Qt.Key_Escape:
			self.leave()
		elif key == QtCore.Qt.Key_Return:
			self.execCommand(self.text())
			self.leave()
		else:
			super().keyPressEvent(event)
		
	def focusNormal(self):
		self.setText("")
		self.setFocus()
		
	def leave(self):
		if self.bpIDE.codeEdit:
			self.bpIDE.codeEdit.setFocus()
			self.bpIDE.searchEdit.show()
			self.hide()
		
	def interpretToken(self, token, cursor):
		if token == "d":
			if cursor.hasSelection():
				cursor.removeSelectedText()
			else:
				cursor.deleteChar()
		elif token == "w":
			cursor.select(QtGui.QTextCursor.WordUnderCursor)
		elif token == "l":
			cursor.select(QtGui.QTextCursor.BlockUnderCursor)
		elif token == "u":
			self.bpIDE.undoLastAction()
		elif token == "r":
			self.bpIDE.redoLastAction()
		else:
			print("Could not interpret token „%s“" % token)
			# TODO: ...
			#cmdPath = "%sCommands/%s" % (getIDERoot(), cmd)
			
			#if os.path.exists(cmdPath):
			#	script = readFile(cmdPath)
			#	
			#	for x in script:
			#		print(x)
		
	def execSingleCommand(self, cmd, cursor):
		cmdLen = len(cmd)
		
		if cmdLen == 1:
			self.interpretToken(cmd, cursor)
		elif cmdLen == 2:
			token = cmd[0]
			selector = cmd[1]
			
			if selector.isdigit():
				for n in range(int(selector)):
					self.interpretToken(token, cursor)
			else:
				self.interpretToken(selector, cursor)
				self.interpretToken(token, cursor)
		elif cmdLen >= 3:
			token = cmd[0]
			selector = cmd[1]
			
			if selector.isdigit():
				times = int(cmd[1:])
				selector = ""
			else:
				times = int(cmd[2:])
			
			for n in range(times):
				if selector:
					self.interpretToken(selector, cursor)
				
				self.interpretToken(token, cursor)
				
				if selector and times > 1:
					if selector == "w":
						cursor.movePosition(QtGui.QTextCursor.NextWord)
					elif selector == "l":
						cursor.movePosition(QtGui.QTextCursor.NextBlock)
		
	def execCommand(self, cmd):
		if not self.bpIDE.codeEdit:
			return
		
		if cmd == ".":
			cmd = self.lastCmd
		
		self.lastCmd = cmd
		
		#print("Executing command: %s" % cmd)
		cursor = self.bpIDE.codeEdit.textCursor()
		
		cursor.beginEditBlock()
		
		# Go!
		pos = -1
		while cmd:
			pos = cmd.find(";", pos + 1)
			
			if pos != -1:
				self.execSingleCommand(cmd[:pos], cursor)
				cmd = cmd[pos+1:]
			else:
				self.execSingleCommand(cmd, cursor)
				break
			
		cursor.endEditBlock()
			
		self.bpIDE.codeEdit.setTextCursor(cursor)
