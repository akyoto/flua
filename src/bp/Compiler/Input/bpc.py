####################################################################
# Header
####################################################################
# Syntax:   Blitzprog Code
# Author:   Eduard Urbach

####################################################################
# License
####################################################################
# (C) 2008  Eduard Urbach
# 
# This file is part of Blitzprog.
# 
# Blitzprog is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Blitzprog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Blitzprog.  If not, see <http://www.gnu.org/licenses/>.

####################################################################
# Imports
####################################################################
from ExpressionParser import *
from Utils import *
import codecs

####################################################################
# Classes
####################################################################
class CompilerException(Exception):
	
	def __init__(self, reason):
		self.reason = reason
		
	def __str__(self):
		return repr(self.reason)

class BPCCompiler:
	
	def __init__(self):
		self.compiledFiles = dict()
		self.initExprParser()
	
	def initExprParser(self):
		self.parser = ExpressionParser()
		
		# See http://www.cppreference.com/wiki/operator_precedence
		
		# 1: Function calls
		operators = OperatorLevel()
		operators.addOperator(Operator("(", "call.unused", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
		# 2: Access
		operators = OperatorLevel()
		operators.addOperator(Operator(".", "access", Operator.BINARY))
		operators.addOperator(Operator("[", "index.unused", Operator.BINARY))
		operators.addOperator(Operator("#", "call", Operator.BINARY))
		operators.addOperator(Operator("@", "index", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
		# Loose pointer
		operators = OperatorLevel()
		operators.addOperator(Operator("~", "loose-reference", Operator.UNARY))
		self.parser.addOperatorLevel(operators)
		
		# 3: Unary
		operators = OperatorLevel()
		operators.addOperator(Operator("!", "not", Operator.UNARY))
		operators.addOperator(Operator("-", "negative", Operator.UNARY))
		self.parser.addOperatorLevel(operators)
		
		# 5: Mul, Div
		operators = OperatorLevel()
		operators.addOperator(Operator("*", "multiply", Operator.BINARY))
		operators.addOperator(Operator("/", "divide", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
		# 6: Add, Sub
		operators = OperatorLevel()
		operators.addOperator(Operator("+", "add", Operator.BINARY))
		operators.addOperator(Operator("-", "subtract", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
		# 8: GT, LT
		operators = OperatorLevel()
		operators.addOperator(Operator(">=", "greater-or-equal", Operator.BINARY))
		operators.addOperator(Operator(">", "greater", Operator.BINARY))
		operators.addOperator(Operator("<=", "less-or-equal", Operator.BINARY))
		operators.addOperator(Operator("<", "less", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
		# 9: Comparison
		operators = OperatorLevel()
		operators.addOperator(Operator("==", "equal", Operator.BINARY))
		operators.addOperator(Operator("!=", "not-equal", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
		# 13: Logical AND
		operators = OperatorLevel()
		operators.addOperator(Operator("&&", "and", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
		# 14: Logical OR
		operators = OperatorLevel()
		operators.addOperator(Operator("||", "or", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
		# 15: Ternary operator
		operators = OperatorLevel()
		operators.addOperator(Operator(":", "ternary-code", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
		operators = OperatorLevel()
		operators.addOperator(Operator("?", "ternary-condition", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
		# 16: Assign
		operators = OperatorLevel()
		operators.addOperator(Operator("+=", "assign-add", Operator.BINARY))
		operators.addOperator(Operator("-=", "assign-subtract", Operator.BINARY))
		operators.addOperator(Operator("*=", "assign-multiply", Operator.BINARY))
		operators.addOperator(Operator("/=", "assign-divide", Operator.BINARY))
		#operators.addOperator(Operator("}=", "assign-each-in", Operator.BINARY))
		operators.addOperator(Operator("=", "assign", Operator.BINARY))
		operators.addOperator(Operator("->", "flows-to", Operator.BINARY))
		operators.addOperator(Operator("<-", "flows-from", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
		# Comma
		operators = OperatorLevel()
		operators.addOperator(Operator(",", "separate", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
	
	def compile(self, mainFile):
		fileIn = os.path.abspath(mainFile)
		
		if not self.compiledFiles:
			self.projectDir = os.path.dirname(fileIn) + "/"
		
		bpcFile = self.spawnFileCompiler(fileIn)
		self.compiledFiles[fileIn] = bpcFile
		
		for file in bpcFile.importedFiles:
			if not file in self.compiledFiles:
				# TODO: Change directory
				self.compile(file)
		
	def spawnFileCompiler(self, fileIn):
		myFile = BPCFile(self, fileIn)
		myFile.compile()
		return myFile
	
	def validate(self):
		pass
	
	def writeToFS(self, dirOut):
		dirOut = os.path.abspath(dirOut) + "/"
		
		for bpcFile in self.compiledFiles.values():
			fileOut = dirOut + stripExt(bpcFile.file[len(self.projectDir):]) + ".xml"
			
			# Directory structure
			concreteDirOut = os.path.dirname(fileOut)
			if not os.path.isdir(concreteDirOut):
				os.makedirs(concreteDirOut)
			
			with open(fileOut, "w") as outStream:
				output = bpcFile.root.toprettyxml()
				outStream.write(output)

class BPCFile:
	
	def __init__(self, compiler, fileIn):
		self.compiler = compiler
		self.file = fileIn
		self.dir = os.path.dirname(fileIn) + "/"
		self.stringCount = 0
		self.importedFiles = []
		self.nextLineIndented = False
		self.savedNextNode = 0
		self.inSwitch = 0
		self.parser = self.compiler.parser
		
		# XML tags which can follow another tag
		
		# 2 levels
		self.blocks = {
			"if-block" : ["else-if", "else"],
			"try-block" : ["catch"]
		}
		
		# 1 level
		self.simpleBlocks = {
			"class" : [],
			"function" : [],
			"while" : [],
			"for" : [],
			"in" : [],
			"switch" : [],
			"case" : ["case"]
		}
		
		# This is used for xml tags which have a "code" node
		self.nextNode = 0
		
	def compile(self):
		print("Compiling: " + self.file)
		
		self.doc = parseString("<module><header><title/><dependencies/></header><code></code></module>")
		self.root = self.doc.documentElement
		self.currentNode = self.root.getElementsByTagName("code")[0]
		
		# Read
		with codecs.open(self.file, "r", "utf-8") as inStream:
			codeText = inStream.read()
		
		lines = codeText.split('\n') + [""]
		tabCount = 0
		prevTabCount = 0
		
		# Go through every line -> build the structure
		for lineIndex in range(0, len(lines)):
			line = lines[lineIndex].rstrip()
			tabCount = self.countTabs(line)
			line = line.lstrip()
			line = self.removeStrings(line)
			line = self.removeComments(line)
			
			if line == "":
				continue
			
			self.nextLineIndented = False
			if lineIndex < len(lines) - 1:
				tabCountNextLine = self.countTabs(lines[lineIndex + 1])
				if tabCountNextLine == tabCount + 1:
					self.nextLineIndented = True
			
			#print(">" * tabCount + line)
			currentLine = self.processLine(line)
			
			# Tab level hierarchy
			if tabCount > prevTabCount:
				if self.savedNextNode:
					self.currentNode = self.savedNextNode
					self.savedNextNode = 0
				else:
					self.currentNode = self.lastNode
			elif tabCount < prevTabCount:
				atTab = prevTabCount
				while atTab > tabCount:
					self.currentNode = self.currentNode.parentNode
					
					# XML elements with "code" tags need special treatment
					if self.currentNode.parentNode.tagName in self.blocks:
						tagsAllowed = self.blocks[self.currentNode.parentNode.tagName]
						if atTab != tabCount + 1 or isTextNode(currentLine) or (not currentLine.tagName in tagsAllowed):
							self.currentNode = self.currentNode.parentNode.parentNode
						else:
							self.currentNode = self.currentNode.parentNode
					elif self.currentNode.tagName in self.simpleBlocks:
						tagsAllowed = self.simpleBlocks[self.currentNode.tagName]
						if atTab != tabCount + 1 or isTextNode(currentLine) or not currentLine.tagName in tagsAllowed:
							self.currentNode = self.currentNode.parentNode
					atTab -= 1
			
			self.savedNextNode = self.nextNode
			
			self.lastNode = self.currentNode.appendChild(currentLine)
			prevTabCount = tabCount
		
		print(self.doc.toprettyxml())
		
	def parseExpr(self, expr):
		return self.parser.buildXMLTree(expr)
		
	def processLine(self, line):
		if startsWith(line, "import"):
			return self.handleImport(line)
		elif startsWith(line, "while"):
			return self.handleWhile(line)
		elif startsWith(line, "try"):
			return self.handleTry(line)
		elif startsWith(line, "catch"):
			return self.handleCatch(line)
		elif startsWith(line, "if"):
			return self.handleIf(line)
		elif startsWith(line, "elif"):
			return self.handleElif(line)
		elif startsWith(line, "else"):
			return self.handleElse(line)
		elif startsWith(line, "throw"):
			return self.handleThrow(line)
		elif startsWith(line, "return"):
			return self.handleReturn(line)
		elif startsWith(line, "const"):
			return self.handleConst(line)
		elif startsWith(line, "break"):
			return self.handleBreak(line)
		elif startsWith(line, "continue"):
			return self.handleContinue(line)
		elif startsWith(line, "private"):
			return self.handlePrivate(line)
		elif startsWith(line, "in"):
			return self.handleIn(line)
		elif startsWith(line, "switch"):
			return self.handleSwitch(line)
		elif line == "...":
			return self.handleNOOP(line)
		elif self.nextLineIndented:
			if self.inSwitch > 0:
				return self.handleCase(line)
			elif line[0].islower():
				return self.handleFunction(line)
			else:
				return self.handleClass(line)
		else:
			line = self.addBrackets(line)
			node = self.parseExpr(line)
			return node
		
	def addBrackets(self, line):
		# If the character that follows the first whitespace is a VarChar we assume it's a function call
		nextWhitespace = getNextWhitespacePos(line, 0)
		if nextWhitespace == -1:
			# No whitespaces, so we need to check if it's a procedure call
			for char in line:
				if (not isVarChar(char)) and (char != '.'):
					return line
			
			# Seems this is a procedure call
			return line + "()"
		
		# We found a whitespace, so check the next character
		char = line[nextWhitespace+1]
		if isVarChar(char):
			return line[:nextWhitespace] + "(" + line[nextWhitespace+1:] + ")"
		
		return line
		
	def handleCase(self, line):
		node = self.doc.createElement("case")
		values = self.compiler.parser.getParametersNode(self.parseExpr(line))
		code = self.doc.createElement("code")
		
		values.tagName = "values"
		for value in values.childNodes:
			value.tagName = "value"
	
		node.appendChild(values)
		node.appendChild(code)
		
		self.nextNode = code
		return node
		
	def handleSwitch(self, line):
		node = self.doc.createElement("switch")
		value = self.doc.createElement("value")
		value.appendChild(self.parseExpr(line[len("switch")+1:]))
		
		node.appendChild(value)
		
		self.inSwitch += 1
		self.nextNode = node
		return node
		
	def handleIn(self, line):
		node = self.doc.createElement("in")
		expr = self.doc.createElement("expression")
		code = self.doc.createElement("code")
		expr.appendChild(self.parseExpr(line[len("in")+1:]))
		
		node.appendChild(expr)
		node.appendChild(code)
		
		self.nextNode = code
		return node
		
	def handlePrivate(self, line):
		node = self.doc.createElement("private")
		self.nextNode = node
		return node
		
	def handleNOOP(self, line):
		return self.doc.createElement("noop")
		
	def handleWhile(self, line):
		node = self.doc.createElement("while")
		condition = self.doc.createElement("condition")
		code = self.doc.createElement("code")
		condition.appendChild(self.parseExpr(line[len("while")+1:]))
		
		node.appendChild(condition)
		node.appendChild(code)
		
		self.nextNode = code
		return node
		
	def handleContinue(self, line):
		return self.doc.createElement("continue")
		
	def handleBreak(self, line):
		return self.doc.createElement("break")
		
	def handleConst(self, line):
		node = self.doc.createElement("const")
		param = self.parseExpr(line[len("const")+1:])
		if param.hasChildNodes() and param.tagName == "assign":
			node.appendChild(param)
		else:
			raise CompilerException("#const keyword expects a variable assignment")
		return node
		
	def handleReturn(self, line):
		node = self.doc.createElement("return")
		param = self.parseExpr(line[len("return")+1:])
		if param.nodeValue or param.hasChildNodes():
			node.appendChild(param)
		return node
	
	def handleThrow(self, line):
		node = self.doc.createElement("throw")
		param = self.parseExpr(line[len("throw")+1:])
		if param.nodeValue or param.hasChildNodes():
			node.appendChild(param)
		else:
			raise CompilerException("#throw keyword expects a parameter (e.g. an exception object)")
		return node
		
	def handleFunction(self, line):
		# Check for function
		funcName = ""
		pos = 0
		lineLen = len(line)
		while pos < lineLen and isVarChar(line[pos]):
			pos += 1
		if pos is len(line):
			funcName = line
		elif line[pos] == ' ':
			funcName = line[:pos]
		else:
			whiteSpace = line.find(' ')
			if whiteSpace is not -1:
				funcName = line[:whiteSpace]
			else:
				funcName = line
			raise CompilerException("Invalid function name '" + funcName + "'")
		
		#print(" belongs to " + self.currentNode.tagName)
		
		node = self.doc.createElement("function")
		
		params = self.parseExpr(line[len(funcName)+1:])
		
		nameNode = self.doc.createElement("name")
		nameNode.appendChild(self.doc.createTextNode(funcName))
		paramsNode = self.parser.getParametersNode(params)
		codeNode = self.doc.createElement("code")
		
		node.appendChild(nameNode)
		node.appendChild(paramsNode)
		node.appendChild(codeNode)
		
		#self.inFunction = True
		self.nextNode = codeNode
		return node
		
	def handleClass(self, line):
		className = line
		
		node = self.doc.createElement("class")
		
		nameNode = self.doc.createElement("name")
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
		node = self.doc.createElement("try-block")
		
		tryNode = self.doc.createElement("try")
		code = self.doc.createElement("code")
		
		tryNode.appendChild(code)
		
		node.appendChild(tryNode)
		self.nextNode = code
		return node
	
	def handleCatch(self, line):
		node = self.doc.createElement("catch")
		exceptionType = self.doc.createElement("variable")
		code = self.doc.createElement("code")
		
		varNode = self.parseExpr(line[len("catch")+1:])
		if nodeIsValid(varNode):
			exceptionType.appendChild(varNode)
		
		node.appendChild(exceptionType)
		node.appendChild(code)
		self.nextNode = code
		return node
		
	def handleIf(self, line):
		node = self.doc.createElement("if-block")
		
		ifNode = self.doc.createElement("if")
		condition = self.doc.createElement("condition")
		code = self.doc.createElement("code")
		
		condition.appendChild(self.parseExpr(line[len("if")+1:]))
		
		ifNode.appendChild(condition)
		ifNode.appendChild(code)
		
		node.appendChild(ifNode)
		
		print("Setting nextNode!")
		self.nextNode = code
		return node
	
	def handleElif(self, line):
		node = self.doc.createElement("else-if")
		condition = self.doc.createElement("condition")
		code = self.doc.createElement("code")
		
		condition.appendChild(self.parseExpr(line[len("elif")+1:]))
		
		node.appendChild(condition)
		node.appendChild(code)
		
		self.nextNode = code
		return node
		
	def handleElse(self, line):
		node = self.doc.createElement("else")
		code = self.doc.createElement("code")
		
		node.appendChild(code)
		self.nextNode = code
		return node
		
	def handleImport(self, line):
		# Priority for module search:
		# ########################### #
		# 1. Local    # 4. Project    # 7. Global     #
		# ########################### ############### #
		# 2. File     # 5.  File      # 8.  File      #
		# 3. Dir      # 6.  Dir       # 9.  Dir       #
		
		importedModule = line[len("import"):].strip()
		importedModulePath = importedModule.replace(".", "/")
		
		# Local
		importedFile = self.dir + importedModulePath + ".bpc"
		
		importedInFolder = self.dir + importedModulePath
		importedInFolder += "/" + stripAll(importedInFolder) + ".bpc"
		
		# Project
		pImportedFile = self.compiler.projectDir + importedModulePath + ".bpc"
		
		pImportedInFolder = self.compiler.projectDir + importedModulePath
		pImportedInFolder += "/" + stripAll(pImportedInFolder) + ".bpc"
		
		# TODO: Implement global variant
		
		if os.path.isfile(importedFile):
			self.importedFiles.append(importedFile)
		elif os.path.isfile(importedInFolder):
			self.importedFiles.append(importedInFolder)
		elif os.path.isfile(pImportedFile):
			self.importedFiles.append(pImportedFile)
		elif os.path.isfile(pImportedInFolder):
			self.importedFiles.append(pImportedInFolder)
		else:
			raise CompilerException("Module not found: " + importedModule)
		
		element = self.doc.createElement("import")
		element.appendChild(self.doc.createTextNode(importedModule))
		return element
	
	def countTabs(self, line):
		tabCount = 0
		while tabCount < len(line) and line[tabCount] == '\t':
			tabCount += 1
		
		return tabCount
	
	def removeStrings(self, line):
		i = 0
		while i < len(line):
			if line[i] == '"':
				h = i + 1
				while h < len(line) and line[h] != '"':
					h += 1
				# TODO: Add string to string list
				#print("STRING: " + line[i:h+1])
				identifier = "_bp_string_" + str(self.stringCount)
				line = line[:i] + identifier + line[h+1:]
				self.stringCount += 1
				i += len(identifier)
			i += 1
		return line
	
	def removeComments(self, line):
		pos = line.find('#')
		if pos is not -1:
			return line[:pos].rstrip()
		else:
			return line
	
####################################################################
# Functions
####################################################################
def compileWarning(msg):
	print("[Warning] " + msg)

####################################################################
# Main
####################################################################
if __name__ == '__main__':
	try:
		print("Starting:")
		start = time.clock()
		
		bpc = BPCCompiler()
		bpc.compile("../Test/Input/main.bpc")
		bpc.validate()
		#bpc.writeToFS("../Test/Output/")
		
		elapsedTime = time.clock() - start
		print("Time:    " + str(elapsedTime * 1000) + " ms")
		print("Done.")
	except:
		printTraceback()