####################################################################
# Header
####################################################################
# Syntax:   Flua Code
# Author:   Eduard Urbach

####################################################################
# License
####################################################################
# (C) 2008  Eduard Urbach
# 
# This file is part of Flua.
# 
# Flua is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Flua is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Flua.  If not, see <http://www.gnu.org/licenses/>.

####################################################################
# Imports
####################################################################
from flua.Compiler.Utils import *
from flua.Compiler.Config import *
from flua.Compiler.Input.bpc.BPCUtils import *
import codecs

####################################################################
# Variables
####################################################################
# XML tags which can follow another tag
# Used by BPC -> XML compiler

# 2 levels
blocks = {
	"if-block" : ["else-if", "else"],
	"try-block" : ["catch"]
}

# 1 level
simpleBlocks = {
	"class" : [],
	"function" : [],
	"while" : [],
	"for" : [],
	"foreach" : [],
	"parallel-for" : [],
	"in" : [],
	"on" : [],
	"switch" : [],
	"case" : [],
	"target" : [],
	"extern" : [],
	"compiler-flags" : [],
	"template" : [],
	"get" : [],
	"set" : [],
	"private" : [],
	"cast-definition" : [],
	"getter" : [],
	"setter" : [],
	"operators" : [],
	"operator" : [],
	"iterators" : [],
	"iterator-type" : [],
	"casts" : [],
	"namespace" : [],
	"define" : [],
	"extends" : [],
	"parallel" : [],
	"begin" : [],
	"shared" : [],
	"const" : [],
	"atomic" : [],
	"public" : [],
	"test" : [],
	"interface" : [],
	"implements" : [],
}

def addGenerics(line):
	bracketCounter = 0
	char = ''
	startGeneric = -1
	lineLen = len(line)
	i = 0
	#oldLine = line
	
	#for i in range(len(line)):
	while i < lineLen:
		char = line[i]
		
		if char == '<':
			bracketCounter += 1
			if bracketCounter == 1:
				startGeneric = i
		elif char == '>':
			bracketCounter -= 1
			
			# End of template parameter
			if bracketCounter == 0:
				templateParam = addGenerics(line[startGeneric+1:i])
				line = line[:startGeneric] + "§(" + templateParam + ")" + line[i+1:]
				
				i += 1
				lineLen = len(line)
				
		elif bracketCounter > 0 and char != '~' and char != ',' and (not char.isspace()) and ((not isVarChar(char)) or char == '.'):
			break
		
		i += 1
		#if oldLine != line:
		#	print(char)
		#	print("Start: " + oldLine)
		#	print("End: " + line)
			
	#print("End addGenerics()")
	return line

def addBrackets(line):
	bracketCounter = 0
	char = ''
	
	for i in range(len(line)):
		char = line[i]
		
		if char == '(' or char == '[':
			bracketCounter += 1
		elif char == ')' or char == ']':
			bracketCounter -= 1
		elif (not isVarChar(char)) and char != '.' and bracketCounter == 0:
			break
	
	identifier = line[:i]
	if char == '.':
		if identifier:
			raise CompilerException("You need to specify a function or property of „%s“" % (identifier))
		else:
			raise CompilerException("Invalid instruction: „%s“" % line)
	# A simple array index without any other calls
	elif char == ']':
		return line
	# Multiple return values
	elif char == ',':
		# TODO: Do this properly instead of quick hacks.
		pos = line.find("=")
		params = line[:pos]
		return "(%s)%s" % (params, line[pos:])
	
	rightOperand = line[i+1:]
	if isDefinitelyOperatorSign(char):
		if (not identifier or not rightOperand):
			#print(line, "|", identifier, "|", rightOperand)
			raise CompilerException("Invalid instruction: „%s“" % line)
	
	# Don't make function calls out of data flow
	if rightOperand.startswith("<-") or rightOperand.startswith("->") or rightOperand.startswith("<->") or rightOperand.startswith("→") or rightOperand.startswith("←"):
		return line
	
	if i < len(line) - 1:
		nextChar = rightOperand[0]
		
		if char.isspace() and (isVarChar(nextChar) or nextChar == '(' or (nextChar == '-' and len(rightOperand) > 1 and rightOperand[1] != "=")):
			line = "%s(%s)" % (line[:i], rightOperand)
	elif line[-1] != ')':
		line += "()"
	
	return line

