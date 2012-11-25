from PyQt4 import QtGui, QtCore, uic
from flua.Tools.IDE.Syntax import *
from flua.Tools.IDE.Environment import *
from flua.Tools.IDE.Threads import *
from flua.Tools.IDE.Widgets import *
from flua.Compiler import *
import collections
#import yappi

# Auto Completion for class members
class BPCClassMemberModel(QtGui.QStringListModel):
	
	def __init__(self, parent, classImpl, private = False):
		super().__init__([], parent)
		
		self.methods = classImpl.classObj.functions
		self.members = classImpl.classObj.properties
		self.publicMembers = classImpl.classObj.publicMembers
		
		self.methodList, self.memberList, self.iteratorList = classImpl.classObj.getAutoCompleteList(private)
		
		#if private:
		#	className = classImpl.classObj.name
		#	membersDict = parent.codeEdit.bpIDE.membersForClass
		#	if className in membersDict:
		#		self.members = membersDict[className] #classImpl.classObj.possibleMembers
		#		self.memberList = list(self.members)
		
		# Sort individually
		#self.memberList.sort()
		#self.methodList.sort()
		#self.iteratorList.sort()
		
		resultingList = self.memberList + self.methodList + self.iteratorList
		resultingList.sort()
		self.setStringList(resultingList)
		
		self.methodIcon = QtGui.QIcon("images/icons/autocomplete/method.png")
		self.memberIcon = QtGui.QIcon("images/icons/autocomplete/member.png")
		self.iteratorIcon = QtGui.QIcon("images/icons/autocomplete/iterator.png")
		
	def memberExists(self, text):
		return text in self.methodList or text in self.memberList
		
	def data(self, index, role):
		if role == QtCore.Qt.DecorationRole:
			text = super().data(index, QtCore.Qt.DisplayRole)
			
			# TODO: Optimize for 'in' dict search instead of list search
			if text in self.methods:
				return self.methodIcon
			elif text in self.members or text in self.publicMembers:
				return self.memberIcon
			elif text in self.iteratorList:
				return self.iteratorIcon
		
		return super().data(index, role)
		
# Auto Completion
class BPCAutoCompleterModel(QtGui.QStringListModel, Benchmarkable):
	
	def __init__(self, parent = None):
		Benchmarkable.__init__(self)
		
		self.shortCuts = dict()
		self.shortCutList = list(self.shortCuts)
		
		self.functions = {}
		self.functionList = []
		
		self.classes = {}
		self.classesList = []
		
		self.keywordList = []
		
		self.funcListLen = 0
		self.classesListLen = 0
		
		self.internFuncsList = []
		self.internDataTypesList = []
		
		self.externFuncs = {}
		self.externVars = {}
		
		self.externFuncsList = list(self.externFuncs)
		self.externVarsList = list(self.externVars)
		
		self.externFuncsListLen = len(self.externFuncsList)
		self.externVarsListLen = len(self.externVarsList)
		
		super().__init__([], parent)
		
		self.keywordIcon = QtGui.QIcon("images/icons/autocomplete/keyword.png")
		self.functionIcon = QtGui.QIcon("images/icons/autocomplete/function.png")
		self.internFuncIcon = QtGui.QIcon("images/icons/autocomplete/intern-function.png")
		self.internDataTypeIcon = QtGui.QIcon("images/icons/autocomplete/intern-data-type.png")
		self.externFuncIcon = QtGui.QIcon("images/icons/autocomplete/extern-function.png")
		self.externVarIcon = QtGui.QIcon("images/icons/autocomplete/extern-variable.png")
		self.classIcon = QtGui.QIcon("images/icons/autocomplete/class.png")
		self.exceptionIcon = QtGui.QIcon("images/icons/autocomplete/exception.png")
		self.shortcutFunctionIcon = QtGui.QIcon("images/icons/autocomplete/shortcut-function.png")
		#self.index(0, 0).setData(QtCore.Qt.DecorationRole, self.icon)
		
	def setBaseLists(self, keywordList, internFuncsList, internDataTypesList):
		self.keywordList = keywordList
		self.internFuncsList = internFuncsList
		self.internDataTypesList = internDataTypesList
		
		#print("Set internal data types:")
		#print(self.internDataTypesList)
		
		self.updateStringList()
		
	#def setAutoCompleteLists(self, functionList, shortCuts, classesList):
	#	self.functionList = functionList
	#	self.funcListLen = len(functionList)
	#	
	#	self.shortCuts = shortCuts
	#	self.shortCutList = list(shortCuts)
	#	
	#	self.classesList = classesList
	#	self.classesListLen = len(classesList)
	#	
	#	self.updateStringList()
		
	def retrieveData(self, outComp):
		self.startBenchmark("Updated AutoComplete list")
		
		self.functions = outComp.mainClass.functions
		self.classes = outComp.mainClass.classes
		self.externFuncs = outComp.mainClass.externFunctions
		self.externVars = outComp.mainClass.externVariables
		
		modified = 0
		
		if len(self.externFuncs) != self.externFuncsListLen:
			self.externFuncsList = list(self.externFuncs)
			self.externFuncsListLen = len(self.externFuncsList)
			modified += 1
			
		if len(self.externVars) != self.externVarsListLen:
			self.externVarsList = list(self.externVars)
			self.externVarsListLen = len(self.externVarsList)
			modified += 1
			
		if len(self.functions) != self.funcListLen:
			self.functionList = list(self.functions)
			self.funcListLen = len(self.functionList)
			
			self.shortCuts = buildShortcutDict(self.functionList)
			self.shortCutList = list(self.shortCuts)
			#print(self.shortCutsList)
			
			modified += 1
			
		if len(self.classes) != self.classesListLen:
			self.classesList = list(self.classes)
			self.classesListLen = len(self.classesList)
			modified += 1
			
		if modified:
			self.updateStringList()
			self.endBenchmark()
		else:
			self.quitBenchmark()
		
	#def setShortCutDict(self, shortCuts):
	#	self.shortCuts = shortCuts
	#	self.shortCutList = list(shortCuts)
	#	self.updateStringList()
	
	def updateStringList(self):
		#self.classesList.reverse()
		
		resultingList = (
			self.classesList +
			self.functionList +
			self.keywordList +
			self.internFuncsList +
			self.internDataTypesList +
			self.externFuncsList +
			self.externVarsList +
			self.shortCutList
		)
		resultingList.sort()
		
		self.setStringList(
			resultingList
		)
		
	def setMemberList(self, memberList):
		self.memberList = memberList
		
	def data(self, index, role):
		if role == QtCore.Qt.DecorationRole:
			text = super().data(index, QtCore.Qt.DisplayRole)
			
			# TODO: Optimize for 'in' dict search instead of list search
			if text in self.functions:
				return self.functionIcon
			elif text in self.externFuncs:
				return self.externFuncIcon
			elif text in self.externVars:
				return self.externVarIcon
			elif text in self.classes:
				if "Exception" in text:
					return self.exceptionIcon
				else:
					return self.classIcon
			elif text in self.shortCuts:
				return self.shortcutFunctionIcon
			elif text in self.keywordList:
				return self.keywordIcon
			elif text in self.internFuncsList:
				return self.internFuncIcon
			elif text in self.internDataTypesList:
				return self.internDataTypeIcon
		
		# TODO: Auto completion for shortcuts
		if role == QtCore.Qt.DisplayRole:
			shortCut = super().data(index, role)
			if shortCut in self.shortCuts:
				fullCompletion = self.shortCuts[shortCut]
				return fullCompletion
			else:
				return shortCut
		
		return super().data(index, role)

