from PyQt4 import QtGui, QtCore, uic
from bp.Tools.IDE.Syntax.BPCSyntax import *
from bp.Tools.IDE.Threads import *
from bp.Compiler import *
#import yappi

# Auto Completion
class BPCAutoCompleterModel(QtGui.QStringListModel):
	
	def __init__(self, parent = None):
		self.shortCuts = {
			"saac" : "SimplyAwesomeAutoComplete"
		}
		self.shortCutList = list(self.shortCuts)
		
		self.keywordList = None
		
		super().__init__([], parent)
		self.keywordIcon = QtGui.QIcon("images/icons/autocomplete/keyword.png")
		#self.index(0, 0).setData(QtCore.Qt.DecorationRole, self.icon)
		
	def setKeywordList(self, keywordList):
		self.keywordList = keywordList
		self.updateStringList()
		
	def updateStringList(self):
		self.setStringList(self.keywordList + self.shortCutList)
		
	def data(self, index, role):
		if role == QtCore.Qt.DecorationRole:
			text = super().data(index, QtCore.Qt.DisplayRole)
			if text in self.keywordList:
				return self.keywordIcon
			elif text in self.shortCutList:
				return self.keywordIcon
		
		# TODO: Auto completion for shortcuts
		if role == QtCore.Qt.DisplayRole:
			shortCut = super().data(index, role)
			if shortCut in self.shortCuts:
				fullCompletion = self.shortCuts[shortCut]
				return fullCompletion
			else:
				return shortCut
		
		return super().data(index, role)

class BPCAutoCompleter(QtGui.QCompleter):
	
	def __init__(self, parent = None):
		self.bpcModel = BPCAutoCompleterModel()
		QtGui.QCompleter.__init__(self, self.bpcModel, parent)

# Code Edit
class BPCodeEdit(QtGui.QPlainTextEdit, Benchmarkable):
	
	def __init__(self, bpIDE = None, parent = None):
		super().__init__(parent)
		
		self.threaded = True
		
		self.bpIDE = bpIDE
		currentTheme = self.bpIDE.getCurrentTheme()
		
		self.qdoc = self.document()
		self.highlighter = BPCHighlighter(self.qdoc, self.bpIDE)
		self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
		self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		self.setFont(self.bpIDE.config.monospaceFont)
		#self.setCurrentCharFormat(self.bpIDE.config.theme["default"])
		
		#bgStyle = bpIDE.currentTheme["default-background"]
		#if bgStyle != "#ffffff":
		#	self.setStyleSheet("background-color: %s" % bgStyle);
		
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
		#self.completer.setWidget(self)
		
		#self.initLineNumberArea()
	
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
	
	#def setBackgroundColor(self, bgColor):
	#	p = self.palette()
	#	p.setColor(QtGui.QPalette.Base, bgColor)
	#	p.setColor(QtGui.QPalette.Window, bgColor)
	#	self.setPalette(p)
	#	self.setBackgroundVisible(True)
	
	def setFont(self, font):
		super().setFont(font)
		self.setTabWidth(self.bpIDE.config.tabWidth)
	
	def setTabWidth(self, value):
		if os.name == "nt":
			self.setTabStopWidth(value * self.fontMetrics().width("9"))
		else:
			self.setTabStopWidth(value * self.fontMetrics().maxWidth())
	
	def setCompleter(self, completer):
		signal = QtCore.SIGNAL("activated(const QString&)")
		
		if self.completer:
			self.disconnect(self.completer, signal, self.insertCompletion)
		
		if not completer:
			return
		
		completer.setWidget(self)
		self.completer = completer
		self.connect(self.completer, signal, self.insertCompletion)
	
	def insertCompletion(self, completion):
		tc = self.textCursor()
		
		if completion in self.completer.bpcModel.shortCuts:
			#tc.movePosition(QtGui.QTextCursor.Left)
			tc.movePosition(QtGui.QTextCursor.StartOfWord)
			tc.select(QtGui.QTextCursor.WordUnderCursor)
			tc.removeSelectedText()
			tc.insertText(self.completer.bpcModel.shortCuts[completion])
		else:
			extra = (len(completion) - len(self.completer.completionPrefix()))
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
	
	def getImportedModulesByCode(self):
		importedMods = []
		lines = self.toPlainText().split("\n")
		for line in lines:
			line = line.strip()
			if line.startswith("import") and len(line) >= 8 and line[6].isspace():
				mod = line[7:].strip()
				if mod:
					importedMods.append(mod)
		return importedMods
	
	def keyPressEvent(self, event):
		# Auto Complete
		isShortcut = (event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Space)
		
		# Auto Complete
		if self.completer and self.bpIDE.codeEdit == self and (isShortcut or self.completer.popup().isVisible()):
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
				popup.setCurrentIndex(self.completer.completionModel().index(0, 0))
			
			# Insert directly if it's just 1 possibility
			enableACInstant = False
			if enableACInstant:
				if self.completer.completionCount() == 1:
					self.insertCompletion(self.completer.currentCompletion())
					return
			
			cr = self.cursorRect()
			cr.setWidth(self.completer.popup().sizeHintForColumn(0) + self.completer.popup().verticalScrollBar().sizeHint().width())
			self.completer.complete(cr) ## popup it up!
			
			#if isShortcut:
			#	self.completer.popup().show()
		# Auto Indent
		elif event.key() == QtCore.Qt.Key_Return:
			cursor = self.textCursor()
			pos = cursor.position()
			block = self.qdoc.findBlock(pos)
			lineInfo = block.userData()
			line = block.text()
			tabLevel = countTabs(line)
			
			isAtEndOfLine = (block.position() + len(line) == pos)
			
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
			
			if keyword and isAtEndOfLine:
				# Indent it?
				if keyword in self.autoIndentKeywords:
					tabLevel += 1
				elif nodeName == "function" or nodeName == "class" or nodeName == "new":
					tabLevel += 1
				elif ((wasFullLine or nodeName == "call")
						and not self.bpIDE.processor.getFirstDTreeByFunctionName(keyword)
						and tabLevel <= 1
						and self.bpIDE.getErrorCount() == 0
						and line[-1] != ')'):
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
				
				if oldPath != newPath and self.bpIDE.processor:
					self.bpIDE.processor.changeCompiledFilePath(oldPath, newPath)
			
			if self.bpcFile:
				self.bpcFile.writeToFS()
			
			self.bpIDE.statusBar.showMessage("Saved " + newPath + " successfully.", 1000)
		except:
			self.setFilePath(oldPath)
			self.bpIDE.statusBar.showMessage("Error saving " + newPath, 2000)
	
	def setFilePath(self, filePath):
		self.filePath = fixPath(filePath)
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
			
			self.bpIDE.runPostProcessor()
		elif self.futureText:
			self.setPlainText(self.futureText)
			self.futureText = ""
		
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
		#self.highlightLine()
	
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

# Information stored per line
class BPLineInformation(QtGui.QTextBlockUserData):
	
	def __init__(self, xmlNode = None, edited = False, previousNode = None):
		super().__init__()
		self.node = xmlNode
		self.oldNode = previousNode
		self.edited = edited

# Useless line numbers
class LineNumberArea(QtGui.QWidget):
	
	def __init__(self, codeEdit):
		super().__init__(codeEdit)
		self.codeEdit = codeEdit
		
	def sizeHint(self):
		return QtCore.QSize(self.codeEdit.getLineNumberAreaWidth(), 0)
		
	def paintEvent(self, event):
		self.codeEdit.lineNumberAreaPaintEvent(event)
