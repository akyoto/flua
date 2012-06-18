from PyQt4 import QtGui, QtCore, QtNetwork
import random
import os

class BPIRCConnectThread(QtCore.QThread):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.bpIDE = parent
		
		# IRC info
		self.host = "irc.freenode.net"
		self.port = 6667
		self.channel = "#blitzprog"
		
		# OH MY GAWD IT'S MUTABLE STATE
		self.channelJoined = False
		
		if os.name == "nt":
			self.nickName = os.environ.get("USERNAME")
		else:
			import pwd
			self.nickName = pwd.getpwuid(os.getuid())[0]
			if not self.nickName:
				self.nickName = os.getenv("USERNAME")
		
		self.nickName = self.nickName.replace(" ", "")
		if not self.nickName:
			self.nickName = "Guest" + str(random.randint(1, 1000)) + "_" + self.bpIDE.config.gitHubName
		
		self.socket = None
	
	def connectToHost(self):
		self.socket.connectToHost(self.host, self.port)
		
	def identifyUser(self):
		self.socket.write("NICK %s \r\n" % self.nickName)
		self.socket.write("USER %s %s %s :%s BOT \r\n" % (self.nickName, self.host, self.nickName, self.nickName))
		self.socket.flush()
		
	def joinChannel(self):
		self.socket.write("JOIN %s \r\n" % self.channel)
		self.socket.flush()
		self.channelJoined = True
	
	def run(self):
		self.connectToHost()
		self.identifyUser()
		
		line = ""
		while 1:
			while self.socket.isReadable():
				byteArray = self.socket.readLine()
				
				if byteArray:
					line = str(byteArray, encoding='utf-8')
					self.bpIDE.console.irc.write(line)
					
					# TODO: Replace this to avoid bugs
					#if line.find("433") != -1:
					#	self.nickName = "bp_" + self.nickName
					#	self.socket.write("/nick %s\r\n" % self.nickName)
					#	self.socket.flush()
					
					if line.find("End of /MOTD") != -1 and not self.channelJoined:
						self.joinChannel()
				
				QtCore.QThread.msleep(1)
			
			QtCore.QThread.msleep(100)

# Adapted from: http://pastebin.com/HXebdsGW
class BPChatWidget(QtGui.QWidget):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.bpIDE = parent
		self.socket = QtNetwork.QTcpSocket(self)
		
		# TODO: Remove font
		self.setFont(self.bpIDE.config.standardFont)
		
		if 0:#not self.bpIDE.developerFlagMain:
			self.connectThread = BPIRCConnectThread(self.bpIDE)
			self.connectThread.socket = self.socket
			self.connectThread.start()
		
	def updateView(self):
		pass
