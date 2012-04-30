from PyQt4 import QtGui, QtCore

class BPDependencyView(QtGui.QPlainTextEdit):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.bpIDE = parent
		self.node = None
		self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
		self.setFont(QtGui.QFont("monospace", 10))

	def setNode(self, newNode):
		self.node = newNode
		
	def getProcessor(self):
		return self.bpIDE.processor
		
	def updateView(self):
		if self.isHidden() and not self.bpIDE.intelliEnabled:
			return
		
		processor = self.getProcessor()
		
		dTree = None
		if processor and self.node in processor.dTreeByNode:
			dTree = processor.dTreeByNode[self.node]
		#elif self.node:
		#	if processor:
		#		self.clear()#No dependency information (%d DTrees available)" % (len(processor.dTreeByNode)))
		#	else:
		#		self.clear()#No dependency information available")
		else:
			self.clear()#No node information")
		
		if dTree:
			self.setPlainText(dTree.getDependencyPreview())
			
		# Toggle visibility
		if self.bpIDE.intelliEnabled:
			lines = self.toPlainText().count("\n")
			if lines <= 1:
				if self.isVisible():
					self.hide()
			else:
				height = (lines + 1) * (self.fontMetrics().lineSpacing() + 3) + 15
				#self.setMaximumHeight(height)
				if height < self.parent().height():
					self.setMinimumHeight(height - 1)
				self.setMaximumHeight(height + 1)
				#self.adjustSize()
				if self.isHidden():
					self.show()
