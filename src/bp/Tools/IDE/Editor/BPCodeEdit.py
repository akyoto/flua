from PyQt4 import QtGui, QtCore, uic
from bp.Tools.IDE.Syntax.BPCSyntax import *
from bp.Compiler import *

class BPLineInformation(QtGui.QTextBlockUserData):
	
	def __init__(self, xmlNode):
		super().__init__()
		self.node = xmlNode
		self.edited = False

class BPCodeEdit(QtGui.QPlainTextEdit):
	
	def __init__(self, parent = None):
		super().__init__(parent)
		self.qdoc = self.document()
		self.highlighter = BPCHighlighter(self.qdoc)
		self.setFont(QtGui.QFont("monospace", 10))
		self.setTabStopWidth(4 * 8)
		self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
		#self.textChanged.connect(self.onTextChange)
		self.qdoc.contentsChange.connect(self.onTextChange)
		self.converter = None
		self.lines = []
		
	def onTextChange(self, position, charsRemoved, charsAdded):
		blockStart = self.qdoc.findBlock(position)
		blockEnd = self.qdoc.findBlock(position + charsAdded)
		for i in range(blockStart.blockNumber(), blockEnd.blockNumber() + 1):
			#print("Update user data for line: " + str(block.text()))
			block = self.qdoc.findBlockByNumber(i)
			lineInfo = block.userData()
			if lineInfo:
				lineInfo.edited = True
		#print(blockStart.blockNumber(), "|", blockEnd.blockNumber(), "|", position, charsAdded, charsRemoved)
		
	def getLineIndex(self):
		return self.textCursor().blockNumber()
		
	def getLineNumber(self):
		return self.getLineIndex() + 1
		
	def getNodeByLineIndex(self, lineIndex):
		lineInfo = self.qdoc.findBlockByNumber(lineIndex).userData()
		if lineInfo:
			if lineInfo.edited == False:
				return lineInfo.node
		
		return None
		
	def setXML(self, xmlCode):
		self.doc = parseString(xmlCode.encode( "utf-8" ))
		self.root = self.doc.documentElement
		codeNode = getElementByTagName(self.root, "code")
		
		self.converter = LineToNodeConverter()
		bpcCode = nodeToBPC(self.root, 0, self.converter)
		self.lines = bpcCode.split("\n")
		
		# Remove two empty lines
		#if 0:
			#offset = 0
			#lastLineEmpty = False
			#for index in range(0, len(self.lines)):
				#i = index + offset
				#if i < len(self.lines):
					#line = self.lines[i]
					#if line.strip() == "":
						#if lastLineEmpty:
							#self.removeLineNumber(i)
							#offset -= 1
						#lastLineEmpty = True
					#else:
						#lastLineEmpty = False
				#else:
					#break
		
		self.setPlainText("\n".join(self.lines))
		for i in range(0, len(self.lines) - 1):
			userData = BPLineInformation(self.converter.lineToNode[i])
			self.qdoc.findBlockByNumber(i).setUserData(userData)
		
	def removeLineNumber(self, index):
		# TODO: Fix index by +1 -1
		self.lines = self.lines[:index-1] + self.lines[index:]
		self.converter.lineToNode = self.converter.lineToNode[:index-1] + self.converter.lineToNode[index:]