####################################################################
# Classes
####################################################################
class BPCFile(ScopeController, Benchmarkable):
	def __init__(self, compiler, fileIn, isMainFile, perLineCallBack = None):
		ScopeController.__init__(self)
		Benchmarkable.__init__(self)
		
		import flua.Compiler.Input.bpc.BPCUtils as bpcUtils
		self.currentSyntax = bpcUtils.currentSyntax
		
		self.compiler = compiler
		self.file = fileIn
		self.dir = os.path.dirname(fileIn) + "/"
		#print(fileIn, " -> ", self.dir)
		
		self.perLineCallBack = perLineCallBack
		
		self.stringCount = 0
		self.importedFiles = []
		self.nextLineIndented = False
		self.savedNextNode = 0
		self.lastAccessNode = None
		#self.idCount = 1
		
		pureFileName = stripAll(fileIn)
		if pureFileName == "Mutable":
			self.classPrefix = "Mutable"
		elif pureFileName == "Immutable":
			self.classPrefix = "Immutable"
		else:
			self.classPrefix = ""
		
		self.inClass = 0
		self.inSwitch = 0
		self.inCase = 0
		self.inExtern = 0
		self.inExtends = 0
		self.inImplements = 0
		self.inTemplate = 0
		self.inFunction = 0
		self.inGetter = 0
		self.inSetter = 0
		self.inCasts = 0
		self.inOperators = 0
		self.inOperator = 0
		self.inIterators = 0
		self.inAtomic = 0
		self.inRequire = 0
		self.inEnsure = 0
		self.inMaybe = 0
		self.inTest = 0
		self.inConst = 0
		self.inIfBlock = 0
		self.inTryBlock = 0
		self.inCompilerFlags = 0
		self.inPublic = 0
		self.inInterface = 0
		
		self.parser = self.compiler.parser
		self.isMainFile = isMainFile
		self.doc = parseString("<module><header><title/><dependencies/><strings/></header><code></code></module>".encode( "utf-8" ))
		self.root = self.doc.documentElement
		self.header = getElementByTagName(self.root, "header")
		self.dependencies = getElementByTagName(self.header, "dependencies")
		self.strings = getElementByTagName(self.header, "strings")
		self.lastLine = ""
		self.lastLineCount = 0
		self.maxLineIndex = -1
		self.currentLineComment = ""
		self.nodeToOriginalLine = dict()
		self.nodeToOriginalLineNumber = dict()
		self.nodes = list()
		
		# This is used for xml tags which have a "code" node
		self.nextNode = 0
		
		self.buildXMLTree = self.parser.buildXMLTree
		self.adjustXMLTree = self.parser.adjustXMLTree
		self.parseExprNoCache = self.parser.buildXMLTree
		self.keywordToHandler = {
			"atomic" : self.handleAtomic,
			"assert" : self.handleAssert,
			"break" : self.handleBreak,
			"to" : self.handleCasts,
			"catch" : self.handleCatch,
			"begin" : self.handleBegin,
			"compilerflags" : self.handleCompilerFlags,
			"const" : self.handleConst,
			"continue" : self.handleContinue,
			"define" : self.handleDefine,
			"elif" : self.handleElif,
			"else" : self.handleElse,
			"ensure" : self.handleEnsure,
			"extends" : self.handleExtends,
			"extern" : self.handleExtern,
			"for" : self.handleFor,
			"get" : self.handleGet,
			"if" : self.handleIf,
			"import" : self.handleImport,
			"implements" : self.handleImplements,
			"in" : self.handleIn,
			"include" : self.handleInclude,
			"interface" : self.handleInterface,
			"iterator" : self.handleIteratorBlock,
			#"maybe" : self.handleMaybe,
			"namespace" : self.handleNamespace,
			"..." : self.handleNOOP,
			"on" : self.handleOn,
			"operator" : self.handleOperatorBlock,
			"parallel" : self.handleParallel,
			"pfor" : self.handleFor,
			"private" : self.handlePrivate,
			"public" : self.handlePublic,
			"require" : self.handleRequire,
			"return" : self.handleReturn,
			"set" : self.handleSet,
			"shared" : self.handleShared,
			"switch" : self.handleSwitch,
			"target" : self.handleTarget,
			"template" : self.handleTemplate,
			"test" : self.handleTest,
			"throw" : self.handleThrow,
			"try" : self.handleTry,
			"while" : self.handleWhile,
			"yield" : self.handleYield,
			
			# For Python support
			"def" : self.handleFunction,
			"class" : self.handleClass,
		}
		
	#def __del__(self):
	#	del self.nodeToOriginalLine
	#	del self.nodes
	#	del self.doc
		
	def writeToFS(self):
		#fileOut = dirOut + stripExt(bpcFile.file[len(self.projectDir):]) + ".flua"
		#fileOut = dirOut + stripAll(bpcFile.file) + ".flua"
		fileOut = stripExt(self.file) + ".flua"
		#print("Writing XML to " + fileOut)
		
		# Directory structure
		#concreteDirOut = os.path.dirname(fileOut)
		#if not os.path.isdir(concreteDirOut):
		#	os.makedirs(concreteDirOut)
		
		with codecs.open(fileOut, "w", encoding="utf-8") as outStream:
			outStream.write(self.root.toprettyxml())
		
	def getRoot(self):
		return self.root
		
	def getFilePath(self):
		return self.file
	
	def getFileName(self):
		return self.file[len(self.dir):]
	
	def getDirectory(self):
		return self.dir
		
	def getLastLine(self):
		return self.lastLine
	
	def getLastLineCount(self):
		return self.lastLineCount
		
	def setFilePath(self, path):
		self.file = path
		
	def checkObjectCreation(self, node):
		if tagName(node) == "call":
			funcNode = getElementByTagName(node, "function")
			#print(node.toprettyxml())
			#print(self.exprCache)
			funcNameNode = funcNode.childNodes[0]
			#print(funcNameNode.toxml())
			# Template call
			if (funcNameNode.nodeType != Node.TEXT_NODE):
				# Namespaces
				if funcNameNode.tagName == "access":
					funcName = funcNameNode.childNodes[1].childNodes[0].nodeValue
				else:
					funcName = funcNameNode.childNodes[0].childNodes[0].nodeValue
				
				if funcName and funcName[0].isupper():
					node.tagName = "new"
					funcNode.tagName = "type"
			elif funcNameNode.nodeValue and funcNameNode.nodeValue[0].isupper():
				node.tagName = "new"
				funcNode.tagName = "type"
		# Correct nodes
		elif node.nodeType == Node.TEXT_NODE:
			if self.currentSyntax == SYNTAX_CPP and node.nodeValue == "this":
				node.nodeValue = "my"
			elif self.currentSyntax in {SYNTAX_RUBY, SYNTAX_PYTHON} and node.nodeValue == "self":
				node.nodeValue = "my"
		
		for child in node.childNodes:
			self.checkObjectCreation(child)
		
	def parseExpr(self, line):
		inExprCache = line in self.compiler.exprCache
		
		if not inExprCache and not line in self.compiler.textNodeCache:
			node = self.buildXMLTree(line)
			self.checkObjectCreation(node)
			
			if node.nodeType != Node.TEXT_NODE:
				# WE NEED TO CONVERT IT TO XML BECAUSE CLONENODE IS BUGGED (and slower)
				self.compiler.exprCache[line] = node.toxml()
			else:
				self.compiler.textNodeCache[line] = node
			
			return node
			
		if inExprCache:
			# Element node - WE NEED TO RE-PARSE IT BECAUSE PYTHON'S CLONENODE IS BUGGED
			#node = self.cloneRecursively(self.compiler.exprCache[line]) 
			node = parseString(self.compiler.exprCache[line]).documentElement
			
			# This is actually slower...
			#original = self.compiler.exprCache[line]
			#node = original.cloneNode(True)
			#self.adjustTagNames(node, original)
		else:
			# Text node
			node = self.compiler.textNodeCache[line].cloneNode(False)
		
		return node
		
	def adjustTagNames(self, cloned, original):
		if original.nodeType == Node.ELEMENT_NODE and cloned.tagName != original.tagName:
			cloned.tagName = original.tagName
		
		# Recursive
		adjXMLTree = self.adjustTagNames
		for i in range(len(original.childNodes)):
			adjXMLTree(cloned.childNodes[i], original.childNodes[i])
		
	def cloneRecursively(self, node):
		cloned = node.cloneNode(True)
		self.adjustTagNames(cloned, node)
		
		#print("Original: " + node.toxml())
		#print("Cloned:   " + cloned.toxml())
		
		return cloned
		
	def compile(self, codeText = None):
		#print("Compiling: " + self.file)
		
		currentLine = None
		self.currentNode = getElementByTagName(self.root, "code")
		self.lastNode = None
		
		# Read
		if codeText is None:
			with codecs.open(self.file, "r", "utf-8") as inStream:
				codeText = inStream.read()
			
			# TODO: Remove all BOMs
			if len(codeText) and codeText[0] == '\ufeff': #codecs.BOM_UTF8:
				codeText = codeText[1:]
		
		self.lastLineCount = -1	# -1 because of "import flua.Core"
		lines = ["import flua.Core"] + codeText.split('\n') + ["..."]
		self.maxLineIndex = len(lines) - 1
		del codeText
		
		#if "unicode" in self.file:
		#	print(lines)
		tabCount = 0
		prevTabCount = 0
		
		# Local variables for faster lookups
		prepareLine = self.prepareLine
		processLine = self.processLine
		registerNode = self.registerNode
		tabBack = self.tabBack
		perLineCallBack = self.perLineCallBack
		
		# Go through every line -> build the structure
		for lineIndex in range(0, len(lines)):
			line = lines[lineIndex]
			tabCount = countTabs(line)
			#line = line.rstrip()
			#line = line.lstrip()
			line = line.strip()
			
			# Set last line for exception handling
			self.lastLine = line
			self.lastLineCount += 1
			
			# Remove strings, comments and check brackets
			line = prepareLine(line)
			
			if not line and not self.currentLineComment:
				# Function block error checking
				if currentLine and currentLine.nodeType == Node.ELEMENT_NODE and ((currentLine.tagName in simpleBlocks) or currentLine.tagName in {"if-block", "try-block", "catch", "if", "elif", "else"}):
					codeNode = getElementByTagName(currentLine, "code")
					
					if (not self.inInterface) and ((not codeNode) or len(codeNode.childNodes) == 0): #and countTabs(lines[lineIndex + 1].rstrip()) <= tabCount:
						raise CompilerException("If you need an empty block use '...' inside the block")
				
				# If we didn't add a comment, add an empty entry
				if len(self.nodes) <= self.lastLineCount:
					self.nodes.append(None)
				
				continue
			
			self.nextLineIndented = False
			if lineIndex < len(lines) - 1:
				tabCountNextLine = countTabs(lines[lineIndex + 1])
				if tabCountNextLine == tabCount + 1: #and lines[lineIndex + 1].strip() != "":
					self.nextLineIndented = True
				elif tabCountNextLine > tabCount + 1:
					# Increase line count to have a correct line number for the error message
					self.lastLineCount += 1
					raise CompilerException("You only need to indent once.")
			
			# TODO: Enable all unicode characters
			#line = line.replace("π", "pi")
			
			# Remove whitespaces
			line = line.replace("\t", " ")
			while line.find("  ") != -1:
				line = line.replace("  ", " ")
			
			if tabCount < prevTabCount:
				savedCurrentNode = self.currentNode
				tabBack(currentLine, prevTabCount, tabCount, True)
				self.currentNode = savedCurrentNode
			
			#print(self.lastLineCount, self.maxLineIndex, line, self.inClass, self.inFunction)
			
			# Seriously.
			if (not self.nextLineIndented) and line.startswith("if java"):
				raise CompilerException("If Java had true garbage collection, most programs would delete themselves upon execution.")
			
			# Don't process last NOOP
			if self.lastLineCount == self.maxLineIndex:
				break
			
			# The actual compiling! Let's get it start-e-e-ed now!
			if line:
				currentLine = processLine(line)
			else:
				currentLine = None
			
			# Save the connection for debugging purposes
			#if self.nodes and (currentLine == None or self.nodes[-1] != currentLine):
			registerNode(currentLine)
			
			# Tab level hierarchy
			if tabCount > prevTabCount:
				if self.savedNextNode:
					self.currentNode = self.savedNextNode
					self.savedNextNode = 0
				else:
					self.currentNode = self.lastNode
			elif tabCount < prevTabCount:
				tabBack(currentLine, prevTabCount, tabCount, False)
			
			self.savedNextNode = self.nextNode
			
			# Comment-ception
			if self.currentLineComment:
				if line:
					currentComment = self.handleComment(self.currentLineComment, inline = True)
					
					# Do NOT append it to the line number -> node converter
					self.nodeToOriginalLine[currentComment] = self.lastLine
					self.nodeToOriginalLine[currentComment] = self.lastLineCount
				else:
					currentComment = self.handleComment(self.currentLineComment, inline = False)
					registerNode(currentComment)
					
				# Append to current node
				if self.currentNode:
					self.currentNode.appendChild(currentComment)
				else:
					raise CompilerException("Invalid indentation")
			else:
				currentComment = None
			
			# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
			# [ATTENTION]    WE PROUDLY PRESENT YOU: THE MAGICAL TOWER OF IF'S      #
			# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
			if currentLine:
				#if perLineCallBack:
				#	perLineCallBack()
				
				if currentLine.nodeType != Node.TEXT_NODE:
					currentLine.setAttribute("id", str(self.lastLineCount))
					currentLine.setAttribute("depth", str(tabCount))
					#self.idCount += 1
					if currentLine.tagName == "assign":
						variableNode = currentLine.childNodes[0].childNodes[0]
						if variableNode.nodeType == Node.TEXT_NODE:
							variable = variableNode.nodeValue
							if not variable in self.getCurrentScope().variables:
								self.getCurrentScope().variables[variable] = currentLine
				
				if not self.currentNode:
					raise CompilerException("„%s“ was indented and needs to be in a valid block" % self.lastLine)
				self.lastNode = self.currentNode.appendChild(currentLine)
			prevTabCount = tabCount
		
		del lines
		
	def tabBack(self, currentLine, prevTabCount, currentTabCount, countIns):
		# TODO: Optimize using dict search for nodeName
		atTab = prevTabCount
		while atTab > currentTabCount:
			if countIns:
				nodeName = self.currentNode.tagName
				if nodeName == "switch":
					self.inSwitch -= 1
				elif nodeName == "code":
					parentNodeName = self.currentNode.parentNode.tagName
					if parentNodeName == "class":
						self.inClass -= 1
					elif parentNodeName == "interface":
						self.inInterface -= 1
					elif parentNodeName == "operator":
						self.inOperator -= 1
					elif parentNodeName == "function":
						self.inFunction -= 1
				elif nodeName == "extern":
					self.inExtern -= 1
				elif nodeName == "template":
					self.inTemplate -= 1
				elif nodeName == "extends":
					self.inExtends -= 1
				elif nodeName == "implements":
					self.inImplements -= 1
				elif nodeName == "get":
					self.inGetter -= 1
				elif nodeName == "set":
					self.inSetter -= 1
				elif nodeName == "casts":
					self.inCasts = 0
				elif nodeName == "operators":
					self.inOperators -= 1
				elif nodeName == "public":
					self.inPublic -= 1
				elif nodeName == "iterators":
					self.inIterators -= 1
				elif nodeName == "atomic":
					self.inAtomic -= 1
				elif nodeName == "require":
					self.inRequire -= 1
				elif nodeName == "ensure":
					self.inEnsure -= 1
				elif nodeName == "maybe":
					self.inMaybe -= 1
				elif nodeName == "test":
					self.inTest -= 1
				elif nodeName == "const":
					self.inConst -= 1
				elif nodeName == "compiler-flags":
					self.inCompilerFlags -= 1
			
			self.currentNode = self.currentNode.parentNode
			
			if countIns:
				if self.currentNode.tagName == "case":
					self.inCase -= 1
			
			# XML elements with "code" tags need special treatment
			parent = self.currentNode.parentNode
			
			if parent != self.doc:
				if parent.tagName in blocks:
					tagsAllowed = blocks[parent.tagName]
					if atTab != currentTabCount + 1 or (currentLine and currentLine.nodeType == Node.TEXT_NODE) or (not currentLine or not currentLine.tagName in tagsAllowed):
						# Decrement if block stack counter
						if parent.tagName == "if-block" and self.currentNode.tagName == "else":
							self.inIfBlock -= 1
						elif parent.tagName == "try-block":
							self.inTryBlock += 1
						
						self.currentNode = parent.parentNode
					else:
						self.currentNode = parent
				elif self.currentNode.tagName in simpleBlocks and self.currentNode.tagName != "extern":
					tagsAllowed = simpleBlocks[self.currentNode.tagName]
					if atTab != currentTabCount + 1 or (currentLine and currentLine.nodeType == Node.TEXT_NODE) or (not currentLine or not currentLine.tagName in tagsAllowed):
						self.currentNode = parent
			
			atTab -= 1
		
	def processLine(self, line):
		if self.keyword in self.keywordToHandler:
			node = self.keywordToHandler[self.keyword](line)
			if node:
				self.checkObjectCreation(node)
			return node
		elif (self.inOperators) and self.inOperator == 0:
			#print(line)
			return self.handleFunction(line)
		elif self.nextLineIndented:
			if self.inSwitch > 0:
				return self.handleCase(line)
			elif self.inOperators or self.inCasts or line[0].islower() or self.inClass or self.inIterators:
				return self.handleFunction(line)
			else:
				return self.handleClass(line)
		else:
			if self.inTemplate:
				return self.handleTemplateParameter(line)
			
			if self.inImplements:
				return self.handleImplementsParameter(line)
			
			if self.inExtends:
				return self.handleExtendsParameter(line)
			
			if self.inCompilerFlags:
				return self.handleCompilerFlag(line)
			
			if self.inPublic > 0:
				return self.handlePublicMember(line)
			
			if self.inExtern and (not self.inClass):
				if self.inConst:
					return self.handleExternVariable(line)
				else:
					return self.handleExternLine(line)
			
			if self.inInterface:
				return self.handleFunction(line)
			
			if self.inClass and not (self.inFunction or self.inSetter or self.inGetter or self.inOperators or self.inIterators or self.inCasts):
				raise CompilerException("A class definition may not contain top-level executable code: „%s“" % (line))
			
			line = addBrackets(line)
			line = addGenerics(line)
			node = self.parseExpr(line)
			
			return node
	
	def registerNode(self, node):
		if len(self.nodes) <= self.lastLineCount:
			self.nodes.append(node)
			self.nodeToOriginalLine[node] = self.lastLine
			self.nodeToOriginalLineNumber[node] = self.lastLineCount
		
	def handleCase(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("case", line)
		
		node = self.doc.createElement("case")
		values = self.compiler.parser.getParametersNode(self.parseExpr(line))
		code = self.doc.createElement("code")
		
		values.tagName = "values"
		for value in values.childNodes:
			value.tagName = "value"
	
		node.appendChild(values)
		node.appendChild(code)
		
		self.inCase += 1
		self.nextNode = code
		return node
		
	def handleSwitch(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("switch", line)
		
		node = self.doc.createElement("switch")
		value = self.doc.createElement("value")
		value.appendChild(self.parseExpr(line[len("switch")+1:]))
		
		node.appendChild(value)
		
		self.inSwitch += 1
		self.nextNode = node
		return node
		
	def handleCasts(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("casts", line)
		
		node = self.doc.createElement("casts")
		
		self.inCasts = 1
		self.nextNode = node
		return node
		
	def handleGet(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("get", line)
		
		node = self.doc.createElement("get")
		
		expr = line[len("get"):].strip()
		if expr:
			params = self.parseExpr(expr)
			paramsNode = self.parser.getParametersNode(params)
			paramsNode.tagName = "default-get"
			node.appendChild(paramsNode)
		
		#code = self.doc.createElement("code")
		#node.appendChild(code)
		
		self.inGetter = 1
		self.nextNode = node
		return node
	
	def handleSet(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("set", line)
		
		node = self.doc.createElement("set")
		
		expr = line[len("set"):].strip()
		if expr:
			params = self.parseExpr(expr)
			paramsNode = self.parser.getParametersNode(params)
			paramsNode.tagName = "default-set"
			node.appendChild(paramsNode)
		
		#code = self.doc.createElement("code")
		#node.appendChild(code)
		
		self.inSetter = 1
		self.nextNode = node
		return node
	
	def handleOperatorBlock(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("operator", line)
		
		node = self.doc.createElement("operators")
		
		self.inOperators = 1
		self.nextNode = node
		return node
		
	def handleIteratorBlock(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("iterators", line)
		
		node = self.doc.createElement("iterators")
		
		self.inIterators = 1
		self.nextNode = node
		return node
		
	def handleTemplate(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("template", line)
		
		node = self.doc.createElement("template")
		
		self.inTemplate = 1
		self.nextNode = node
		return node
		
	def handleExtends(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("extends", line)
		
		node = self.doc.createElement("extends")
		
		self.inExtends = 1
		self.nextNode = node
		return node
		
	def handleImplements(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("implements", line)
		
		node = self.doc.createElement("implements")
		
		self.inImplements += 1
		self.nextNode = node
		return node
		
	def handleTemplateParameter(self, line):
		paramNode = self.parseExpr(line)
		
		if paramNode.nodeType == Node.ELEMENT_NODE and paramNode.tagName == "assign":
			paramNode.tagName = "parameter"
			paramNode.childNodes[0].tagName = "name"
			paramNode.childNodes[1].tagName = "default-value"
			return paramNode
		else:
			node = self.doc.createElement("parameter")
			node.appendChild(paramNode)
			return node
		
	def handleImplementsParameter(self, line):
		# parseExpr because of possible namespaces
		paramNode = self.parseExpr(line)
		
		node = self.doc.createElement("implements-interface")
		node.appendChild(paramNode)
		return node
		
	def handleExtendsParameter(self, line):
		# parseExpr because of possible namespaces
		paramNode = self.parseExpr(line)
		
		node = self.doc.createElement("extends-class")
		node.appendChild(paramNode)
		return node
		
	def handleIn(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("in", line)
		
		node = self.doc.createElement("in")
		expr = self.doc.createElement("expression")
		code = self.doc.createElement("code")
		expr.appendChild(self.parseExpr(line[len("in")+1:]))
		
		node.appendChild(expr)
		node.appendChild(code)
		
		self.nextNode = code
		return node
		
	def handleOn(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("on", line)
		
		node = self.doc.createElement("on")
		expr = self.doc.createElement("expression")
		code = self.doc.createElement("code")
		expr.appendChild(self.parseExpr(line[len("on")+1:]))
		
		node.appendChild(expr)
		node.appendChild(code)
		
		self.nextNode = code
		return node
		
	def handleNamespace(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("namespace", line)
		
		node = self.doc.createElement("namespace")
		expr = self.doc.createElement("name")
		code = self.doc.createElement("code")
		expr.appendChild(self.parseExpr(line[len("namespace")+1:]))
		
		node.appendChild(expr)
		node.appendChild(code)
		
		self.nextNode = code
		return node
		
	def handleFor(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("for", line)
		
		if len(line) < 5:
			raise CompilerException("You need to specify an iterator in „%s“" % (line))
		
		# Remove 'p' from pfor
		if line[0] == 'p':
			line = line[1:]
			parallel = True
		else:
			parallel = False
		
		if line[3] == '(':
			line = "for " + line[4:]
		elif line[4] == '(':
			line = "for " + line[5:]
		
		if self.currentSyntax == SYNTAX_CPP:
			line = line[:-1] # Remove ')'
		
		node = self.doc.createElement(["for", "parallel-for"][parallel])
		
		line += " "
		pos = line.find(" to ")
		posUntil = line.find(" until ")
		posCounting = line.find(" counting ")
		
		if pos == -1 and posUntil == -1:
			pos = line.find(" in ")
			if pos == -1:
				raise CompilerException("Missing iterator definition in 'for' expression")
			else:
				node.tagName = ["foreach", "parallel-foreach"][parallel]
				
				iterName = line[4:pos].strip()
				
				if posCounting == -1:
					iterCollection = line[pos+len(" in "):].strip()
					counterVar = ""
				else:
					iterCollection = line[pos+len(" in "):posCounting].strip()
					counterVar = line[posCounting + len(" counting "):]
				
				iterNameExpr = self.parseExpr(iterName)
				iterCollectionExpr = self.parseExpr(iterCollection)
				
				iterNode = self.doc.createElement("iterator")
				iterNode.appendChild(iterNameExpr)
				
				collNode = self.doc.createElement("collection")
				collNode.appendChild(iterCollectionExpr)
				
				if counterVar:
					counterVarExpr = self.parseExpr(counterVar)
					
					counterNode = self.doc.createElement("counter")
					counterNode.appendChild(counterVarExpr)
					node.appendChild(counterNode)
				
				codeNode = self.doc.createElement("code")
				
				node.appendChild(iterNode)
				node.appendChild(collNode)
				node.appendChild(codeNode)
				
				self.nextNode = codeNode
				
				#raise CompilerException("'for' as 'foreach' not implemented yet")
		else:
			toUsed = True
			if pos == -1:
				pos = posUntil
				toUsed = False
			
			initCode = line[len("for")+1:pos]
			if initCode.find('=') == -1:
				# TODO: Allow nameless iterators
				raise CompilerException("Missing iterator assignment: %s" % (initCode))
			initExpr = self.parseExprNoCache(initCode)
			
			#if not toParam:
			#	keyword = ["until", "to"][toUsed]
			#	raise CompilerException("Missing expression after „%s“" % (keyword))
			
			if toUsed:
				toParam = line[pos+len(" to "):]
				toExpr = self.parseExpr(toParam)
			else:
				toParam = line[pos+len(" until "):]
				toExpr = self.parseExpr(toParam)
			
			if initExpr.childNodes:
				if initExpr.childNodes[0].childNodes:
					iterNode = self.doc.createElement("iterator")
					iterNode.appendChild(initExpr.childNodes[0].childNodes[0])
				
				if initExpr.childNodes[1].childNodes:
					fromNode = self.doc.createElement("from")
					fromNode.appendChild(initExpr.childNodes[1].childNodes[0])
			else:
				raise CompilerException("Incorrect iterator assignment: %s" % (initCode))
			
			if toUsed:
				toNode = self.doc.createElement("to")
			else:
				toNode = self.doc.createElement("until")
			toNode.appendChild(toExpr)
			
			codeNode = self.doc.createElement("code")
			
			node.appendChild(iterNode)
			node.appendChild(fromNode)
			node.appendChild(toNode)
			node.appendChild(codeNode)
			
			self.nextNode = codeNode
		
		return node
		
	def handleShared(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("shared", line)
		
		node = self.doc.createElement("shared")
		code = self.doc.createElement("code")
		node.appendChild(code)
		
		self.nextNode = code
		return node
		
	def handlePrivate(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("private", line)
		
		node = self.doc.createElement("private")
		self.nextNode = node
		return node
		
	def handlePublic(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("public", line)
		
		node = self.doc.createElement("public")
		
		self.nextNode = node
		self.inPublic += 1
		return node
		
	def handlePublicMember(self, line):
		node = self.doc.createElement("public-member")
		node.appendChild(self.parseExpr(addGenerics(line)))
		
		return node
		
	def handleDefine(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("define", line)
		
		node = self.doc.createElement("define")
		self.nextNode = node
		return node
		
	def handleParallel(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("parallel", line)
		
		node = self.doc.createElement("parallel")
		code = self.doc.createElement("code")
		node.appendChild(code)
		
		self.nextNode = code
		return node
		
	def handleBegin(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("begin", line)
		
		node = self.doc.createElement("begin")
		code = self.doc.createElement("code")
		node.appendChild(code)
		
		self.nextNode = code
		return node
		
	def handleRequire(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("require", line)
		
		node = self.doc.createElement("require")
		self.inRequire += 1
		
		self.nextNode = node
		return node
		
	def handleAtomic(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("atomic", line)
		
		node = self.doc.createElement("atomic")
		self.inAtomic += 1
		
		self.nextNode = node
		return node
	
	def handleEnsure(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("ensure", line)
		
		node = self.doc.createElement("ensure")
		self.inEnsure += 1
		
		self.nextNode = node
		return node
	
	#def handleMaybe(self, line):
	#	if not self.nextLineIndented:
	#		self.raiseBlockException("maybe", line)
	#	
	#	node = self.doc.createElement("maybe")
	#	self.inMaybe += 1
	#	
	#	self.nextNode = node
	#	return node
	
	def handleTest(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("test", line)
		
		node = self.doc.createElement("test")
		code = self.doc.createElement("code")
		node.appendChild(code)
		
		self.inTest += 1
		
		self.nextNode = code
		return node
		
	def handleNOOP(self, line):
		return self.doc.createElement("noop")
		
	def handleWhile(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("while", line)
		
		node = self.doc.createElement("while")
		condition = self.doc.createElement("condition")
		code = self.doc.createElement("code")
		condition.appendChild(self.parseExpr(line[len("while")+1:]))
		
		node.appendChild(condition)
		node.appendChild(code)
		
		self.nextNode = code
		return node
	
	def handleTarget(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("target", line)
		
		node = self.doc.createElement("target")
		condition = self.doc.createElement("name")
		code = self.doc.createElement("code")
		condition.appendChild(self.doc.createTextNode(line[len("target")+1:]))
		
		node.appendChild(condition)
		node.appendChild(code)
		
		self.nextNode = code
		return node
	
	def handleCompilerFlags(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("compilerflags", line)
		
		node = self.doc.createElement("compiler-flags")
		self.inCompilerFlags += 1
		
		self.nextNode = node
		return node
	
	def handleCompilerFlag(self, line):
		node = self.doc.createElement("compiler-flag")
		node.appendChild(self.doc.createTextNode(line))
		
		return node
	
	def handleExtern(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("extern", line)
		
		node = self.doc.createElement("extern")
		self.inExtern += 1
		
		self.nextNode = node
		return node
	
	def handleExternLine(self, line):
		node = self.doc.createElement("extern-function")
		name = self.doc.createElement("name")
		node.appendChild(name)
		
		pos = line.find(":")
		
		if pos == -1:
			name.appendChild(self.doc.createTextNode(line))
		else:
			funcName = line[:pos].rstrip()
			funcType = line[pos+1:].lstrip()
			
			type = self.doc.createElement("type")
			node.appendChild(type)
			
			name.appendChild(self.doc.createTextNode(funcName))
			type.appendChild(self.doc.createTextNode(funcType))
		
		return node
		
	def handleExternVariable(self, line):
		node = self.doc.createElement("extern-variable")
		name = self.doc.createElement("name")
		node.appendChild(name)
		
		pos = line.find(":")
		
		if pos == -1:
			varName = line
			varType = "Int"
		else:
			varName = line[:pos].rstrip()
			varType = line[pos+1:].lstrip()
		
		type = self.doc.createElement("type")
		node.appendChild(type)
		
		name.appendChild(self.doc.createTextNode(varName))
		type.appendChild(self.doc.createTextNode(varType))
		
		return node
		
	def handleContinue(self, line):
		return self.doc.createElement("continue")
		
	def handleBreak(self, line):
		return self.doc.createElement("break")
		
	def handleConst(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("const", line)
		
		node = self.doc.createElement("const")
		self.inConst += 1
		
		self.nextNode = node
		return node
		
	def handleReturn(self, line):
		node = self.doc.createElement("return")
		paramCode = line[len("return")+1:]
		if paramCode:
			param = self.parseExpr(addGenerics(paramCode))
			if param.nodeValue or param.hasChildNodes():
				node.appendChild(param)
		return node
	
	def handleAssert(self, line):
		node = self.doc.createElement("assert")
		paramCode = line[len("assert")+1:]
		if paramCode:
			param = self.parseExpr(addGenerics(paramCode))
			if param.nodeValue or param.hasChildNodes():
				node.appendChild(param)
				return node
		
		raise CompilerException("assert keyword expects an expression to be checked (throws an error if it's 'false')")
		
	def handleThrow(self, line):
		node = self.doc.createElement("throw")
		param = self.parseExpr(addGenerics(line[len("throw")+1:]))
		if param.nodeValue or param.hasChildNodes():
			node.appendChild(param)
		else:
			raise CompilerException("throw keyword expects a parameter (e.g. an exception object)")
		return node
	
	def handleYield(self, line):
		node = self.doc.createElement("yield")
		param = self.parseExpr(line[len("yield")+1:])
		if param.nodeValue or param.hasChildNodes():
			node.appendChild(param)
		else:
			raise CompilerException("yield keyword expects a parameter (the next object in the sequence)")
		return node
	
	def handleInclude(self, line):
		node = self.doc.createElement("include")
		param = self.doc.createTextNode(line[len("include")+1:])
		if param.nodeValue:
			node.appendChild(param)
		else:
			raise CompilerException("include keyword expects a file name")
		return node
		
	def handleFunction(self, line):
		# Remove Python def keyword
		if self.currentSyntax == SYNTAX_PYTHON:
			if not line.startswith("def "):
				raise CompilerException("Missing 'def' keyword in function definition")
			line = line[4:] # Remove 'def ' at the start and ')' at the end
		
		# Check for function
		funcName = ""
		pos = 0
		lineLen = len(line)
		while pos < lineLen and isVarChar(line[pos]):
			pos += 1
		
		if pos is len(line):
			funcName = line
		elif line[pos] in {' ', '('}:
			funcName = line[:pos]
			
			if line[pos] == '(':
				line = line[:-1]
		else:
			if self.currentSyntax == SYNTAX_PYTHON:
				line = line[:-1]
				
				whiteSpace = line.find('(')
			else:
				whiteSpace = line.find(' ')
			
			if whiteSpace != -1:
				funcName = line[:whiteSpace]
			else:
				funcName = line
			
			#print(line, pos, funcName)
			
			if (not self.inOperators) and (not self.inCasts):
				raise CompilerException("Invalid function name '" + funcName + "' for function definition")
		
		#print(" belongs to " + self.currentNode.tagName)
		nameNode = self.doc.createElement("name")
		
		if self.inSetter:
			node = self.doc.createElement("setter")
		elif self.inGetter:
			node = self.doc.createElement("getter")
		elif self.inOperators:
			self.inOperator += 1
			node = self.doc.createElement("operator")
		elif self.inIterators:
			node = self.doc.createElement("iterator-type")
		elif self.inCasts:
			node = self.doc.createElement("cast-definition")
			nameNode.tagName = "to"
			nameNode.appendChild(self.parseExpr(addGenerics(funcName)))
		else:
			self.inFunction += 1
			node = self.doc.createElement("function")
		
		if self.inInterface:
			if self.nextLineIndented:
				node.setAttribute("implemented", "true")
			else:
				node.setAttribute("implemented", "false")
		
		if not self.inCasts:
			nameNode.appendChild(self.doc.createTextNode(funcName))
		
		node.appendChild(nameNode)
		
		expr = addGenerics(line[len(funcName)+1:])
		
		if expr:
			if isDefinitelyOperatorSign(expr[0]):
				raise CompilerException("Parameter name missing: „%s“ (expecting function definition for „%s“)" % (expr, funcName))
			params = self.parseExpr(expr)
			paramsNode = self.parser.getParametersNode(params)
			node.appendChild(paramsNode)
		
		codeNode = self.doc.createElement("code")
		node.appendChild(codeNode)
		#self.inFunction = True
		
		if not self.inInterface:
			self.nextNode = codeNode
		
		return node
		
	def handleInterface(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("interface", line)
		
		self.inInterface += 1
		
		#pos = line.find(" interface")
		interfaceName = line[len("interface "):]
		
		node = self.doc.createElement("interface")
		
		nameNode = self.doc.createElement("name")
		nameNode.appendChild(self.doc.createTextNode(interfaceName))
		
		code = self.doc.createElement("code")
		
		node.appendChild(nameNode)
		node.appendChild(code)
		
		self.nextNode = code
		return node
		
	def handleClass(self, line):
		self.inClass += 1
		
		# Remove Python class keyword
		if self.currentSyntax == SYNTAX_PYTHON:
			if not line.startswith("class "):
				raise CompilerException("Missing 'class' keyword in class definition")
			line = line[6:]
		
		if " extends" in line:
			raise CompilerException("'extends' must be written as a block inside the class")
		
		className = line
		
		node = self.doc.createElement("class")
		nameNode = self.doc.createElement("name")
		
		dirName = extractDir(self.file).split("/")[-2]
		if className == dirName:
			nameNode.appendChild(self.doc.createTextNode(self.classPrefix + className))
		else:
			nameNode.appendChild(self.doc.createTextNode(className))
		#publicNode = self.doc.createElement("public")
		#privateNode = self.doc.createElement("private")
		code = self.doc.createElement("code")
		
		node.appendChild(nameNode)
		#node.appendChild(publicNode)
		#node.appendChild(privateNode)
		node.appendChild(code)
		
		self.nextNode = code
		return node
		
	def handleTry(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("try", line)
		
		node = self.doc.createElement("try-block")
		
		tryNode = self.doc.createElement("try")
		code = self.doc.createElement("code")
		
		tryNode.appendChild(code)
		
		node.appendChild(tryNode)
		self.nextNode = code
		self.inTryBlock += 1
		return node
	
	def handleCatch(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("catch", line)
		
		#if self.inTryBlock <= 0:
		#	raise CompilerException("catch needs to be used directly after a try block")
		
		node = self.doc.createElement("catch")
		exceptionType = self.doc.createElement("variable")
		code = self.doc.createElement("code")
		
		varExpr = line[len("catch")+1:]
		if varExpr:
			varNode = self.parseExpr(varExpr)
			if nodeIsValid(varNode):
				exceptionType.appendChild(varNode)
		
		node.appendChild(exceptionType)
		node.appendChild(code)
		self.nextNode = code
		return node
		
	def raiseBlockException(self, keyword, line):
		raise CompilerException("It is required to have an indented %s block after „%s“" % (keyword, line))
		
	def handleIf(self, line):
		node = self.doc.createElement("if-block")
		
		ifNode = self.doc.createElement("if")
		condition = self.doc.createElement("condition")
		code = self.doc.createElement("code")
		
		conditionText = line[len("if")+1:]
		
		# Error check
		if conditionText == "":
			raise CompilerException("You need to specify an if condition")
		
		# Don't be so serious!
		if conditionText.endswith(":"):
			raise CompilerException("This ain't Python, my friend (colon is not needed)")
		
		if not self.nextLineIndented:
			self.raiseBlockException("if", line)
		
		condition.appendChild(self.parseExpr(conditionText))
		
		ifNode.appendChild(condition)
		ifNode.appendChild(code)
		
		node.appendChild(ifNode)
		
		self.nextNode = code
		self.inIfBlock += 1
		return node
	
	def handleElif(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("elif", line)
		
		#if self.inIfBlock <= 0:
		#	raise CompilerException("elif can't be used without an if block")
		
		node = self.doc.createElement("else-if")
		condition = self.doc.createElement("condition")
		code = self.doc.createElement("code")
		
		condition.appendChild(self.parseExpr(line[len("elif")+1:]))
		
		node.appendChild(condition)
		node.appendChild(code)
		
		self.nextNode = code
		return node
		
	def handleElse(self, line):
		if not self.nextLineIndented:
			self.raiseBlockException("else", line)
		
		#if self.inIfBlock <= 0:
		#	raise CompilerException("else can't be used without if or elif")
		
		node = self.doc.createElement("else")
		code = self.doc.createElement("code")
		
		node.appendChild(code)
		self.nextNode = code
		return node
		
	def handleImport(self, line):
		if self.nextLineIndented:
			if self.lastLineCount > 0:
				raise CompilerException("import can not be used as a block (yet)")
			else:
				raise CompilerException("Indentation at the beginning of the file is not allowed")
		
		importedModule = line[len("import"):].strip()
		modulePath = getModulePath(importedModule, self.dir, self.compiler.projectDir, self.compiler.importExtension)
		
		if modulePath:
			self.importedFiles.append(modulePath)
		elif importedModule == "":
			raise CompilerException("You need to specify which module you want to import")
		else:
			#print(importedModule, " = ", modulePath, "(1)", self.dir, "(2)", self.compiler.projectDir)
			raise CompilerException("Module not found: " + importedModule)
		
		element = self.doc.createElement("import")
		element.appendChild(self.doc.createTextNode(importedModule))
		self.dependencies.appendChild(element)
		
		# Manually register this
		self.registerNode(element)
		
		return None
	
	def handleInlineComment(self, comment):
		pass
	
	def handleComment(self, comment, inline):
		node = self.doc.createElement("comment")
		node.appendChild(self.doc.createTextNode(encodeCDATA(comment)))
		if inline:
			node.setAttribute("inline", "true")
		
		# Manually register this
		#self.registerNode(node)
		#self.currentNode.appendChild(node)
		
		return node
	
	def addString(self, stri, stringLimiter):
		# TODO: Add string to string list
		identifier = "flua_string_" + str(self.stringCount) #.zfill(9)
		
		# Create XML node
		stringNode = self.doc.createElement("string")
		stringNode.setAttribute("id", identifier)
		if stringLimiter == "'":
			stringNode.setAttribute("as-byte", "true")
		stringNode.appendChild(self.doc.createTextNode(encodeCDATA(stri)))
		self.strings.appendChild(stringNode)
		
		self.stringCount += 1
		
		return identifier
	
	def prepareLine(self, line):
		i = 0
		roundBracketsBalance = 0 # ()
		curlyBracketsBalance = 0 # {}
		squareBracketsBalance = 0 # []
		#chevronsBalance = 0 # <>
		
		seqPrefix = "_flua_seq"
		seqPrefixLen = len(seqPrefix)
		
		self.currentLineComment = None
		self.keyword = ""
		
		# DO NOT CACHE len(line)!
		while i < len(line):
			# Remove comments
			if line[i] == '#':
				lineContent = line[:i].rstrip()
				comment = line[i+1:]
				self.currentLineComment = comment
				return lineContent
			# Number of brackets check
			elif line[i] == '(':
				roundBracketsBalance += 1
			elif line[i] == ')':
				roundBracketsBalance -= 1
			elif line[i] == '[':
				squareBracketsBalance += 1
				
				#print("in")
				#print(self.inOperators)
				#print(self.inOperator)
				
				if (self.inOperators == False or self.inOperator == True) and (not self.inInterface) and not line.strip().startswith("[] "):
					if i > 1 and i + 1 < len(line) and line[i+1] == ']':
						raise CompilerException("You can't create a vector with 0 elements using this syntax. You can use 'Vector<YOUR_TYPE>()' if you really need an empty vector.")
					
					# New sequences
					if (i == 0 or (not isVarChar(line[i-1]) and line[i-1] != "]")):
						line = "%s%s%s" % (line[:i], seqPrefix, line[i:])
						i += seqPrefixLen
			elif line[i] == ']':
				squareBracketsBalance -= 1
			elif line[i] == '{':
				# Ignore on C++
				if self.currentSyntax == SYNTAX_CPP:
					line = line[:i].rstrip()
					break
				
				curlyBracketsBalance += 1
			elif line[i] == '}':
				# Ignore on C++
				if self.currentSyntax == SYNTAX_CPP:
					line = line[:i].rstrip()
					break
				
				curlyBracketsBalance -= 1
			elif line[i] == ';':
				# Ignore on C++
				if self.currentSyntax == SYNTAX_CPP:
					line = line[:i]
					break
			elif line[i] == ':' and i == len(line) - 1:
				# Ignore on Python
				if self.currentSyntax == SYNTAX_PYTHON:
					line = line[:i]
					break
			elif line[i] == ' ':
				if not self.keyword:
					self.keyword = line[:i]
				
				# Remove "new"
				if self.currentSyntax == SYNTAX_CPP:
					if i >= 3:
						if line[i-3:i] == "new" and (i == 3 or not isVarChar(line[i - 4])):
							#print("before: " + line)
							line = line[:i-3] + line[i+1:]
							#print("after:  " + line)
							i -= 3
					
			#elif line[i] == '<':
			#	chevronsBalance += 1
			#elif line[i] == '>':
			#	chevronsBalance -= 1
			
			# Remove strings
			elif line[i] == '"' or line[i] == "'":
				stringLimiter = line[i]
				
				lineLen = len(line)
				
				if i + 1 < lineLen:
					firstCharacter = line[i + 1]
				else:
					firstCharacter = ""
				
				paramAtEndOfString = False
				
				h = i + 1
				while h < lineLen and line[h] != stringLimiter:
					# Variables in strings
					if line[h] == '$' and line[h - 1] != '\\':
						paramEnd = h + 1
						
						if paramEnd >= lineLen:
							raise CompilerException("Expecting variable name after „%s“" % line)
						
						# Get variable name
						while paramEnd < lineLen and (line[paramEnd].isalnum() or line[paramEnd] == '_'):
							paramEnd += 1
						
						paramName = line[h+1:paramEnd]
						identifier = self.addString(line[i+1:h], stringLimiter)
						
						# TODO: Possible string concatenation optimization
						rest = line[paramEnd:]
						if rest and rest[0] == stringLimiter:
							# Ignore empty string at the end
							line = '%s%s+%s%s' % (line[:i], identifier, paramName, rest[1:])
							paramAtEndOfString = True
							break
						else:
							line = '%s%s+%s+"%s' % (line[:i], identifier, paramName, rest)
						lineLen = len(line)
						h = lineLen - len(rest)
						i = h - 1
						continue
					h += 1
				
				# Byte representation must be 1 character long
				if stringLimiter == "'" and (h  - i != 2 or firstCharacter == "\\") and not (firstCharacter == "\\" and h - i == 3):
					raise CompilerException("A character / byte representation needs to contain exactly 1 character")
					
				if paramAtEndOfString:
					continue
				
				if h == lineLen:
					raise CompilerException("You forgot to close the string: \" missing")
				
				if h + 1 < lineLen and mustNotBeNextToExpr(line[h + 1]):
					raise CompilerException("Operator missing: %s ↓ %s" % (line[i:h+1].strip(), line[h+1:].strip()))
				if i > 1 and mustNotBeNextToExpr(line[i - 1]):
					raise CompilerException("Operator missing: %s ↓ %s" % (line[:i].strip(), line[i:h+1].strip()))
				
				identifier = self.addString(line[i+1:h], stringLimiter)
				line = line[:i] + identifier + line[h+1:]
				i += len(identifier) - 1
			i += 1
		
		if not self.keyword:
			self.keyword = line
		
		if self.currentSyntax == SYNTAX_RUBY:
			if line == "end":#line.endswith("end") and line[:-3].isspace():
				self.keyword = ""
				return ""
			elif self.keyword == "elsif":
				self.keyword = "elif"
				return "elif" + line[4:]
		
		# ()
		if roundBracketsBalance > 0:
			raise CompilerException("You forgot to close the round bracket: ')' missing%s" % ([" %d times" % (abs(roundBracketsBalance)), ""][abs(roundBracketsBalance) == 1]))
		elif roundBracketsBalance < 0:
			raise CompilerException("You forgot to open the round bracket: '(' missing%s" % ([" %d times" % (abs(roundBracketsBalance)), ""][abs(roundBracketsBalance) == 1]))
		
		# []
		if squareBracketsBalance > 0:
			raise CompilerException("You forgot to close the square bracket: ']' missing%s" % ([" %d times" % (abs(squareBracketsBalance)), ""][abs(squareBracketsBalance) == 1]))
		elif squareBracketsBalance < 0:
			raise CompilerException("You forgot to open the square bracket: '[' missing%s" % ([" %d times" % (abs(squareBracketsBalance)), ""][abs(squareBracketsBalance) == 1]))
		
		# <>
		#if chevronsBalance > 0:
		#	raise CompilerException("You forgot to close the chevron: '>' missing%s" % ([" %d times" % (chevronsBalance), ""][abs(chevronsBalance) == 1]))
		#elif chevronsBalance < 0:
		#	raise CompilerException("You forgot to open the chevron: '<' missing%s" % ([" %d times" % (chevronsBalance), ""][abs(chevronsBalance) == 1]))
		
		return line
	
