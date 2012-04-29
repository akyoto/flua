from PyQt4 import QtGui, QtCore, uic
from bp.Tools.IDE.Syntax.BPCSyntax import *
from bp.Compiler import *

class BPLineInformation(QtGui.QTextBlockUserData):
	
	def __init__(self, xmlNode, edited = False):
		super().__init__()
		self.node = xmlNode
		self.edited = edited

class BPCodeUpdater(QtCore.QThread):
	
	def __init__(self, codeEdit):
		super().__init__(codeEdit)
		self.codeEdit = codeEdit
		self.bpMainWidget = codeEdit.bpMainWidget
		self.setDocument(codeEdit.qdoc)
		self.bpc = BPCCompiler(getModuleDir())
		self.bpcFile = None
		self.finished.connect(self.codeEdit.compilerFinished)
		
	def setDocument(self, doc):
		self.qdoc = doc
		
	def run(self):
		codeText = self.qdoc.toPlainText()
		#self.bpMainWidget.msgView.clear()
		#self.codeEdit.clearHighlights()
		
		try:
			# TODO: Remove unsafe benchmark
			self.bpMainWidget.startBenchmark("BPCCompiler")
			self.bpcFile = self.bpc.spawnFileCompiler(self.codeEdit.getFilePath(), True, codeText)
			self.bpMainWidget.endBenchmark()
		except InputCompilerException as e:
			lineNumber = e.getLineNumber()
			errorMessage = e.getMsg()
			self.bpMainWidget.msgView.addLineBasedMessage(lineNumber, errorMessage)
			#self.codeEdit.setLineError(lineNumber - 1, errorMessage)
			#self.codeEdit.highlightLine(lineNumber - 1, QtGui.QColor("#ff0000"))
			#print("Error in line %d: %s\n%s" % (lineNumber, e.getLine(), errorMessage))
		
		return
		# Old "update edited only" code
		#block = self.qdoc.begin()
		#end = self.qdoc.end()
		#while block != end:
			#userData = block.userData()
			#if not userData or userData.edited:
				#text = block.text()
				#if text:
					#newNode = self.bpc.processLine(text)
					#if newNode:
						#print(text)
						#print(newNode.toprettyxml())
			
			#block = block.next()

class LineNumberArea(QtGui.QWidget):
	
	def __init__(self, codeEdit):
		super().__init__(codeEdit)
		self.codeEdit = codeEdit
		
	def sizeHint(self):
		return QtCore.QSize(self.codeEdit.getLineNumberAreaWidth(), 0)
		
	def paintEvent(self, event):
		self.codeEdit.lineNumberAreaPaintEvent(event)

