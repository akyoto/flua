from PyQt4 import QtGui, QtCore, uic
from bp.Tools.IDE.Syntax.BPCSyntax import *
from bp.Compiler import *

class BPCodeEdit(QtGui.QTextEdit):
	
	def __init__(self, parent = None):
		super(BPCodeEdit, self).__init__(parent)
		self.highlighter = BPCHighlighter(self.document())
		self.setFont(QtGui.QFont("monospace", 10))
		self.setTabStopWidth(4 * 8)
		self.setLineWrapMode(QtGui.QTextEdit.NoWrap)
		self.converter = None
		self.lines = []
		
	def setXML(self, xmlCode):
		self.doc = parseString(xmlCode.encode( "utf-8" ))
		self.root = self.doc.documentElement
		codeNode = getElementByTagName(self.root, "code")
		
		self.converter = LineToNodeConverter()
		bpcCode = nodeToBPC(self.root, 0, self.converter)
		self.lines = bpcCode.split("\n")
		
		# Remove two empty lines
		if 0:
			offset = 0
			lastLineEmpty = False
			for index in range(0, len(self.lines)):
				i = index + offset
				if i < len(self.lines):
					line = self.lines[i]
					if line.strip() == "":
						if lastLineEmpty:
							self.removeLineNumber(i)
							offset -= 1
						lastLineEmpty = True
					else:
						lastLineEmpty = False
				else:
					break
		
		self.setText("\n".join(self.lines))
		
	def removeLineNumber(self, index):
		# TODO: Fix index by +1 -1
		self.lines = self.lines[:index-1] + self.lines[index:]
		self.converter.lineToNode = self.converter.lineToNode[:index-1] + self.converter.lineToNode[index:]