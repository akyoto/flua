from PyQt4 import QtGui, QtCore, QtNetwork
import random
import os

# Adapted from: http://pastebin.com/HXebdsGW
class BPChatWidget(QtGui.QWidget):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.bpIDE = parent
		self.host = "irc.freenode.net"
		self.port = 6667
		self.channel = "#blitzprog"
		
		if os.path.exists("/home/"):
			rootPath = "/home/"
			for root, subFolders, files in os.walk(rootPath):
				self.nickName = ";".join(subFolders)
				break
		else:
			self.nickName = "Guest" + str(random.randint(1, 1000)) + "_" + self.bpIDE.config.gitHubName
		self.socket = None
		
		# TODO: Remove font
		self.setFont(self.bpIDE.config.standardFont)
		
		if not self.bpIDE.developerFlagMain:
			self.connectToServer()
		
	def connectToServer(self):
		self.socket = QtNetwork.QTcpSocket(self)
		self.socket.connectToHost(self.host, self.port)
		
		self.socket.write("NICK %s \r\n" % self.nickName)
		self.socket.write("USER %s %s %s :%s BOT \r\n" % (self.nickName, self.host, self.nickName, self.nickName))
		self.socket.write("JOIN %s \r\n" % self.channel)
		
	def updateView(self):
		pass