class BPCAutoCompleter(QtGui.QCompleter, Benchmarkable):
	
	# States
	STATE_SEARCHING_SUGGESTION = 1
	STATE_OPENED_AUTOMATICALLY = 2
	STATE_OPENED_BY_USER = 3
	
	def __init__(self, parent = None):
		Benchmarkable.__init__(self)
		
		self.bpcModel = BPCAutoCompleterModel()
		QtGui.QCompleter.__init__(self, self.bpcModel, parent)
		self.setModelSorting(QtGui.QCompleter.CaseSensitivelySortedModel)
		#self.setModelSorting(QtGui.QCompleter.UnsortedModel)
		self.popup().setObjectName("AutoCompleter")
		
	def memberExists(self, name):
		return self.model().memberExists(name)
		
	def memberListActivated(self):
		return self.model() != self.bpcModel
		
	def createClassMemberModel(self, dataType, private = False):
		self.startBenchmark("Create class member model for „%s“" % dataType)
		
		try:
			classImpl = self.codeEdit.outFile.getClassImplementationByTypeName(dataType)
		except BaseException as e:
			print(str(e))
			return False
		
		classMemberModel = BPCClassMemberModel(self, classImpl, private)
		self.endBenchmark()
		
		self.startBenchmark("Setting new model")
		#self.setModelSorting(QtGui.QCompleter.UnsortedModel)
		self.setModel(classMemberModel)
		self.endBenchmark()
		
		return True
		
	def deactivateMemberList(self):
		if self.model() != self.bpcModel:
			#self.startBenchmark("Set model sorting")
			#self.setModelSorting(QtGui.QCompleter.CaseSensitivelySortedModel)
			#self.endBenchmark()
			
			#self.startBenchmark("Set model")
			self.setModel(self.bpcModel)
			#self.endBenchmark()
		
	def activateMemberList(self, cursorRelPos = -1):
		# DON'T USE "or self.model() != self.bpcModel" because it will make types
		# stay here and they won't change.
		if not self.codeEdit.outFile:
			return False
		
		bpIDE = self.codeEdit.bpIDE
		tc = self.codeEdit.textCursor()
		pos = tc.position()
		block = tc.block()
		
		# Get the line text
		text = block.text()
		relPos = pos - block.position()
		leftOfCursor = text[:relPos]
		
		# Shortcut: Import?
		if text.startswith("import "):
			# TODO: Import model
			return False
		
		if len(leftOfCursor) >= 2 and leftOfCursor[-2] == '"':
			self.codeEdit.lastObject = getLeftMemberAccess(leftOfCursor, len(leftOfCursor) - 1, allowPoint = False)
			return self.createClassMemberModel("UTF8String")
		
		# Get what's in front of the dot
		dotPos = leftOfCursor.rfind(".")
		
		obj = getLeftMemberAccess(leftOfCursor, dotPos, allowPoint = True)
		member = leftOfCursor[dotPos+1:]
		
		#print("\nActivating member list:")
		#print("Object: " + obj)
		#print("Member: " + member)
		
		self.codeEdit.lastObject = obj
		#print(self.codeEdit.bpcFile)
		#print(self.codeEdit.outFile)
		
		# Shortcut: my?
		if obj in {"my", "self", "this"}:
			if bpIDE.currentNode:
				node = bpIDE.currentNode
				while node and node.parentNode and node.nodeType != Node.TEXT_NODE and (not node.tagName in {"class", "module"}):
					node = node.parentNode
				
				if node and node.tagName == "class":
					currentClass = getElementByTagName(node, "name").firstChild.nodeValue
					return self.createClassMemberModel(currentClass, private = True)
			else:
				return False
		
		if self.codeEdit.bpcFile and self.codeEdit.outFile:
			try:
				bpcFile = self.codeEdit.bpcFile
				prepdLine = bpcFile.prepareLine(obj)
				node = bpcFile.parseExpr(prepdLine)
			except CompilerException as e:
				print(str(e))
				return False
			
			#print("Translated expression to XML:\n%s\nNow trying to determine its data type." % (node.toprettyxml()))
			
			try:
				bpIDE.restoreScopesOfNode(bpIDE.currentNode)
				dataType = self.codeEdit.outFile.getExprDataType(node)
			except CompilerException as e:
				print(str(e))
				return False
			else:
				try:
					return self.createClassMemberModel(dataType)
					#print("Created class member model for „%s“" % dataType)
				except BaseException as e:
					print("No class information available for „%s“ (%s)" % (dataType, str(e)))
					self.deactivateMemberList()
		
		return False

def getLeftMemberAccess(expr, lastOccurence, allowPoint = True):
	# Left operand
	start = lastOccurence - 1
	
	leftBrackets = "([<"
	rightBrackets = ")]>"
	
	while start >= 0 and ((allowPoint and expr[start] == ".") or expr[start] == '"' or isVarChar(expr[start]) or expr[start] in rightBrackets):
		if expr[start] in rightBrackets:
			bracketCounter = 1
		else:
			bracketCounter = 0
			
		if expr[start] == '"':
			start -= 1
			while start >= 0 and expr[start] != '"':
				start -= 1
			start -= 1
			continue
		
		# Move to last part of the bracket
		while bracketCounter > 0 and start > 0:
			start -= 1
			if expr[start] in rightBrackets:
				bracketCounter += 1
			elif expr[start] in leftBrackets:
				bracketCounter -= 1
		start -= 1
	
	return expr[start+1:lastOccurence]

