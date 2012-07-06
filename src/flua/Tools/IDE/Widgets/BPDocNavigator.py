from PyQt4 import QtGui, QtCore
from flua.Compiler.Utils import *
import os

class BPDocNavigator(QtGui.QWidget):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.codeEdit = parent
		self.bpIDE = parent.bpIDE
		self.setObjectName("DocNavigator")
		
		self.customWidth = 160
		self.customHeight = 48
		
		self.previousFile = ""
		self.nextFile = ""
		
		# Get previous and next file
		filePath = self.codeEdit.getFilePath()
		
		parts = filePath.split("/")
		
		docNumber = int(parts[-1][:2])
		
		previousNumber = str(docNumber - 1)
		nextNumber = str(docNumber + 1)
		
		if len(previousNumber) == 1:
			previousNumber = "0" + previousNumber
		
		if len(nextNumber) == 1:
			nextNumber = "0" + nextNumber
		
		fileDir = extractDir(filePath)
		for root, subFolders, files in os.walk(fileDir):
			if root == fileDir:
				for x in files:
					if x.startswith(previousNumber):
						self.previousFile = fixPath(fileDir + x)
					elif x.startswith(nextNumber):
						self.nextFile = fixPath(fileDir + x)
		
		# Create the buttons
		self.group = QtGui.QButtonGroup(self)
		
		hBox = QtGui.QHBoxLayout()
		for i in range(2):
			if i == 0 and not self.previousFile:
				continue
			elif i == 1 and not self.nextFile:
				continue
			
			button = QtGui.QPushButton(["«", "»"][i])
			#button.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
			#button.setSize(96, 48)
			button.setToolTip([stripAll(self.previousFile), stripAll(self.nextFile)][i])
			hBox.addWidget(button)
			self.group.addButton(button, i)
			button.clicked.connect([self.backward, self.forward][i])
		
		self.setLayout(hBox)
		
	def backward(self):
		self.bpIDE.closeCurrentTab()
		self.bpIDE.openFile(self.previousFile)
		
	def forward(self):
		self.bpIDE.closeCurrentTab()
		self.bpIDE.openFile(self.nextFile)
