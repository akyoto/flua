from PyQt4 import QtGui, QtCore, uic
from bp.Tools.IDE.Syntax.BPCSyntax import *
from bp.Compiler import *
#import yappi

class BPLineInformation(QtGui.QTextBlockUserData):
	
	def __init__(self, xmlNode = None, edited = False, previousNode = None):
		super().__init__()
		self.node = xmlNode
		self.oldNode = previousNode
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
		#yappi.start()
		if self.codeEdit.futureText:
			codeText = self.codeEdit.futureText
		else:
			codeText = self.qdoc.toPlainText()
		#self.bpIDE.msgView.clear()
		#self.codeEdit.clearHighlights()
		
		try:
			# TODO: Remove unsafe benchmark
			filePath = self.codeEdit.getFilePath()
			print("-" * 80)
			self.startBenchmark("[%s] Parser" % stripDir(filePath))
			self.bpcFile = self.bpc.spawnFileCompiler(filePath, True, codeText)
			if self.bpcFile.inFunction != 0:
				print("inFunction: " +  str(self.bpcFile.inFunction))
		except InputCompilerException as e:
			lineNumber = e.getLineNumber()
			errorMessage = e.getMsg()
			errorFilePath = e.getFilePath()
			self.bpIDE.msgView.addLineBasedMessage(errorFilePath, lineNumber, errorMessage)
			#self.codeEdit.setLineError(lineNumber - 1, errorMessage)
			#self.codeEdit.highlightLine(lineNumber - 1, QtGui.QColor("#ff0000"))
		finally:
			#yappi.stop()
			#yappi.print_stats()
			self.endBenchmark()
			#yappi.clear_stats()
		
		return

class LineNumberArea(QtGui.QWidget):
	
	def __init__(self, codeEdit):
		super().__init__(codeEdit)
		self.codeEdit = codeEdit
		
	def sizeHint(self):
		return QtCore.QSize(self.codeEdit.getLineNumberAreaWidth(), 0)
		
	def paintEvent(self, event):
		self.codeEdit.lineNumberAreaPaintEvent(event)

class BPCAutoCompleterModel(QtGui.QStringListModel):
	
	def __init__(self, parent = None):
		super().__init__(list(BPCHighlighter.keywords), parent)
		self.icon = QtGui.QIcon("images/icons/autocomplete/keyword.png")
		#self.index(0, 0).setData(QtCore.Qt.DecorationRole, self.icon)
		
	def data(self, index, role):
		if role == QtCore.Qt.DecorationRole:
			return self.icon
		return super().data(index, role)

class BPCAutoCompleter(QtGui.QCompleter):
	
	def __init__(self, parent = None):
		self.model = BPCAutoCompleterModel()
		QtGui.QCompleter.__init__(self, self.model, parent)