class BPCodeEdit(QtGui.QPlainTextEdit):
	
	def __init__(self, bpMainWidget = None):
		super().__init__(bpMainWidget)
		self.bpMainWidget = bpMainWidget
		self.qdoc = self.document()
		self.highlighter = BPCHighlighter(self.qdoc, self.bpMainWidget.getCurrentTheme())
		self.setFont(QtGui.QFont("monospace", 10))
		self.setTabStopWidth(4 * 8)
		self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
		#self.setCurrentCharFormat(self.bpMainWidget.currentTheme["default"])
		#self.textChanged.connect(self.onTextChange)
		self.doc = None
		self.root = None
		self.qdoc.contentsChange.connect(self.onTextChange)
		self.lines = []
		self.updater = None
		self.filePath = ""
		self.lineNumberArea = None
		
		if 0:
			self.initLineNumberArea()
	
	def clearHighlights(self):
		self.setExtraSelections([])
	
	def getCurrentTheme(self):
		return self.bpMainWidget.getCurrentTheme()
	
	def setFilePath(self, filePath):
		self.filePath = filePath
		
	def getFilePath(self):
		return self.filePath
		
	def setLineNode(self, index, newNode):
		block = self.qdoc.findBlockByNumber(index)
		lineInfo = block.userData()
		if lineInfo:
			block.setUserData(BPLineInformation(newNode, False))
	
	def setLineEdited(self, index, edited):
		block = self.qdoc.findBlockByNumber(index)
		lineInfo = block.userData()
		if lineInfo:
			block.setUserData(BPLineInformation(lineInfo.node, True))
		
	def onTextChange(self, position, charsRemoved, charsAdded):
		blockStart = self.qdoc.findBlock(position)
		blockEnd = self.qdoc.findBlock(position + charsAdded)
		for i in range(blockStart.blockNumber(), blockEnd.blockNumber() + 1):
			#print("Update user data for line: " + str(block.text()))
			self.setLineEdited(i, True)
		
		# Run bpc -> xml updater
		if self.updater and not self.updater.isRunning():
			self.bpMainWidget.msgView.clear()
			self.updater.setDocument(self.qdoc)
			self.updater.start(QtCore.QThread.LowestPriority)
		
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
		
	def compilerFinished(self):
		bpcFile = self.updater.bpcFile
		self.updater.bpcFile = None
		
		if bpcFile:
			self.bpMainWidget.startBenchmark("UpdateRootSafely")
			self.updateRootSafely(bpcFile)
			self.bpMainWidget.endBenchmark()
			
			self.bpMainWidget.updateLineInfo(True)
		
	def updateRootSafely(self, bpcFile):
		lineIndex = -1 # -1 because of bp.Core
		for node in bpcFile.nodes:
			if node:
				#print(("[%d]" % (lineIndex)) + bpcFile.nodeToOriginalLine[node])
				self.setLineNode(lineIndex, node)
			else:
				self.setLineNode(lineIndex, None)
			lineIndex += 1
		
		self.root = bpcFile.root
		
	def setRoot(self, newRoot):
		self.root = newRoot
		#header = getElementByTagName(self.root, "header")
		codeNode = getElementByTagName(self.root, "code")
		
		converter = LineToNodeConverter()
		bpcCode = nodeToBPC(self.root, 0, converter).strip()
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
		
		# Set user data
		for i in range(0, len(self.lines) - 1):
			userData = BPLineInformation(converter.lineToNode[i])
			self.qdoc.findBlockByNumber(i).setUserData(userData)
			
		# Create the updater
		self.updater = BPCodeUpdater(self)
		
	def setXML(self, xmlCode):
		self.doc = parseString(xmlCode.encode( "utf-8" ))
		self.setRoot(self.doc.documentElement)
		
	def goToLine(self, lineNum):
		cursor = self.textCursor()
		cursor.setPosition(self.qdoc.findBlockByLineNumber(lineNum - 1).position())
		self.setTextCursor(cursor)
		
	def goToLineEnd(self, lineNum):
		cursor = self.textCursor()
		cursor.setPosition(self.qdoc.findBlockByLineNumber(lineNum).position() - 1)
		self.setTextCursor(cursor)
	
	# LineNumberArea functions
	
	def initLineNumberArea(self):
		self.lineNumberArea = LineNumberArea(self)
		
		self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
		self.updateRequest.connect(self.updateLineNumberArea)
		self.cursorPositionChanged.connect(self.highlightCurrentLine)
		
		self.updateLineNumberAreaWidth(0)
		self.highlightLine()
	
	def highlightLine(self, lineIndex = 0, lineColor = None):
		if not lineColor:
			lineColor = self.getCurrentTheme()["current-line"]
		
		if lineColor:
			extraSelections = []
			
			if(not self.isReadOnly()):
				selection = QtGui.QTextEdit.ExtraSelection()
				selection.format.setBackground(lineColor)
				selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
				selection.cursor = self.textCursor()
				if lineIndex:
					selection.cursor.setPosition(self.qdoc.findBlockByLineNumber(lineIndex).position())
				selection.cursor.clearSelection()
				extraSelections.append(selection)
			
			self.setExtraSelections(extraSelections)
		
	def getLineNumberAreaWidth(self):
		digits = 1
		maxBlocks = max(1, self.blockCount())
		while maxBlocks >= 10:
			maxBlocks //= 10
			digits += 1
			
		space = 3 + self.fontMetrics().width('9') * digits
		return space
		
	def updateLineNumberArea(self, rect, dy):
		if dy:
			self.lineNumberArea.scroll(0, dy)
		else:
			self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
			
		if rect.contains(self.viewport().rect()):
			self.updateLineNumberAreaWidth(0)
		
	def updateLineNumberAreaWidth(self, newBlockCount):
		self.setViewportMargins(self.getLineNumberAreaWidth(), 0, 0, 0)
		
	def resizeEvent(self, event):
		super().resizeEvent(event)
		
		if self.lineNumberArea:
			cr = self.contentsRect()
			self.lineNumberArea.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.getLineNumberAreaWidth(), cr.height()))
		
	def lineNumberAreaPaintEvent(self, event):
		painter = QtGui.QPainter(self.lineNumberArea)
		painter.fillRect(event.rect(), QtCore.Qt.lightGray)
		
		block = self.firstVisibleBlock()
		blockNumber = block.blockNumber()
		top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
		bottom = top + self.blockBoundingRect(block).height()
		
		while block.isValid() and top <= event.rect().bottom():
			if block.isVisible() and bottom >= event.rect().top():
				number = str(blockNumber + 1)
				painter.setPen(QtCore.Qt.black)
				painter.drawText(0, top, self.lineNumberArea.width(), self.fontMetrics().height(), QtCore.Qt.AlignRight, number)
			
			block = block.next()
			top = bottom
			bottom = top + int(self.blockBoundingRect(block).height())
			blockNumber += 1
