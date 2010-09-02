####################################################################
# Header
####################################################################
# Language: Blitzprog Code
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
from Languages.ProgrammingLanguage import *
from ExpressionParser import *
from xml.dom.minidom import *

####################################################################
# Classes
####################################################################
class LanguageBPC(ProgrammingLanguage):
	
	def __init__(self):
		self.extensions = ["bpc"]
		self.doc = None
		self.stringCount = 0
		self.nextLineIndented = False
		self.currentNode = None
		
		self.inFunction = False
		self.inClass = False
		
		self.keywordsBlock = ["if", "elif", "else", "switch", "in", "do", "for", "while", "try", "catch"]
		self.keywordsNoBlock = ["import", "return", "const", "break", "continue", "throw"]
        
	def initExprParser(self):
		self.parser = ExpressionParser()
		
		# See http://www.cppreference.com/wiki/operator_precedence
		
		# 1: Function calls
		operators = OperatorLevel()
		operators.addOperator(Operator("(", "direct-call", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
		# 2: Access
		operators = OperatorLevel()
		operators.addOperator(Operator(".", "access", Operator.BINARY))
		operators.addOperator(Operator("#", "call", Operator.BINARY))
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
		operators.addOperator(Operator(">", "greater-than", Operator.BINARY))
		operators.addOperator(Operator("<", "less-than", Operator.BINARY))
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
		operators.addOperator(Operator("=", "assign", Operator.BINARY))
		operators.addOperator(Operator("+=", "assign-add", Operator.BINARY))
		operators.addOperator(Operator("-=", "assign-subtract", Operator.BINARY))
		operators.addOperator(Operator("*=", "assign-multiply", Operator.BINARY))
		operators.addOperator(Operator("/=", "assign-divide", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
		# Comma
		operators = OperatorLevel()
		operators.addOperator(Operator(",", "separate", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
	def countTabs(self, line):
		tabCount = 0
		while tabCount < len(line) and line[tabCount] == '\t':
			tabCount += 1
		
		return tabCount
		
	def compileCodeToXML(self, code):
		lines = code.split('\n') + ["__bp__EOM"]
		self.doc = parseString("<module><header><title/><dependencies/></header><code></code></module>")
		self.initExprParser()
		
		root = self.doc.documentElement
		lastTabCount = 0
		self.currentNode = root.getElementsByTagName("code")[0]
		lastNode = self.currentNode
		
		try:
			for lineIndex in range(0, len(lines)):
				line = lines[lineIndex].rstrip()
				if line:
					tabCount = self.countTabs(line)
					
					self.nextLineIndented = False
					if lineIndex < len(lines) - 1:
						tabCountNextLine = self.countTabs(lines[lineIndex + 1])
						if tabCountNextLine == tabCount + 1:
							self.nextLineIndented = True
							print("INDENT")
					
					line = line.strip()
					
					line = self.removeStrings(line)
					line = self.removeComments(line)
					
					# Function leaving
					if tabCount < lastTabCount:
						if self.currentNode.tagName == "code":
							if self.currentNode.parentNode.tagName == "function":
								print("LEFT FUNCTION")
								self.inFunction = False
							elif self.currentNode.parentNode.tagName == "class":
								print("LEFT CLASS")
								self.inClass = False
					
					node = self.parseLine(line)
					
					#===============================================================
					# print("--------------------------")
					# print("Line: [" + line + "]")
					# print("Node: [" + node.tagName + "]")
					# print(node.getElementsByTagName("code"))
					# print("Current Node: [" + self.currentNode.parentNode.tagName + "." + self.currentNode.tagName + "]")
					#===============================================================
					
					# Block
					if tabCount > lastTabCount:
						self.currentNode = lastNode
						
						codeTags = self.currentNode.getElementsByTagName("code")
						if codeTags:
							self.currentNode = codeTags[0]
						
						self.currentNode.appendChild(node)
					elif tabCount < lastTabCount:
						atTab = lastTabCount
						while atTab > tabCount:
							if self.currentNode.tagName == "code":
								self.currentNode = self.currentNode.parentNode.parentNode
								if self.currentNode.tagName == "if-block" and node.tagName != "else-if" and node.tagName != "else":
									self.currentNode = self.currentNode.parentNode
							else:
								self.currentNode = self.currentNode.parentNode
							atTab -= 1
						
						self.currentNode.appendChild(node)
					else:
						self.currentNode.appendChild(node)
					
					# Check
					if node.nodeType == Node.TEXT_NODE:
						if node.nodeValue == "__bp__EOM":
							self.currentNode.removeChild(node)
					elif (node.tagName == "else-if" or node.tagName == "else") and self.currentNode.tagName != "if-block":
						raise CompilerException("#elif and #else can only appear in an #if block")
					
					lastTabCount = tabCount
					lastNode = node
		except CompilerException as e:
			e.setLine(lineIndex + 1)
			raise e
		except:
			printTraceback()
			
		return self.doc
	
	def functionExists(self, name):
		if name == "print":
			return True
		return False
	
	def removeStrings(self, line):
		i = 0
		while i < len(line):
			if line[i] == '"':
				h = i + 1
				while h < len(line) and line[h] != '"':
					h += 1
				# TODO: Add string to string list
				#print("STRING: " + line[i:h+1])
				identifier = "string_" + str(self.stringCount)
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
	
	def parseLine(self, line):
		node = None
		
		# Blocks
		if self.nextLineIndented:
			if startswith(line, "if"):
				node = self.doc.createElement("if-block")
				
				ifNode = self.doc.createElement("if")
				condition = self.doc.createElement("condition")
				code = self.doc.createElement("code")
				
				condition.appendChild(self.parseExpr(line[len("if")+1:]))
				
				ifNode.appendChild(condition)
				ifNode.appendChild(code)
				
				node.appendChild(ifNode)
			elif startswith(line, "elif"):
				node = self.doc.createElement("else-if")
				condition = self.doc.createElement("condition")
				code = self.doc.createElement("code")
				
				condition.appendChild(self.parseExpr(line[len("elif")+1:]))
				
				node.appendChild(condition)
				node.appendChild(code)
			elif startswith(line, "else"):
				node = self.doc.createElement("else")
				code = self.doc.createElement("code")
				
				node.appendChild(code)
			elif startswith(line, "while"):
				node = self.doc.createElement("while")
				condition = self.doc.createElement("condition")
				code = self.doc.createElement("code")
				print("WHILE:")
				condition.appendChild(self.parseExpr(line[len("while")+1:]))
				
				node.appendChild(condition)
				node.appendChild(code)
			else:
				# TODO: Check for other block types: Classes, functions, ...
				
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
				
				if self.inFunction and funcName == "init":
					self.currentNode.parentNode.tagName = "class"
					self.inClass = True
					print("ENTERED CLASS")
				
				node = self.doc.createElement("function")
				
				nameNode = self.doc.createElement("name")
				nameNode.appendChild(self.doc.createTextNode(funcName))
				codeNode = self.doc.createElement("code")
				
				node.appendChild(nameNode)
				node.appendChild(codeNode)
				
				self.inFunction = True
				print("ENTERED FUNCTION")
		else:
			if startswith(line, "import"):
				node = self.doc.createElement("import")
				param = self.parseExpr(line[len("import")+1:])
				if param.nodeValue or param.hasChildNodes():
					node.appendChild(param)
				else:
					raise CompilerException("#import keyword expects a module name")
			elif startswith(line, "return"):
				node = self.doc.createElement("return")
				param = self.parseExpr(line[len("return")+1:])
				if param.nodeValue or param.hasChildNodes():
					node.appendChild(param)
			elif startswith(line, "const"):
				node = self.doc.createElement("const")
				param = self.parseExpr(line[len("const")+1:])
				if param.hasChildNodes() and param.tagName == "assign":
					node.appendChild(param)
				else:
					raise CompilerException("#const keyword expects a variable assignment")
			elif startswith(line, "throw"):
				node = self.doc.createElement("throw")
				param = self.parseExpr(line[len("throw")+1:])
				if param.nodeValue or param.hasChildNodes():
					node.appendChild(param)
				else:
					raise CompilerException("#throw keyword expects a parameter (e.g. an exception object)")
			elif startswith(line, "break"):
				node = self.doc.createElement("break")
			elif startswith(line, "continue"):
				node = self.doc.createElement("continue")
			else:
				# Is it a function call?
				node = self.parseExpr(line)
				
				if node is None:
					raise CompilerException("Unknown command")
		return node
	
	# This function is only used for procedure calls
	def getFunctionCallNode(self, line):
		print("getFunctionCall " + line)
		line += " "
		lineLen = len(line)
		print("Len: " + str(lineLen))
		for i in range(lineLen):
			if line[i] == ' ':
				funcName = line[:i]
				print("Func: " + funcName)
				if self.functionExists(funcName):
					print("FOUND!")
					node = self.doc.createElement("call")
					func = self.doc.createElement("function")
					func.appendChild(self.doc.createTextNode(funcName))
					node.appendChild(func)
					
					# Parameters
					#===========================================================
					# parameterString = line[i+1:]
					# for parameter in parameterString.split(','):
					#	parameter = parameter.strip()
					#	paramNode = self.doc.createElement("parameter")
					#	paramNode.appendChild(self.parseExpr(parameter))
					#	node.appendChild(paramNode)
					#===========================================================
					paramNode = None
					params = self.parseExpr(line[i+1:])
					if params.nodeType == Node.ELEMENT_NODE and params.tagName == "parameters":
						paramNode = params
					else:
						paramNode = self.doc.createElement("parameters")
						singleParamNode = self.doc.createElement("parameter")
						singleParamNode.appendChild(params)
						paramNode.appendChild(singleParamNode)
					node.appendChild(paramNode)
					
					print("FUNC CALL")
					return node
				elif funcName.find('.') is not -1:
					print("OBJECT CALL")
					return self.parser.buildXMLTree(funcName + "(" + line[i+1:] + ")")
				elif self.keywordsBlock.__contains__(funcName):
					print("OH NOES!")
					raise CompilerException("Keyword #" + funcName + " needs an indented block on the next line")
				else:
					print("NONE")
					return None
					
			if not isVarChar(line[i]) and line[i] != '.':
				return None
		return None
	
	def parseExpr(self, expr):
		node = self.getFunctionCallNode(expr)
		if node is not None:
			return node
		else:
			node = self.parser.buildXMLTree(expr)
			return node
	
	def compileXMLToCode(self, code):
		pass
	
	def getName(self):
		return "BPC"