class BPCodeEdit(QtGui.QPlainTextEdit, Benchmarkable):
	
	def __init__(self, bpIDE = None):
		super().__init__(bpIDE)
		
		self.threaded = True
		
		self.bpIDE = bpIDE
		self.qdoc = self.document()
		self.highlighter = BPCHighlighter(self.qdoc, self.bpIDE)
		self.setFont(QtGui.QFont("monospace", 10))
		self.setTabStopWidth(4 * self.fontMetrics().maxWidth())
		self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
		self.setCurrentCharFormat(self.bpIDE.currentTheme["default"])
		
		bgStyle = bpIDE.currentTheme["default-background"]
		if bgStyle != "#ffffff":
			self.setStyleSheet("background-color: %s" % bgStyle);
		
		#p = self.palette()
		#p.setColor(QtGui.QPalette.Base, QtCore.Qt.red)
		#p.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
		#self.setPalette(p)
		#self.setTextColor(QtCore.QColor.white)
		
		self.autoIndentKeywords = {
			"if",
			"elif",
			"else",
			"try",
			"catch",
			"while",
			"for",
			"in",
			"switch",
			"case",
			"target",
			"extern",
			"compilerflags",
			"template",
			"get",
			"set",
			"private",
			"operator",
			"to"
		}
		
		self.qdoc.contentsChange.connect(self.onTextChange)
		self.lineNumberArea = None
		
		self.completer = None
		completer = BPCAutoCompleter()
		self.setCompleter(completer)
		#self.completer.setWidget(self)
		
		if 0:
			self.initLineNumberArea()
	
	def setCompleter(self, completer):
		if self.completer:
			self.disconnect(self.completer, 0, self, 0)
		if not completer:
			return
		
		completer.setWidget(self)
		completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
		completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.completer = completer
		self.connect(self.completer, QtCore.SIGNAL("activated(const QString&)"), self.insertCompletion)
	
	def insertCompletion(self, completion):
		tc = self.textCursor()
		extra = (len(completion) - len(self.completer.completionPrefix()))
		tc.movePosition(QtGui.QTextCursor.Left)
		tc.movePosition(QtGui.QTextCursor.EndOfWord)
		tc.insertText(completion[len(completion) - extra:])
		self.setTextCursor(tc)
	
	def textUnderCursor(self):
		tc = self.textCursor()
		tc.select(QtGui.QTextCursor.WordUnderCursor)
		return tc.selectedText()

	def focusInEvent(self, event):
		if self.completer:
			self.completer.setWidget(self)
		QtGui.QPlainTextEdit.focusInEvent(self, event)
	
	def keyPressEvent(self, event):
		# Auto Complete
		isShortcut = (event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Space)
		if isShortcut:
			self.completer.popup().show()
		
		# Auto Complete
		if self.completer and self.completer.popup().isVisible():
			if event.key() in (
					QtCore.Qt.Key_Enter,
					QtCore.Qt.Key_Return,
					QtCore.Qt.Key_Escape,
					QtCore.Qt.Key_Tab,
					QtCore.Qt.Key_Backtab):
				event.ignore()
				return
			
			## has ctrl-E been pressed??
			if (not self.completer or not isShortcut):
				super().keyPressEvent(event)

			## ctrl or shift key on it's own??
			ctrlOrShift = event.modifiers() in (QtCore.Qt.ControlModifier, QtCore.Qt.ShiftModifier)
			if ctrlOrShift and not event.text():
				# ctrl or shift key on it's own
				return
			
			eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-=" #end of word

			hasModifier = ((event.modifiers() != QtCore.Qt.NoModifier) and not ctrlOrShift)

			completionPrefix = self.textUnderCursor()

			if (not isShortcut and (hasModifier or not event.text() or len(completionPrefix) < 3 or event.text()[-1] in eow)):
				self.completer.popup().hide()
				return

			if (completionPrefix != self.completer.completionPrefix()):
				self.completer.setCompletionPrefix(completionPrefix)
				popup = self.completer.popup()
				popup.setCurrentIndex(self.completer.completionModel().index(0,0))

			cr = self.cursorRect()
			cr.setWidth(self.completer.popup().sizeHintForColumn(0) + self.completer.popup().verticalScrollBar().sizeHint().width())
			self.completer.complete(cr) ## popup it up!
		# Auto Indent
		elif event.key() == QtCore.Qt.Key_Return:
			cursor = self.textCursor()
			pos = cursor.position()
			block = self.qdoc.findBlock(pos)
			lineInfo = block.userData()
			line = block.text()
			tabLevel = countTabs(line)
			
			nodeName = ""
			if lineInfo:
				node = lineInfo.node
				if node and node.nodeType != Node.TEXT_NODE:
					nodeName = node.tagName
			
			# Retrive the keyword from the line
			pureLine = line[tabLevel:]
			keyword = ""
			i = 0
			for c in pureLine:
				if not c.isalnum() and not c == '_':
					keyword = pureLine[:i]
					break
				i += 1
			
			# Whole line
			wasFullLine = False
			if not keyword:
				keyword = pureLine
				wasFullLine = True
			
			if keyword:
				# Indent it?
				if keyword in self.autoIndentKeywords:
					tabLevel += 1
				elif nodeName == "function" or nodeName == "class" or nodeName == "new":
					tabLevel += 1
				elif (wasFullLine or nodeName == "call") and not self.bpIDE.processor.getFirstDTreeByFunctionName(keyword) and tabLevel <= 1:
					# TODO: Check whether parameters hold variable names only
					# If the parameters have numbers then this won't be a function definition
					tabLevel += 1
				# TODO: All methods
				elif keyword == "init" and tabLevel == 1:
					tabLevel += 1
			
			# Add the text
			cursor.beginEditBlock()
			cursor.insertText("\n" + "\t" * tabLevel)
			cursor.endEditBlock()
			
			event.accept()
		# TODO: Binary and ?
		#elif event.key() == QtCore.Qt.Key_Space and event.modifiers() == QtCore.Qt.ControlModifier:
		#	print("Yo!")
		else:
			super().keyPressEvent(event)
	
	def clear(self):
		self.doc = None
		self.root = None
		self.filePath = ""
		self.futureText = ""
		self.lines = []
		self.bpcFile = None
		
		self.disableUpdatesFlag = True
		self.updater = BPCodeUpdater(self)
		super().clear()
		self.disableUpdatesFlag = False
	
	def clearHighlights(self):
		self.setExtraSelections([])
	
	def getCurrentTheme(self):
		return self.bpIDE.getCurrentTheme()
	
	def rehighlightFunctionUsage(self):
		# TODO: Only highlight blocks where the function is used
		self.startBenchmark("CDE Rehighlight")
		self.highlighter.rehighlight()
		self.endBenchmark()
	
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
		
	#def setLineNode(self, index, newNode):
	#	block = self.qdoc.findBlockByNumber(index)
	#	
	#	oldNode = None
	#	oldData = block.userData()
	#	if oldData:
	#		oldNode = oldData.node
	#	
	#	block.setUserData(BPLineInformation(newNode, False, oldNode))
	
	def setLineEdited(self, index, edited):
		block = self.qdoc.findBlockByNumber(index)
		lineInfo = block.userData()
		if lineInfo:
			block.setUserData(BPLineInformation(lineInfo.node, True, lineInfo.oldNode))
		
	def onTextChange(self, position, charsRemoved, charsAdded):
		blockStart = self.qdoc.findBlock(position)
		blockEnd = self.qdoc.findBlock(position + charsAdded)
		for i in range(blockStart.blockNumber(), blockEnd.blockNumber() + 1):
			#print("Update user data for line: " + str(block.text()))
			self.setLineEdited(i, True)
		
		# Run bpc -> xml updater
		#print(self.disableUpdatesFlag)
		if self.updater and not self.disableUpdatesFlag and not self.updater.isRunning():
			self.runUpdater()
		
	def runUpdater(self):
		self.bpIDE.msgView.clear()
		
		self.updater.setDocument(self.qdoc)
		
		if self.threaded:
			self.updater.start(QtCore.QThread.NormalPriority)
		else:
			self.updater.run()
			self.compilerFinished()
		
	def getLineIndex(self):
		return self.textCursor().blockNumber()
		
	def getLineNumber(self):
		return self.getLineIndex() + 1
		
	def getNodeByLineIndex(self, lineIndex):
		lineInfo = self.qdoc.findBlockByNumber(lineIndex).userData()
		
		if lineInfo:
			#if lineInfo.edited == False:
			return lineInfo.node
		
		return None
		
	def getOldNodeByLineIndex(self, lineIndex):
		lineInfo = self.qdoc.findBlockByNumber(lineIndex).userData()
		
		if lineInfo:
			#if lineInfo.edited == False:
			return lineInfo.oldNode
		
		return None
		
	def compilerFinished(self):
		self.bpcFile = self.updater.bpcFile
		self.updater.bpcFile = None
		
		#self.disableUpdatesFlag = True
		
		if self.bpcFile:
			#self.bpIDE.startBenchmark("UpdateRootSafely")
			self.updateRootSafely()
			#self.bpIDE.endBenchmark()
			
			self.bpIDE.updateLineInfo(force=True, updateDependencyView=False)
			self.bpIDE.runPostProcessor()
		elif self.futureText:
			self.setPlainText(self.futureText)
			self.futureText = ""
		
		self.bpIDE.msgView.updateView()
		
		#self.disableUpdatesFlag = False
		
	def getCurrentLine(self):
		lineIndex = self.getLineIndex()
		return self.qdoc.findBlockByNumber(lineIndex).text()
		
	def updateRootSafely(self):
		lineIndex = -1 # -1 because of bp.Core
		for node in self.bpcFile.nodes:
			#print("[%d] %s" % (lineIndex, node))
			if lineIndex >= 0:
				block = self.qdoc.findBlockByNumber(lineIndex)
				
				oldNode = None
				oldData = block.userData()
				if oldData:
					oldNode = oldData.node
					#oldData.oldNode = oldData.node
					#oldData.node = node
				#else:
				block.setUserData(BPLineInformation(node, False, oldNode))
				#self.setLineNode(lineIndex, node)
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
		self.disableUpdatesFlag = True
		self.setPlainText("\n".join(self.lines))
		
		#self.futureText = 
		self.runUpdater()
		
	def setXML(self, xmlCode):
		self.disableUpdatesFlag = True
		
		self.doc = parseString(xmlCode.encode("utf-8"))
		self.setRoot(self.doc.documentElement)
		
	def goToLine(self, lineNum):
		cursor = self.textCursor()
		cursor.setPosition(self.qdoc.findBlockByLineNumber(max(lineNum - 1, 0)).position())
		self.setTextCursor(cursor)
		
	def goToLineEnd(self, lineNum):
		cursor = self.textCursor()
		block = self.qdoc.findBlockByLineNumber(lineNum - 1)
		cursor.setPosition(block.position() + len(block.text()))
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
