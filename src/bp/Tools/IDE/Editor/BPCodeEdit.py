from PyQt4 import QtGui, QtCore, uic
from bp.Tools.IDE.Syntax.BPCSyntax import *
from bp.Compiler import *

class BPLineInformation(QtGui.QTextBlockUserData):
	
	def __init__(self, xmlNode = None, edited = False):
		super().__init__()
		self.node = xmlNode
		self.edited = edited

class BPCodeUpdater(QtCore.QThread, Benchmarkable):
	
	def __init__(self, codeEdit):
		super().__init__(codeEdit)
		self.codeEdit = codeEdit
		self.bpIDE = codeEdit.bpIDE
		self.setDocument(codeEdit.qdoc)
		self.bpc = BPCCompiler(getModuleDir())
		self.bpcFile = None
		self.finished.connect(self.codeEdit.compilerFinished)
		
	def setDocument(self, doc):
		self.qdoc = doc
		
	def run(self):
		if self.codeEdit.futureText:
			codeText = self.codeEdit.futureText
		else:
			codeText = self.qdoc.toPlainText()
		#self.bpIDE.msgView.clear()
		#self.codeEdit.clearHighlights()
		
		try:
			# TODO: Remove unsafe benchmark
			filePath = self.codeEdit.getFilePath()
			self.startBenchmark("BPC Parser")
			self.bpcFile = self.bpc.spawnFileCompiler(filePath, True, codeText)
			self.endBenchmark()
		except InputCompilerException as e:
			lineNumber = e.getLineNumber()
			errorMessage = e.getMsg()
			self.bpIDE.msgView.addLineBasedMessage(lineNumber, errorMessage)
			#self.codeEdit.setLineError(lineNumber - 1, errorMessage)
			#self.codeEdit.highlightLine(lineNumber - 1, QtGui.QColor("#ff0000"))
		
		return

class LineNumberArea(QtGui.QWidget):
	
	def __init__(self, codeEdit):
		super().__init__(codeEdit)
		self.codeEdit = codeEdit
		
	def sizeHint(self):
		return QtCore.QSize(self.codeEdit.getLineNumberAreaWidth(), 0)
		
	def paintEvent(self, event):
		self.codeEdit.lineNumberAreaPaintEvent(event)

class BPCodeEdit(QtGui.QPlainTextEdit):
	
	def __init__(self, bpIDE = None):
		super().__init__(bpIDE)
		self.bpIDE = bpIDE
		self.qdoc = self.document()
		self.highlighter = BPCHighlighter(self.qdoc, self.bpIDE)
		self.setFont(QtGui.QFont("monospace", 10))
		self.setTabStopWidth(4 * 8)
		self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
		self.setCurrentCharFormat(self.bpIDE.currentTheme["default"])
		self.clear()
		
		self.qdoc.contentsChange.connect(self.onTextChange)
		self.lineNumberArea = None
		
		if 0:
			self.initLineNumberArea()
	
	def clear(self):
		self.doc = None
		self.root = None
		self.filePath = ""
		self.futureText = ""
		self.lines = []
		self.bpcFile = None
		self.disableUpdatesFlag = False
		self.updater = BPCodeUpdater(self)
		self.runUpdater()
		super().clear()
	
	def clearHighlights(self):
		self.setExtraSelections([])
	
	def getCurrentTheme(self):
		return self.bpIDE.getCurrentTheme()
	
	def save(self, newPath = ""):
		oldPath = self.getFilePath()
		
		try:
			if newPath:
				if not newPath.endswith(".bp"):
					newPath = stripExt(newPath) + ".bp"
				self.setFilePath(newPath)
			
			if self.bpcFile:
				self.bpcFile.writeToFS()
		except:
			self.setFilePath(oldPath)
	
	def setFilePath(self, filePath):
		self.filePath = filePath
		if self.bpcFile:
			self.bpcFile.setFilePath(self.filePath)
		
	def getFilePath(self):
		return self.filePath
		
	def setLineNode(self, index, newNode):
		block = self.qdoc.findBlockByNumber(index)
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
		if self.updater and not self.disableUpdatesFlag and not self.updater.isRunning():
			self.runUpdater()
		
	def runUpdater(self):
		self.bpIDE.msgView.clear()
		self.updater.setDocument(self.qdoc)
		self.updater.start(QtCore.QThread.NormalPriority)
		
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
		self.bpcFile = self.updater.bpcFile
		self.updater.bpcFile = None
		
		self.disableUpdatesFlag = True
		
		if self.bpcFile:
			#self.bpIDE.startBenchmark("UpdateRootSafely")
			self.updateRootSafely()
			#self.bpIDE.endBenchmark()
			
			self.bpIDE.updateLineInfo(force=True, updateDependencyView=False)
			self.bpIDE.runPostProcessor()
		
		self.bpIDE.msgView.updateView()
		
		self.disableUpdatesFlag = False
		
	def updateRootSafely(self):
		lineIndex = -1 # -1 because of bp.Core
		for node in self.bpcFile.nodes:
			#print("[%d] %s" % (lineIndex, node))
			if lineIndex >= 0:
				self.setLineNode(lineIndex, node)
			lineIndex += 1
		
		self.root = self.bpcFile.root
		
	def setRoot(self, newRoot):
		self.root = newRoot
		#header = getElementByTagName(self.root, "header")
		codeNode = getElementByTagName(self.root, "code")
		
		converter = LineToNodeConverter()
		bpcCode = nodeToBPC(self.root, 0, converter).strip()
		self.lines = bpcCode.split("\n")
		
		# Set user data
		lineToNodeLen = len(converter.lineToNode)
		for i in range(len(self.lines)):
			if i < lineToNodeLen:
				userData = BPLineInformation(converter.lineToNode[i])
			else:
				userData = BPLineInformation()
			self.qdoc.findBlockByNumber(i).setUserData(userData)
		
		# Set new text
		#self.disableUpdatesFlag = True
		#self.setPlainText("")
		#self.disableUpdatesFlag = False
		
		self.futureText = "\n".join(self.lines)
		self.runUpdater()
		
	def setXML(self, xmlCode):
		self.doc = parseString(xmlCode.encode("utf-8"))
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
