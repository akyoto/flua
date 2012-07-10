from PyQt4 import QtGui, QtCore
from flua.Compiler.Utils import *
import os

class BPMessageView(QtGui.QListWidget):
	
	def __init__(self, parent, bpIDE):
		super().__init__(parent)
		self.ce = parent
		self.bpIDE = bpIDE
		self.setWordWrap(True)
		self.setObjectName("MessageView")
		self.messages = dict()
		self.hide()
		
		self.resetLastException()
		
		#self.setContentsMargins(0, 0, 0, 0)
		#self.setMaximumHeight(0)
		#self.setScrollBarPolicy(QtGui.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.icon = QtGui.QIcon("images/icons/status/dialog-warning.png")
		self.itemClicked.connect(self.goToLineOfItem)
		self.horizontalScrollBar().hide()
		
	def resetLastException(self):
		self.lastLineNumber = -2
		self.lastErrorMessage = ""
		self.lastErrorFilePath = ""
		self.lastException = None
		
	def goToLineOfItem(self, item):
		errorFilePath = item.data(QtCore.Qt.UserRole + 1)
		
		self.clearSelection()
		
		if (not errorFilePath) or (not os.path.isfile(errorFilePath)):
			if self.lastException:
				print("No line information for „%s“" % (self.lastException.__class__))
			return
		
		lineNum = item.data(QtCore.Qt.UserRole + 2)
		if lineNum:
			lineNum = int(lineNum)
		
		if errorFilePath != self.bpIDE.getFilePath():
			self.bpIDE.openFile(errorFilePath)
		
		if lineNum is not None and lineNum != -1:
			self.bpIDE.goToLineEnd(lineNum)
		
	def addMessage(self, msg):
		#newItem = QtGui.QListWidgetItem(self.icon, msg)
		#newItem.setData(QtCore.Qt.UserRole + 1, "")
		#newItem.setData(QtCore.Qt.UserRole + 2, -1)
		#self.addItem(newItem)
		
		#self.updateView()
		self.addLineBasedMessage("", -1, msg)
		
	def addLineBasedMessage(self, errorFilePath, lineNumber, msg):
		awesomeHash = errorFilePath + str(lineNumber) + msg
		if awesomeHash in self.messages:
			return
		
		# Remove error code information from the view
		pos = msg.find("[Error code")
		if pos != -1:
			msg = msg[:pos]
		
		self.messages[awesomeHash] = msg
		
		newItem = QtGui.QListWidgetItem(self.icon, msg)
		
		newItem.setData(QtCore.Qt.UserRole + 1, errorFilePath)
		newItem.setData(QtCore.Qt.UserRole + 2, lineNumber)
		
		info = "<strong>%s</strong><br/>Line [%d]: %s" % (errorFilePath, lineNumber, msg)
		newItem.setToolTip(info)
		#self.setStyleSheet("background")
		#self.setSizeHint(QtCore.QSize(0, 10))
		self.addItem(newItem)
		
		#self.updateView()
		
	def updateViewParser(self):
		# Last parser exception
		ce = self.bpIDE.codeEdit
		
		if ce and ce.updater and ce.updater.lastException:
			self.clear()
			
			e = self.lastException = ce.updater.lastException
			#ce.updater.lastException = None
			lineNumber = e.getLineNumber()
			errorMessage = e.getMsg()
			errorFilePath = e.getFilePath()
			
			if lineNumber != self.lastLineNumber or errorMessage != self.lastErrorMessage or errorFilePath != self.lastErrorFilePath:
				self.addLineBasedMessage(errorFilePath, lineNumber, errorMessage)
				self.lastLineNumber = lineNumber
				self.lastErrorMessage = errorMessage
				self.lastErrorFilePath = errorFilePath
		else:
			if self.lastException:
				wasMyException = isinstance(self.lastException, InputCompilerException)
				
				if wasMyException:
					self.clear()
		
		self.updateView()
		
	def updateViewPostProcessor(self):
		#self.clear()
		if self.lastException:
			wasMyException = isinstance(self.lastException, PostProcessorException)
			
			if wasMyException:
				self.clear()
			else:
				return
		
		# Last post processor exception
		pp = self.ce.postProcessorThread
		if pp and pp.lastException:
			self.clear()
			e = self.lastException = pp.lastException
			pp.lastException = None
			self.addLineBasedMessage(e.getFilePath(), e.getLineNumber(), e.getMsg())
		
		self.updateView()
		
	def updateViewOutputCompiler(self):
		if self.lastException:
			wasMyException = isinstance(self.lastException, OutputCompilerException)
			
			if wasMyException:
				self.clear()
			else:
				return
		#else:
		#	wasOutputCompilerException = False
		
		e = self.lastException = self.bpIDE.outputCompilerThread.lastException
		
		if e:
			#node = e.getLastParsedNode()
			
			self.addLineBasedMessage(e.getFilePath(), e.getLineNumber(), e.getMsg())
			
			if not self.bpIDE.config.developerMode:
				self.bpIDE.consoleDock.hide()
		
		self.updateView()
		
	def clear(self):
		self.resetLastException()
		self.messages = dict()
		super().clear()
		self.hide()
		
	def updateView(self):
		#if self.bpIDE.intelliEnabled:
		
		itemNum = self.count()
		if itemNum:
			#self.adjustSize()#resize(0, 0)
			#self.setMaximumHeight(self.count() * 50)
			
			# To make visual item rect calc all items, "fake" a height of 600 px
			#self.setGeometry(self.x(), self.y(), self.ce.msgViewWidth, 600)
			self.setMaximumHeight(600)
			
			# Item size
			maxHeight = 2
			for i in range(itemNum):
				maxHeight += self.visualItemRect(self.item(i)).height() + 1
			
			#maxHeight = max(92, maxHeight)
			
			# Resize bubble
			margin = 7 + 10
			b = self.ce.bubble
			
			# Resize myself
			self.setGeometry(self.x(), self.y(), self.width(), maxHeight)
			
			if self.isHidden() and len(self.ce.updateQueue) == 0:
				self.show()
				
				newOffY = self.height() + margin * 2
				if newOffY > b.y() or b.y() - newOffY > self.ce.bubbleMinMovePx:
					b.setGeometry(b.x(), newOffY, b.width(), b.height())
		else:
			if self.isVisible():
				self.hide()
				#b.setGeometry(b.x(), 7, b.width(), b.height())
				