# Code Edit
class BPCodeEdit(QtGui.QPlainTextEdit, Benchmarkable):
	
	def __init__(self, bpIDE = None, parent = None):
		super().__init__(parent)
		Benchmarkable.__init__(self)
		
		self.threaded = True
		
		self.bpIDE = bpIDE
		currentTheme = self.bpIDE.getCurrentTheme()
		
		self.openingFile = False
		self.isTextFile = False
		self.hoveringFileName = ""
		self.lastObject = ""
		self.updateQueue = collections.deque()
		self.qdoc = self.document()
		self.completer = None
		self.environment = None
		self.docNavigator = None
		self.highlighter = None
		self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
		self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
		self.setFont(self.bpIDE.config.monospaceFont)
		self.lastCompletionTime = 0
		self.autoCompleteState = BPCAutoCompleter.STATE_SEARCHING_SUGGESTION
		self.reloading = False
		self.outFile = None
		self.lastFunctionCount = -1
		self.backgroundCompilerOutstandingTasks = 0
		self.ppOutstandingTasks = 0
		self.selectionChanged.connect(self.onSelectionChange)
		
		self.highlightLineSelection = QtGui.QTextEdit.ExtraSelection()
		self.highlightLineSelection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
		self.highlightLineSelection.cursor = self.textCursor()
		
		# Bracket highlighting
		self.bracketHighlightingActive = False
		self.bracketBeginSelection = QtGui.QTextEdit.ExtraSelection()
		self.bracketEndSelection = QtGui.QTextEdit.ExtraSelection()
		
		self.bracketsBegin = {
			'(' : ')',
			'[' : ']',
			'{' : '}',
		}
		
		self.bracketsEnd = {
			')' : '(',
			']' : '[',
			'}' : '{',
		}
		
		# Auto Replace
		self.autoReplace = {
			# Simple data flow
			#"->" : "→",
			#"<-" : "←",
			
			# These need more than one version
			# TODO: Not fully working yet, implement it.
			#"-->" : "⇢",
			#"-→" : "⇢",
			
			#"<--" : "⇠",
			#"←-" : "⇠",
			
			#"<->" : "↔",
			#"←>" : "↔",
			#"<→" : "↔",
		}
		
		self.autoSuggestion = self.bpIDE.config.autoSuggestionEnabled
		self.autoSuggestionMinChars = self.bpIDE.config.autoSuggestionMinChars
		#self.autoSuggestionTypedChars = 3
		self.autoSuggestionMinCompleteChars = self.bpIDE.config.autoSuggestionMinCompleteChars
		self.autoSuggestionMaxItemCount = self.bpIDE.config.autoSuggestionMaxItemCount
		
		self.enableACInstant = True
		
		# Bubbles!
		if not isinstance(parent, BPCodeEdit):
			# Doc bubble
			self.bubble = BPCodeEdit(self.bpIDE, self)
			self.bubble.hide()
			
			self.bubble.setObjectName("DocBubble")
			#self.bubble.setStyleSheet("background: rgba(0,0,0,10%); border-top-left-radius: 7px;")
			self.bubble.clear(True)
			self.bubble.setReadOnly(True)
			self.bubbleWidth = 325
			self.msgViewWidth = self.bubbleWidth
			self.bubble.setFont(QtGui.QFont("Ubuntu Mono", 9))
			
			self.bubble.horizontalScrollBar().setMaximumWidth(0)
			self.bubble.horizontalScrollBar().setMaximumHeight(0)
			self.bubble.horizontalScrollBar().hide()
			
			#self.bubble.verticalScrollBar().setStyleSheet("background: rgba(0,0,0,0%);")
			#self.bubble.verticalScrollBar().setMaximumWidth(0)
			#self.bubble.verticalScrollBar().setMaximumHeight(0)
			self.bubble.verticalScrollBar().hide()
			
			self.bubble.setLineWrapMode(QtGui.QPlainTextEdit.WidgetWidth)
			
			self.bubbleMinMovePx = 50
			self.bubble.setTabWidth(3)
			
			# Message view
			self.msgView = BPMessageView(self, self.bpIDE)
			self.msgView.setFont(QtGui.QFont("Ubuntu", 9))
		else:
			self.bubble = None
			self.msgView = None
		
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
			"const",
			"target",
			"extends",
			"pattern",
			"extern",
			"compilerflags",
			"template",
			"get",
			"set",
			"private",
			"operator",
			"to",
			"require",
			"ensure",
			"test",
			"parallel",
			"shared",
			"atomic",
			"namespace",
			"public",
			"on",
			"interface",
			"iterator",
			"implements",
			
			# A dirty hack so that C++ gets some auto indent
			'inline',
			'case',
			'default',
			'enum',
			
			# More cheating!
			"elsif",
		}
		
		self.qdoc.contentsChange.connect(self.onTextChange)
		self.lineNumberArea = None
		
		self.completer = None
		#self.completer.setWidget(self)
		
		# Line numbers
		#if self.bubble:
		#	self.initLineNumberArea()
	
	def reload(self):
		self.save()
		xmlCode = loadXMLFile(self.getFilePath())
		
		#self.clear()
		self.disableUpdatesFlag = True
		self.setPlainText("")
		self.openingFile = True
		self.reloading = True
		
		self.bpIDE.beforeSwitchingFile()
		self.setXML(xmlCode)
		self.bpIDE.afterSwitchingFile()
		#self.onUpdateTimeout()
		
		#self.runUpdater()
	
	def clear(self, isBubble = False):
		self.doc = None
		self.root = None
		self.lines = []
		self.bpcFile = None
		self.setFilePath("")
		
		if not isBubble:
			self.disableUpdatesFlag = True
			self.updater = None
			super().clear()
			self.updater = BPCodeUpdater(self)
			self.postProcessorThread = BPPostProcessorThread(self)
			self.disableUpdatesFlag = False
			
			self.timer = QtCore.QTimer(self)
			self.timer.timeout.connect(self.onUpdateTimeout)
			self.timer.start(self.bpIDE.config.updateInterval)
		else:
			self.updater = None
			self.timer = None
			super().clear()
	
	#def setBackgroundColor(self, bgColor):
	#	p = self.palette()
	#	p.setColor(QtGui.QPalette.Base, bgColor)
	#	p.setColor(QtGui.QPalette.Window, bgColor)
	#	self.setPalette(p)
	#	self.setBackgroundVisible(True)
	
	def updateFunctionCount(self, newFuncCount):
		if newFuncCount != self.lastFunctionCount: #and (self.lastFunctionCount != -1 or self.isTmpFile()):
			self.rehighlightFunctionUsage()
		
		self.lastFunctionCount = newFuncCount
	
	def isTmpFile(self):
		return self.bpIDE.isTmpPath(self.getFilePath())
	
	def wheelEvent(self, event):
		if self.bpIDE.ctrlPressed:
			font = self.font()
			ptSize = font.pointSize() + ((event.delta() > 0) * 2 - 1)
			
			if abs(ptSize) > 5:
				font.setPointSize(abs(ptSize))
			
			self.bpIDE.config.applyMonospaceFont(font)
		else:
			super().wheelEvent(event)
	
	def getCursorPosition(self):
		return self.textCursor().position()
		
	def setCursorPosition(self, pos):
		cursor = self.textCursor()
		cursor.setPosition(pos)
		self.setTextCursor(cursor)
	
	def highlightBrackets(self):
		cursor = self.textCursor()
		position = cursor.position()
		doc = self.qdoc
		theme = self.bpIDE.config.theme
		
		# Format
		bracketMatchFormat = theme["matching-brackets"]
		defaultFormat = theme["default"]
		
		# Remove old highlighting
		if self.bracketHighlightingActive:
			self.bracketHighlightingActive = False
			self.setExtraSelections(self.getActiveExtraSelections())
		
		# Do nothing on selected text
		if cursor.hasSelection():
			return
		
		# Check if we really need to highlight
		#if (cursor.atBlockEnd() or doc.characterAt(position) != '(') and (cursor.atBlockStart() or doc.characterAt(position - 1) != ')'):
		#	self.highlightingBrackets = False
		#	return
		
		isBeginBracket = doc.characterAt(position) in self.bracketsBegin
		isEndBracket = doc.characterAt(position - 1) in self.bracketsEnd
		
		if isBeginBracket:
			move = QtGui.QTextCursor.NextCharacter
			begin = doc.characterAt(position)
			end = self.bracketsBegin[begin]
			movement = 1
			position += 1
		elif isEndBracket:
			move = QtGui.QTextCursor.PreviousCharacter
			begin = doc.characterAt(position - 1)
			end = self.bracketsEnd[begin]
			movement = -1
			position -= 2
		else:
			return
		
		bracketBeginCursor = QtGui.QTextCursor(cursor)
		bracketBeginCursor.movePosition(move, QtGui.QTextCursor.KeepAnchor)
		
		charCount = doc.characterCount()
		
		braceDepth = 1
		while position >= 0 and position < charCount:
			c = doc.characterAt(position)
			
			#if not c:
			#	break
			
			if c == begin:
				braceDepth += 1
			elif c == end:
				braceDepth -= 1
				
				if braceDepth == 0:
					self.bracketEndSelection.format = bracketMatchFormat
					self.bracketEndSelection.cursor = QtGui.QTextCursor(cursor)
					self.bracketEndSelection.cursor.setPosition(position)
					self.bracketEndSelection.cursor.movePosition(QtGui.QTextCursor.NextCharacter, QtGui.QTextCursor.KeepAnchor)
					
					self.bracketBeginSelection.format = bracketMatchFormat
					self.bracketBeginSelection.cursor = bracketBeginCursor
					
					self.bracketHighlightingActive = True
					
					self.setExtraSelections(self.getActiveExtraSelections())
					
					break
			
			position += movement
	
	def getActiveExtraSelections(self):
		extraSelections = [self.highlightLineSelection]
		
		if self.bracketHighlightingActive: #and self.bracketEndSelection:
			extraSelections.append(self.bracketBeginSelection)
			extraSelections.append(self.bracketEndSelection)
			
		return extraSelections
	
	def locationBackward(self):
		print("Backward not implemented!")
		
	def locationForward(self):
		print("Forward not implemented!")
	
	def getTextAtCursor(self):
		tc = self.textCursor()
		pos = tc.positionInBlock()
		block = tc.block()
		
		# Get the line text
		text = block.text()
		
		if not text:
			return
		
		leftOfCursor = text[:pos]
		
		# TODO: Allow point
		#obj = getLeftMemberAccess(leftOfCursor, pos, allowPoint = False)
		obj = ""
		
		# Just to be absolutely sure this won't be an endless loop...
		count = 0
		
		while 1:
			tc.movePosition(QtGui.QTextCursor.StartOfWord)
			tc.select(QtGui.QTextCursor.WordUnderCursor)
			
			obj = tc.selectedText()
			
			if obj.replace("_", "").isalnum():
				break
			
			# 2 times to avoid an endless loop
			tc.movePosition(QtGui.QTextCursor.Left, n = 2)
			
			if tc.positionInBlock() == 0 or text[:tc.positionInBlock()].isspace() or count > 100:
				obj = ""
				break
				
			count += 1
			
		return obj
	
	def makeFunction(self, obj):
		#print("Making function %s" % obj)
		
		funcCode = "\n\n# \n%s\n\t..." % (obj)
		
		tc = self.textCursor()
		tc.beginEditBlock()
		
		tc.movePosition(QtGui.QTextCursor.EndOfWord)
		tc.insertText(funcCode)
		
		tc.movePosition(QtGui.QTextCursor.Left)
		tc.select(QtGui.QTextCursor.WordUnderCursor)
		
		tc.endEditBlock()
		
		self.setTextCursor(tc)
		
	def makeClass(self, obj):
		#print("Making class %s" % obj)
		
		classCode = """

# 
%s
	public
		...
	
	init
		...""" % (obj)
		
		tc = self.textCursor()
		tc.beginEditBlock()
		
		tc.movePosition(QtGui.QTextCursor.EndOfWord)
		
		# Get the line text
		block = tc.block()
		text = block.text()
		relPos = tc.positionInBlock()
		
		if relPos >= len(text) or not text[relPos] in "(<>)":
			tc.insertText("()")
		else:
			tc.movePosition(QtGui.QTextCursor.Right)
			tc.movePosition(QtGui.QTextCursor.EndOfWord)
		
		tc.insertText(classCode)
		
		tc.movePosition(QtGui.QTextCursor.Left)
		tc.select(QtGui.QTextCursor.WordUnderCursor)
		
		tc.endEditBlock()
		self.setTextCursor(tc)
	
	def mousePressEvent(self, event):
		if not self.bpIDE.config.developerMode:
			self.bpIDE.consoleDock.hide()
			self.bpIDE.searchResults.hide()
		
		if event.button() == QtCore.Qt.XButton1:
			self.locationBackward()
		elif event.button() == QtCore.Qt.XButton2:
			self.locationForward()
		
		if self.bpIDE.ctrlPressed and self.hasMouseTracking() and self.hoveringFileName:
			# Create file if it doesn't exist
			if not os.path.exists(self.hoveringFileName):
				with open(self.hoveringFileName, "w") as out:
					out.write("\n")
			
			self.bpIDE.openFile(self.hoveringFileName)
			self.hoveringFileName = ""
			self.setMouseTracking(False)
		
		super().mousePressEvent(event)
		
	# TODO: Implement this.
	def jumpToFunction(self, outFunc):
		tc = self.textCursor()
		
		#try:
		#if self.bpcFile:
		#	lineNumber = self.bpcFile.nodeToOriginalLineNumber[searchingNode]
		
		self.setTextCursor(tc)
		self.ensureCursorVisible()
		
	# TODO: Implement this.
	def jumpToClass(self, className):
		tc = self.textCursor()
		self.setTextCursor(tc)
		self.ensureCursorVisible()
		
	def onSelectionChange(self):
		if self.hasFocus():
			self.bpIDE.searchEdit.setUseSelection(self.textCursor().hasSelection())
	
	def mouseMoveEvent(self, event):
		self.hoveringFileName = ""
		
		if self.bpIDE.ctrlPressed:
			p = event.pos()
			cursor = self.cursorForPosition(p)
			block = cursor.block()
			text = block.text().strip()
			
			#cursor.movePosition(QtGui.QTextCursor.StartOfWord)
			#cursor.select(QtGui.QTextCursor.WordUnderCursor)
			
			if text.startswith("include "):
				self.hoveringFileName = extractDir(self.getFilePath()) + text[len("include "):]
			elif text.startswith("import "):
				importedMod = text[len("import "):]
				self.hoveringFileName = self.bpIDE.getModulePath(importedMod)
				
			# C++ syntax
			if self.hoveringFileName.endswith(";"):
				self.hoveringFileName = self.hoveringFileName[:-1]
		
		super().mouseMoveEvent(event)
	
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
		self.completer.codeEdit = self
		completer.disconnect(self.completer, signal, self.insertCompletion)
		self.connect(self.completer, signal, self.insertCompletion)
		
		# Set keyword list to the local environment
		if self.environment:
			#print("Setting base lists of %s" % (self.environment.name))
			self.completer.bpcModel.setBaseLists(
				list(self.environment.autoCompleteKeywords),
				list(self.environment.internalFunctions),
				list(self.environment.internalDataTypes)
			)
	
	def insertCompletion(self, completion):
		if self.bpIDE.codeEdit != self:
			return
		
		tc = self.textCursor()
		
		#tc.select(QtGui.QTextCursor.WordUnderCursor)
		relPos = tc.positionInBlock()
		textBlock = tc.block().text()
		
		if relPos > 1:
			char = textBlock[relPos - 1]
			
			if isVarChar(char):
				tc.movePosition(QtGui.QTextCursor.Left)
		else:
			char = ""
		
		if char != ".":
			tc.movePosition(QtGui.QTextCursor.StartOfWord)
			tc.select(QtGui.QTextCursor.WordUnderCursor)
			tc.removeSelectedText()
		
		if completion in self.completer.bpcModel.shortCuts:
			tc.insertText(self.completer.bpcModel.shortCuts[completion])
		else:
			tc.insertText(completion)
		
		# Class members
		if self.completer.memberListActivated():
			completerModel = self.completer.model()
			
			if completion in completerModel.iteratorList:
				tc.select(QtGui.QTextCursor.BlockUnderCursor)
				old = tc.selectedText()
				
				#print(old)
				#print(self.lastObject)
				#print(completion)
				
				if old.strip() == "%s.%s" % (self.lastObject, completion):
					tabs = "\t" * countTabs(old)
					tc.removeSelectedText()
					tc.insertText("\n%sfor x in %s\n%s\t..." % (tabs, old.strip(), tabs))
					tc.select(QtGui.QTextCursor.WordUnderCursor)
					self.setTextCursor(tc)
				else:
					tc.clearSelection()
			elif completion in completerModel.methodList and ((relPos == len(textBlock) or textBlock[relPos] != "(")):
				tc.insertText("()")
				tc.movePosition(QtGui.QTextCursor.Left)
			self.completer.setModel(self.completer.bpcModel)
		else:
			# Functions
			# TODO: Optimize for dict search instead of list search
			funcList = self.completer.bpcModel.functionList
			if completion in funcList:
				beforeCompletion = tc.block().text()[:-len(completion)]
				functionHasParameters = False
				
				# At end of line?
				if ((relPos == len(textBlock) or (not textBlock[relPos] in '("\''))): #tc.block().text() == beforeCompletion + completion:
					if beforeCompletion.isspace() or (not beforeCompletion) and functionHasParameters:
						tc.insertText(" ")
					else:
						tc.insertText("()")
						tc.movePosition(QtGui.QTextCursor.Left)
			# Expr blocks
			#elif completion in xmlToBPCExprBlock.keys() or completion in xmlToBPCSingleLineExpr.values():
			#	pass#tc.insertText(" ")
			# Blocks
			elif completion in self.completer.bpcModel.classesList:
				# Not exactly a perfect solution but works in most cases...
				textBlock = tc.block().text()
				if textBlock[-1] != ")" and (not textBlock.startswith("catch ")):
					node = self.bpIDE.currentNode
					
					if node:
						parentName = node.parentNode.tagName
						
						if parentName in {"extends", "implements"}:
							pass
						elif node.nodeType == Node.ELEMENT_NODE and node.tagName == "declare-type":
							pass
						else:
							tc.insertText("()")
							tc.movePosition(QtGui.QTextCursor.Left)
			elif completion in xmlToBPCBlock.values():
				tc.insertText("\n" + ("\t" * (countTabs(tc.block().text()) + 1)))
			
		self.lastCompletionTime = time.time()
		self.setTextCursor(tc)
		self.autoCompleteState = BPCAutoCompleter.STATE_SEARCHING_SUGGESTION
	
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
	
	def keyReleaseEvent(self, event):
		#if event.modifiers() & QtCore.Qt.ControlModifier:
		if self.bpIDE.ctrlPressed and self.hasMouseTracking():
			self.setMouseTracking(False)
		
		self.bpIDE.ctrlPressed = False
		super().keyReleaseEvent(event)
	
	def focusInEvent(self, event):
		# To fix switching workspaces on GNOME/KDE
		self.bpIDE.ctrlPressed = False
		super().focusInEvent(event)
	
	def keyPressEvent(self, event, dontAutoComplete = False):
		#if self.bpIDE.codeEdit is None:
		#	return
		
		# Ctrl + Mouse click
		eventModifiers = event.modifiers()
		eventKey = event.key()
		
		if eventModifiers == QtCore.Qt.ControlModifier:
			self.bpIDE.ctrlPressed = True
			self.setMouseTracking(True)
		
		if self.completer:
			popup = self.completer.popup()
		else:
			popup = None
		
		# Escape disables AC
		if eventKey == QtCore.Qt.Key_Escape:
			if not self.bpIDE.config.developerMode:
				self.bpIDE.consoleDock.hide()
			
			self.autoCompleteState = BPCAutoCompleter.STATE_SEARCHING_SUGGESTION
			popup.hide()
			event.ignore()
			return
		
		# Auto Complete
		isShortcut = (eventModifiers == QtCore.Qt.ControlModifier and eventKey == QtCore.Qt.Key_Space)
		
		# Auto Complete
		if 		(
					(not dontAutoComplete) and
					self.completer and
					self.bpIDE.codeEdit == self and
					(self.autoSuggestion or isShortcut or (popup and popup.isVisible()))
				):
			# Ignore certain keys for the editor when AC is open
			if popup.isVisible() and eventKey in (
					QtCore.Qt.Key_Enter,
					QtCore.Qt.Key_Return,
					QtCore.Qt.Key_Escape,
					QtCore.Qt.Key_Tab,
					QtCore.Qt.Key_Backtab):
				
				event.ignore()
				return
			
			# Handle the key event normally
			if not isShortcut:
				self.keyPressEvent(event, dontAutoComplete = True)
				
				if eventKey in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
					self.autoCompleteState = BPCAutoCompleter.STATE_SEARCHING_SUGGESTION
					return
			
			## ctrl or shift key on it's own should not AC
			ctrlOrShift = event.modifiers() in (QtCore.Qt.ControlModifier, QtCore.Qt.ShiftModifier)
			if ctrlOrShift and not event.text():
				#self.autoCompleteState = BPCAutoCompleter.STATE_SEARCHING_SUGGESTION
				#popup.hide()
				return
			
			# Get the text in the line
			oldCursor = self.textCursor()
			cursor = self.textCursor()
			block = cursor.block()
			text = block.text()
			relPos = cursor.positionInBlock() #cursor.position() - block.position()
			
			if (not isShortcut) and relPos == 1:
				self.autoCompleteState = BPCAutoCompleter.STATE_SEARCHING_SUGGESTION
				popup.hide()
				return
			
			# 
			if 	(
					(
						eventKey == QtCore.Qt.Key_Backspace #and
						#(self.autoCompleteState == BPCAutoCompleter.STATE_SEARCHING_SUGGESTION)
					)
					or
					(
					(not isShortcut) and (not event.text())
					)
					#and
					#((not self.completer.memberListActivated()) or self.completer.completionPrefix() == "")
				):
				self.autoCompleteState = BPCAutoCompleter.STATE_SEARCHING_SUGGESTION
				popup.hide()
				return
			
			# Modifier pressed?
			#hasModifier = ((event.modifiers() != QtCore.Qt.NoModifier) and not ctrlOrShift)
			
			eow = "~!@#$%^&*()_+{}|:\"<>?,/;'[]\\-= "
			if (not isShortcut) and ((not event.text()) or event.text()[-1] in eow):
				#print(event.text()[-1] + "<<<<<<<<<<")
				self.autoCompleteState = BPCAutoCompleter.STATE_SEARCHING_SUGGESTION
				popup.hide()
				self.completer.deactivateMemberList()
				return
			
			# Data flow and other auto replace stuff
			cursor.movePosition(QtGui.QTextCursor.Left)
			cursor.select(QtGui.QTextCursor.WordUnderCursor)
			
			selText = cursor.selectedText()
			if selText in self.autoReplace:
				cursor.removeSelectedText()
				cursor.insertText(self.autoReplace[selText])
				self.setTextCursor(cursor)
			else:
				self.setTextCursor(oldCursor)
			
			# Don't AC on comments
			if text.lstrip().startswith("#"):
				if self.autoCompleteState != BPCAutoCompleter.STATE_SEARCHING_SUGGESTION:
					self.autoCompleteState = BPCAutoCompleter.STATE_SEARCHING_SUGGESTION
					popup.hide()
				
				return
			
			# Check char format
			#cursor.movePosition(QtGui.QTextCursor.StartOfWord)
			#charFormat = cursor.charFormat()
			#style = self.bpIDE.getCurrentTheme()
			#
			#if charFormat == style["comment"] or charFormat == style["string"]:
			#	return
			
			# Debug
			#print(relPos)
			#print(text)
			#print(text[:relPos])
			
			# Get the completion prefix
			completionPrefix = getLeftMemberAccess(text[:relPos], relPos, allowPoint = False)
			completionPrefixLen = len(completionPrefix)
			
			# Did the user already type in the right member name?
			if self.completer.memberListActivated() and self.completer.memberExists(completionPrefix):
				self.autoCompleteState = BPCAutoCompleter.STATE_SEARCHING_SUGGESTION
				popup.hide()
				self.completer.deactivateMemberList()
				return
			
			# When the cursor is at a.member| this returns "."
			b4pos = relPos - completionPrefixLen - 1
			if b4pos and text and abs(b4pos) < len(text):
				charBeforeWord = text[b4pos]
				
				# Ignore "..." no-op
				if (b4pos >= 2 and text[b4pos - 1] == "." and text[b4pos - 2] == "."):
					self.autoCompleteState = BPCAutoCompleter.STATE_SEARCHING_SUGGESTION
					popup.hide()
					self.completer.deactivateMemberList()
					return
			else:
				charBeforeWord = ""
			
			if completionPrefix.endswith(")"):
				if text and relPos > 0 and text[relPos - 1] != ".":
					self.autoCompleteState = BPCAutoCompleter.STATE_SEARCHING_SUGGESTION
					popup.hide()
					self.completer.deactivateMemberList()
					return
			
			# Set the prefix later
			gonnaSetPrefix = False
			if (
					event.text() == "."
					or
					(
						((completionPrefixLen >= self.autoSuggestionMinChars and (not completionPrefix[-1] in "~!@#$%^&*()_+{}|:\"<>?,/;'[]\\-=")) or isShortcut or popup.isVisible() or self.completer.memberListActivated())
						and
						(completionPrefix != self.completer.completionPrefix())
					)
				):
				
				# Backspace to 0 length would show a HUGE list unexpectedly
				if completionPrefixLen == 0 and eventKey == QtCore.Qt.Key_Backspace:
					if charBeforeWord != "." or (text and relPos >= 1 and text[relPos - 1] == "."): #and (not self.completer.memberListActivated()):
						self.autoCompleteState = BPCAutoCompleter.STATE_SEARCHING_SUGGESTION
						popup.hide()
						return
				
				gonnaSetPrefix = True
			
			# Member list
			if charBeforeWord == ".":
				if not self.completer.memberListActivated():
					#print("OK:")
					#print(completionPrefix)
					#print(relPos)
					#print(text)
					#print(event.text())
					
					#OK:
					#
					#7
					#				my.abc
					#.
					
					if len(text) > relPos + 1:
						firstCharAfterCursor = text[relPos + 1]
						if isVarChar(firstCharAfterCursor):
							return
					
					if self.completer.activateMemberList(relPos):
						self.autoCompleteState = BPCAutoCompleter.STATE_OPENED_AUTOMATICALLY
					else:
						popup.hide()
						self.completer.deactivateMemberList()
						return
			else:
				if self.completer.memberListActivated():
					self.completer.deactivateMemberList()
					gonnaSetPrefix = False
			
			# AFTER THE MEMBER LIST HAS BEEN EVENTUALLY CREATED set the prefix
			if gonnaSetPrefix:
				#print("SETTING PREFIX TO:%s" % completionPrefix)
				self.completer.setCompletionPrefix(completionPrefix)
				popup.setCurrentIndex(self.completer.completionModel().index(0, 0))
			
			# If we press Ctrl + Space we change the state
			if isShortcut:
				# Insert directly if it's just 1 possibility
				if self.enableACInstant and self.completer.completionCount() == 1:
					self.insertCompletion(self.completer.currentCompletion())
					popup.hide()
					self.autoCompleteState = BPCAutoCompleter.STATE_SEARCHING_SUGGESTION
					return
				else:
					self.autoCompleteState = BPCAutoCompleter.STATE_OPENED_BY_USER
			else:
				# Is the prefix equal to the first suggestion? If so, hide the popup.
				if self.completer.currentCompletion() == completionPrefix:
					popup.hide()
					self.autoCompleteState = BPCAutoCompleter.STATE_SEARCHING_SUGGESTION
					return
			
			# Current state
			if 	(
					self.autoSuggestion
					and
					(
						self.autoCompleteState == BPCAutoCompleter.STATE_SEARCHING_SUGGESTION or
						self.autoCompleteState == BPCAutoCompleter.STATE_OPENED_AUTOMATICALLY
					)
				):
				# Adding any text?
				eventText = event.text()
				
				# Hide if necessary
				if popup.isHidden() and (not eventText):
					return
				else:
					if (not completionPrefix) and charBeforeWord != ".":
						popup.hide()
						return
				
				# Auto suggestion worth it?
				if charBeforeWord != ".":
					# (not self.completer.memberListActivated()) and 
					autoCompleteAintWorthIt = (
						(
							completionPrefixLen < self.autoSuggestionMinChars
						)
						or
						(
							len(self.completer.currentCompletion()) - completionPrefixLen < self.autoSuggestionMinCompleteChars
							and
							not completionPrefix in self.completer.bpcModel.shortCuts
						)
						or
						(
							self.completer.completionCount() > self.autoSuggestionMaxItemCount
						)
					)
					if autoCompleteAintWorthIt:
						#if len(self.completer.currentCompletion()) - completionPrefixLen < 2:
						self.autoCompleteState = BPCAutoCompleter.STATE_SEARCHING_SUGGESTION
						popup.hide()
						return
					#elif popup.isHidden():
					#	# Ok so AC popup would be worth it...now check for how many characters the popup would be visible
					#	if 	(
					#			len(self.completer.currentCompletion()) <
					#			(
					#				self.autoSuggestionMinChars +
					#				self.autoSuggestionMinCompleteChars +
					#				self.autoSuggestionTypedChars
					#			)
					#		):
					#		return
				
				# Change state
				self.autoCompleteState = BPCAutoCompleter.STATE_OPENED_AUTOMATICALLY
			elif self.autoCompleteState == BPCAutoCompleter.STATE_OPENED_BY_USER:
				pass
			
			# Pop it up!
			cr = self.cursorRect()
			cr.setWidth(popup.sizeHintForColumn(0) + popup.verticalScrollBar().sizeHint().width())
			self.completer.complete(cr)
			
		# Unindent
		elif event.key() == QtCore.Qt.Key_Backtab: # Seriously f*** *** whoever invented Backtab instead of shift modifier + tab
			self.unIndentSelection()
			
		# Disable wrong indentation
		elif event.key() == QtCore.Qt.Key_Tab:
			if self.textCursor().hasSelection():
				if event.modifiers() == QtCore.Qt.ShiftModifier:
					self.unIndentSelection()
				else:
					self.indentSelection()
			else:
				cursor = self.textCursor()
				pos = cursor.position()
				block = self.qdoc.findBlock(pos)
				prevBlock = block.previous()
				
				line = block.text()
				tabLevel = countTabs(line)
				prevLine = prevBlock.text()
				prevTabLevel = countTabs(prevLine)
				
				if not prevLine or tabLevel <= prevTabLevel or not line[:pos - block.position()].isspace():
					super().keyPressEvent(event)
		
		# Auto Indent
		elif event.key() == QtCore.Qt.Key_Return:
			cursor = self.textCursor()
			
			pos = cursor.position()
			block = self.qdoc.findBlock(pos)
			blockPos = block.position()
			lineInfo = block.userData()
			line = block.text()
			tabLevel = countTabs(line)
			
			isAtEndOfLine = (blockPos + len(line) == pos)
			
			nodeName = ""
			if lineInfo:
				node = lineInfo.node
				if node and node.nodeType != Node.TEXT_NODE:
					nodeName = node.tagName
			else:
				node = None
			
			# Retrieve the keyword from the line
			pureLine = line[tabLevel:]
			keyword = ""
			i = 0
			for c in pureLine:
				if not c.isalnum() and not c == '_' or i == (pos - blockPos):
					keyword = pureLine[:i]
					break
				i += 1
			
			# Whole line
			wasFullLine = False
			if not keyword:
				keyword = pureLine
				wasFullLine = True
			
			keywordStaysAfterNewline = (pos >= blockPos + len(keyword)) #isAtEndOfLine
			
			if keyword and keywordStaysAfterNewline and not keyword[0] == '#' and nodeName != "extern-function":
				if (pos - blockPos != 0) and (not line[:pos - blockPos].isspace()):
					#print(nodeName)
					# Indent it?
					if keyword in self.autoIndentKeywords:
						tabLevel += 1
					elif (nodeName in functionNodeTagNames or nodeName == "class" or nodeName == "new"):
						if node.hasAttribute("implemented"):
							impl = node.getAttribute("implemented")
							if impl == "true":
								tabLevel += 1
						else:
							tabLevel += 1
					elif keyword == "init" and tabLevel == 1:
						tabLevel += 1
					#else:
					#	topLevelFuncExists = self.bpIDE.processor.getFirstDTreeByFunctionName(keyword)
					#	if not topLevelFuncExists:
					#		tabLevel += 1
						# isTopLevelFuncDefinition = (node is not None and node.parentNode.parentNode.tagName == "module")
						# isClassFunction = (self.updater is not None) and (self.updater.lastException is not None)
						# topLevelFuncExists = self.bpIDE.processor.getFirstDTreeByFunctionName(keyword)
						# if (
							# (wasFullLine or addBrackets(pureLine)[-1] == ')')
							# and tabLevel <= 1
							# and isAtEndOfLine
							# and line and line[-1] != ')'
							# and (isTopLevelFuncDefinition or isClassFunction)
							# and (not topLevelFuncExists) or (isClassFunction)
							# ):
							
						# TODO: Check whether parameters hold variable names only
						# If the parameters have numbers then this won't be a function definition
							# tabLevel += 1
			
			# Add the text
			cursor.beginEditBlock()
			cursor.insertText("\n" + "\t" * (min(tabLevel, pos - blockPos)))
			cursor.endEditBlock()
			
			event.accept()
		# TODO: Binary and ?
		#elif event.key() == QtCore.Qt.Key_Space and event.modifiers() == QtCore.Qt.ControlModifier:
		#	print("Yo!")
		else:
			super().keyPressEvent(event)
	
	def processSelection(self, func, startOffset):
		cursor = self.textCursor()
		cursor.beginEditBlock()
		
		# Previous selection
		selStart = cursor.selectionStart()
		selEnd = cursor.selectionEnd()
		
		selStartBlockPosition = self.qdoc.findBlock(selStart).position()
		
		cursor.setPosition(selEnd, QtGui.QTextCursor.MoveAnchor)
		blockEnd = cursor.blockNumber()
		
		cursor.setPosition(selStartBlockPosition, QtGui.QTextCursor.MoveAnchor)
		
		offsets = 0
		
		while cursor.blockNumber() <= blockEnd:
			#print(str(cursor.blockNumber()) + " / " + str(blockEnd))
			
			nOffset = func(cursor)
			
			if offsets == 0:
				startOffset = nOffset
			
			offsets += nOffset
			
			oldLineNumber = cursor.blockNumber()
			
			cursor.movePosition(QtGui.QTextCursor.NextBlock, QtGui.QTextCursor.MoveAnchor)
			cursor.movePosition(QtGui.QTextCursor.StartOfBlock, QtGui.QTextCursor.MoveAnchor)
			
			# Detect endless loop
			if cursor.blockNumber() == oldLineNumber:
				break
		
		# Restore old selection
		cursor.setPosition(selStart + startOffset, QtGui.QTextCursor.MoveAnchor)
		cursor.setPosition(selEnd + offsets, QtGui.QTextCursor.KeepAnchor)
		
		cursor.endEditBlock()
		self.setTextCursor(cursor)
		
		# Rehighlight
		#self.rehighlightFunctionUsage()
	
	def indentSelection(self):
		self.processSelection(self.indentLine, 1)
	
	def unIndentSelection(self):
		self.processSelection(self.unIndentLine, -1)
	
	def toggleCommentsSelection(self):
		self.processSelection(self.toggleCommentLine, 0)
	
	def indentLine(self, cursor):
		cursor.insertText("\t")
		return 1
		
	def unIndentLine(self, cursor):
		line = cursor.block().text()
		
		if line and line[0].isspace():
			cursor.deleteChar()
			return -1
		else:
			return 0
	
	def toggleCommentLine(self, cursor):
		line = cursor.block().text()
		
		if line and line[0] == '#':
			cursor.deleteChar()
			
			# Remove space as well
			if len(line) > 1 and line[1].isspace():
				cursor.deleteChar()
				return -2
			else:
				return -1
		else:
			cursor.insertText('# ')
			return 2
	
	def clearHighlights(self):
		self.setExtraSelections([])
	
	def getCurrentTheme(self):
		return self.bpIDE.getCurrentTheme()
	
	def rehighlightFunctionUsage(self):
		if self.isTextFile:
			return
		
		# TODO: Only highlight blocks where the function is used
		self.startBenchmark("[%s] Syntax Highlighter" % (stripDir(self.filePath)))
		self.highlighter.rehighlight()
		self.endBenchmark()
		
	def rehighlightCurrentLine(self):
		#print("Rehighlight current line")
		self.highlighter.rehighlightBlock(self.textCursor().block())
	
	def save(self, newPath = "", msgStatusBar = False):
		oldPath = self.getFilePath()
		
		try:
			if newPath:
				if self.isTextFile:
					self.setFilePath(newPath)
				else:
					if not newPath.endswith(".flua"):
						newPath = stripExt(newPath) + ".flua"
					self.setFilePath(newPath)
					
					if oldPath != newPath and self.bpIDE.processor:
						self.bpIDE.processor.changeCompiledFilePath(oldPath, newPath)
			
			if self.isTextFile:
				with codecs.open(self.getFilePath(), "w", encoding="utf-8") as outStream:
					outStream.write(self.toPlainText())
			else:
				if self.bpcFile:
					self.bpcFile.writeToFS()
				else:
					raise "No bpc data"
			
			# Success
			self.qdoc.setModified(False)
			
			if msgStatusBar:
				self.bpIDE.statusBar.showMessage("Saved " + self.getFilePath() + " successfully.", 1000)
		except:
			self.setFilePath(oldPath)
			
			if msgStatusBar:
				self.bpIDE.statusBar.showMessage("Error saving " + newPath, 3000)
		
	# Sets the language environment
	def setEnvironment(self, environment):
		if environment == self.environment:
			return
		
		self.environment = environment
		self.highlighter = GenericHighlighter(self.environment, self.qdoc, self.bpIDE)
		
		#if not extractExt(self.filePath) in environment.fileExtensions:
		#	self.setFilePath(stripExt(self.filePath) + environment.standardFileExtension)
		
		if environment == self.bpIDE.fluaEnvironment:
			self.isTextFile = False
			text = self.toPlainText()
			self.setPlainText("")
			self.setPlainText(text)
			self.runUpdater()
		else:
			self.isTextFile = True
		
		self.highlighter.rehighlight()
		
		if self.bubble:
			self.bubble.setEnvironment(environment)
		
		self.setCompleter(self.completer)
	
	def setFileExtension(self, ext):
		self.setFilePath(stripExt(self.filePath) + ext)
	
	def setFilePath(self, filePath):
		self.filePath = fixPath(filePath)
		
		# Environment
		env = self.bpIDE.getEnvironmentByFilePath(self.filePath)
		self.setEnvironment(env)
		
		if self.bpcFile:
			self.bpcFile.setFilePath(self.filePath)
		
		if not self.docNavigator:
			if self.isDocFile():
				self.docNavigator = BPDocNavigator(self)
				self.resizeDocNavigator()
		else:
			if not self.isDocFile():
				self.docNavigator.hide()
			else:
				self.docNavigator.show()
		
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
	
	# def setLineEdited(self, index, edited):
		# block = self.qdoc.findBlockByNumber(index)
		# lineInfo = block.userData()
		# if lineInfo:
			# block.setUserData(BPLineInformation(lineInfo.node, True, lineInfo.oldNode))
		
	def onTextChange(self, position, charsRemoved, charsAdded):
		# blockStart = self.qdoc.findBlock(position)
		# blockEnd = self.qdoc.findBlock(position + charsAdded)
		# for i in range(blockStart.blockNumber(), blockEnd.blockNumber() + 1):
			# #print("Update user data for line: " + str(block.text()))
			# self.setLineEdited(i, True)
		
		# Run bpc -> xml updater
		#print(self.disableUpdatesFlag)
		self.bpIDE.backgroundCompileIsUpToDate = False
		self.bpIDE.somethingModified = True
		
		# Only invalidate the data if this code edit is not a code bubble
		if (self.bubble) and (charsAdded or charsRemoved):
			#print("%d chars added / %d chars removed!" % (charsAdded, charsRemoved))
			self.backgroundCompilerOutstandingTasks += 1
			self.ppOutstandingTasks += 1
		
		if self.updater and not self.disableUpdatesFlag:
			self.runUpdater()
		
	def runUpdater(self):
		if self.isTextFile:
			return
		
		self.updateQueue.append(1)
		if self.openingFile:
			self.onUpdateTimeout()
		
	def onUpdateTimeout(self):
		if self.isTextFile:
			return
		
		if self.updateQueue:
			#print("onUpdateTimeout: got some work")
			self.updateQueue.clear()
			self.updater.setDocument(self.qdoc)
			
			if self.threaded:
				self.updater.startWith()
			else:
				self.updater.run()
				self.updater.finished.emit()
		
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
		if self.updater.bpcFile:
			del self.bpcFile
			self.bpcFile = self.updater.bpcFile
			self.updater.bpcFile = None
		
		#self.disableUpdatesFlag = True
		
		if self.bpcFile:
			self.doc = self.bpcFile.doc
			#self.bpIDE.startBenchmark("UpdateRootSafely")
			self.updateRootSafely()
			#self.bpIDE.endBenchmark()
			
			self.bpIDE.runPostProcessor(self)
		
		# Message view
		self.msgView.updateViewParser()
		
		# Highlight if needed
		if self.updater.lastException:
			# IMPORTANT: If an exception occured, editing should be able to run the updater again!
			ce = self.updater.codeEdit
			if ce and ce.disableUpdatesFlag:
				ce.disableUpdatesFlag = False
				ce.highlighter.rehighlight()
		
		# Any work in the queue left?
		interval = self.updater.executionTime + self.bpIDE.config.updateInterval
		if self.updateQueue and abs(self.timer.interval() - interval) > 400:
			print("Setting new update interval: %d ms" % (interval))
			self.timer.setInterval(interval)
		
	def getCurrentLine(self):
		lineIndex = self.getLineIndex()
		return self.qdoc.findBlockByNumber(lineIndex).text()
		
	def updateRootSafely(self):
		lineIndex = -1 # -1 because of flua.Core
		for node in self.bpcFile.nodes:
			#print("[%d] %s" % (lineIndex, node))
			if lineIndex >= 0:
				block = self.qdoc.findBlockByNumber(lineIndex)
				
				oldNode = None
				oldData = block.userData()
				if oldData:
					oldNode = oldData.node
					# Meta data
					if oldNode and oldNode.nodeType != Node.TEXT_NODE and oldNode.tagName in metaDataForNodeName:
						metaNode = getElementByTagName(oldNode, "meta")
						if metaNode and node and node.nodeType == Node.ELEMENT_NODE and node.tagName == oldNode.tagName:
							node.appendChild(metaNode)
					
					#oldData.oldNode = oldData.node
					#oldData.node = node
				#else:
				del oldData
				block.setUserData(BPLineInformation(node, False, oldNode))
				#self.setLineNode(lineIndex, node)
			lineIndex += 1
		
		#del self.root
		self.root = self.bpcFile.root
		
		#del self.bpcFile.root
		#del self.bpcFile.doc
		#del self.bpcFile.nodeToOriginalLine
		#del self.bpcFile.nodes
		
	def setRoot(self, newRoot):
		self.root = newRoot
		#header = getElementByTagName(self.root, "header")
		codeNode = getElementByTagName(self.root, "code")
		
		converter = LineToNodeConverter()
		bpcCode = nodeToBPC(self.root, 0, converter).strip()
		self.lines = bpcCode.split("\n")
		
		# Set new text
		self.disableUpdatesFlag = True
		code = "\n".join(self.lines) + "\n"
		
		# Fixes a bug in QTextDocument for the modification state
		#if not code:
		#	code = "\n"
		
		self.setPlainText(code)
		
		# Set user data
		lineToNodeLen = len(converter.lineToNode)
		
		for i in range(len(self.lines)):
			if i < lineToNodeLen and converter.lineToNode[i]:
				#print(self.lines[i] + " >>> " + converter.lineToNode[i].toxml())
				userData = BPLineInformation(converter.lineToNode[i])
			else:
				userData = BPLineInformation()
			self.qdoc.findBlockByNumber(i).setUserData(userData)
		
		self.runUpdater()
		
	# Sets the Flua XML code
	def setXML(self, xmlCode):
		self.disableUpdatesFlag = True
		
		self.doc = parseString(xmlCode.encode("utf-8"))
		#print(self.doc.toprettyxml())
		
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
		#self.cursorPositionChanged.connect(self.highlightCurrentLine)
		
		self.updateLineNumberAreaWidth(0)
		#self.highlightLine()
	
	def highlightLine(self, lineIndex = 0, lineColor = None):
		if not lineColor:
			lineColor = self.getCurrentTheme()["current-line"]
		
		#if(not self.isReadOnly()):
		self.highlightLineSelection.format.setBackground(lineColor)
		if lineIndex:
			self.highlightLineSelection.cursor.setPosition(self.qdoc.findBlockByLineNumber(lineIndex).position())
		self.highlightLineSelection.cursor.clearSelection()
		
		self.setExtraSelections(self.getActiveExtraSelections())
		
	def isDocFile(self):
		if self.isTextFile:
			return False
		
		fileName = stripAll(self.getFilePath())
		
		isDoc = (len(fileName) >= 4 and fileName[:2].isdigit() and self.bubble is not None)
		return isDoc
		
	def resizeEvent(self, event):
		super().resizeEvent(event)
		
		if self.lineNumberArea:
			cr = self.contentsRect()
			self.lineNumberArea.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.getLineNumberAreaWidth(), cr.height()))
		
		if self.bubble:
			self.resizeBubble()
		
		self.resizeDocNavigator()
	
	def resizeDocNavigator(self):
		if self.docNavigator:
			self.docNavigator.setGeometry(self.width() / 1.5 - self.docNavigator.customWidth / 2 - 7, self.height() - self.docNavigator.customHeight - 21, self.docNavigator.customWidth, self.docNavigator.customHeight)
	
	BUBBLE_MARGIN = 18
	BUBBLE_MARGIN_HALF = BUBBLE_MARGIN / 2
	
	def adjustBubbleSize(self):
		self.bubble.document().adjustSize()
		newHeight = (self.bubble.document().size().height()) * (self.bubble.fontMetrics().height()) + BPCodeEdit.BUBBLE_MARGIN_HALF
		
		if self.bubble.y() + newHeight >= self.height():
			newHeight = self.height() - self.bubble.y() - BPCodeEdit.BUBBLE_MARGIN
			self.bubble.verticalScrollBar().show()
		else:
			self.bubble.verticalScrollBar().hide()
		
		# min(self.bubbleWidth, self.bubble.document().size().width() + 24)
		self.resizeBubble(self.bubbleWidth, newHeight)
	
	def resizeBubble(self, width = -1, height = -1):
		margin = BPCodeEdit.BUBBLE_MARGIN
		
		if width == -1:
			width = self.bubbleWidth
		
		if height == -1:
			height = self.bubble.height()
		
		msgViewHeight = self.msgView.height()
		
		# Resize msg view as well
		offX = self.width() - self.msgViewWidth - margin
		self.msgView.setGeometry(offX, margin, self.msgViewWidth, msgViewHeight)
		
		# Docs
		offX = self.width() - width - margin
		
		offY = msgViewHeight + margin * 2
		if not (offY > self.bubble.y() or self.bubble.y() - offY > self.bubbleMinMovePx):
			offY = self.bubble.y()
		
		self.bubble.setGeometry(offX, offY, width, height)
		
	def getLineNumberAreaWidth(self):
		digits = 1
		maxBlocks = max(1, self.blockCount())
		while maxBlocks >= 10:
			maxBlocks //= 10
			digits += 1
		
		space = 24 + self.fontMetrics().width('9') * digits
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
		
	def lineNumberAreaPaintEvent(self, event):
		style = self.bpIDE.getCurrentTheme()
		
		painter = QtGui.QPainter(self.lineNumberArea)
		painter.fillRect(event.rect(), QtGui.QColor("#242424"))
		
		numberColor = QtGui.QColor("#777777")
		
		#if self.bubble:
		#	topOffset = 0
		#	heightOffset = 0
		#else:
		#	topOffset = 3
		#	heightOffset = 2
		
		block = self.firstVisibleBlock()
		blockNumber = block.blockNumber()
		top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top() #- topOffset
		bottom = top + self.blockBoundingRect(block).height()
		resultingHeight = self.fontMetrics().height() #+ heightOffset
		resultingWidth = self.lineNumberArea.width()
		
		oldFont = self.font()
		#self.setFont(self.lineNumberFont)
		painter.setFont(oldFont)
		
		while block.isValid() and top <= event.rect().bottom():
			if block.isVisible() and bottom >= event.rect().top():
				number = str(blockNumber + 1)
				painter.setPen(numberColor)
				#painter.drawText(0, top, resultingWidth, resultingHeight, QtCore.Qt.AlignHCenter, number)
			
			block = block.next()
			top = bottom
			bottom = top + int(self.blockBoundingRect(block).height())
			blockNumber += 1
			
		self.setFont(oldFont)

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
