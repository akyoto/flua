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
		
		self.keywordsBlock = ["if", "elif", "else", "while"]
		
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
		lines = code.split('\n')
		self.doc = parseString("<module><header><title/><dependencies/></header><code></code></module>")
		self.initExprParser()
		
		root = self.doc.documentElement
		lastTabCount = 0
		currentNode = root.getElementsByTagName("code")[0]
		lastNode = currentNode
		
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
					node = self.parseLine(line)
					
					#===============================================================
					# print("--------------------------")
					# print("Line: [" + line + "]")
					# print("Node: [" + node.tagName + "]")
					# print(node.getElementsByTagName("code"))
					# print("Current Node: [" + currentNode.parentNode.tagName + "." + currentNode.tagName + "]")
					#===============================================================
					
					# Block
					if tabCount > lastTabCount:
						currentNode = lastNode
						
						codeTags = currentNode.getElementsByTagName("code")
						if codeTags:
							currentNode = codeTags[0]
						
						currentNode.appendChild(node)
					elif tabCount < lastTabCount:
						atTab = lastTabCount
						while atTab > tabCount:
							if currentNode.tagName == "code":
								currentNode = currentNode.parentNode.parentNode
								if currentNode.tagName == "if-block" and node.tagName != "else-if" and node.tagName != "else":
									currentNode = currentNode.parentNode
							else:
								currentNode = currentNode.parentNode
							atTab -= 1
						
						currentNode.appendChild(node)
					else:
						currentNode.appendChild(node)
					
					# Check
					if node.nodeType == Node.TEXT_NODE:
						pass
					elif (node.tagName == "else-if" or node.tagName == "else") and currentNode.tagName != "if-block":
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
				raise CompilerException("Unknown keyword")
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
		for i in range(lineLen):
			if line[i] == ' ':
				funcName = line[:i]
				if self.functionExists(funcName):
					node = self.doc.createElement("call")
					node.setAttribute("function", funcName)
					
					# Parameters
					#===========================================================
					# parameterString = line[i+1:]
					# for parameter in parameterString.split(','):
					#	parameter = parameter.strip()
					#	paramNode = self.doc.createElement("parameter")
					#	paramNode.appendChild(self.parseExpr(parameter))
					#	node.appendChild(paramNode)
					#===========================================================
					paramNode = self.doc.createElement("parameters")
					paramNode.appendChild(self.parseExpr(line[i+1:]))
					node.appendChild(paramNode)
					
					return node
				elif self.keywordsBlock.__contains__(funcName):
					raise CompilerException("Keyword #" + funcName + " needs an indented block on the next line")
				else:
					return None
					
			if not isVarChar(line[i]):
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