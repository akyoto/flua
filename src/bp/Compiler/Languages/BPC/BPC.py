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
		
	def initExprParser(self):
		self.parser = ExpressionParser()
		
		# See http://www.cppreference.com/wiki/operator_precedence
		
		# 2: Access
		operators = OperatorLevel()
		operators.addOperator(Operator(".", "access", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
		# 5: Mul, Div
		operators = OperatorLevel()
		operators.addOperator(Operator("*", "multiply", Operator.BINARY))
		operators.addOperator(Operator("/", "divide", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
		# 6: Add, Sub
		operators = OperatorLevel()
		operators.addOperator(Operator("+", "add", Operator.BINARY))
		operators.addOperator(Operator("-", "substract", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
		# 9: Comparison
		operators = OperatorLevel()
		operators.addOperator(Operator("==", "compare", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
		# 16: Assign
		operators = OperatorLevel()
		operators.addOperator(Operator("=", "assign", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
	def countTabs(self, line):
		tabCount = 0
		while tabCount < len(line) and line[tabCount] == '\t':
			tabCount += 1
		
		return tabCount
		
	def compileCodeToXML(self, code):
		lines = code.split('\n')
		self.doc = parseString("<root><header><title/><dependencies/></header><code></code></root>")
		self.initExprParser()
		
		root = self.doc.documentElement
		lastTabCount = 0
		currentNode = root.getElementsByTagName("code")[0]
		lastNode = currentNode
		
		for lineIndex in range(0, len(lines)):
			line = lines[lineIndex]
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
						else:
							currentNode = currentNode.parentNode
						atTab -= 1
					
					currentNode.appendChild(node)
				else:
					currentNode.appendChild(node)
				
				lastTabCount = tabCount
				lastNode = node
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
				node = self.doc.createElement("if")
				condition = self.doc.createElement("condition")
				code = self.doc.createElement("code")
				
				condition.appendChild(self.parseExpr(line[len("if")+1:]))
				
				node.appendChild(condition)
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
			# Is it a function call?
			node = self.parseExpr(line)
			if node is None:
				raise CompilerException("Unknown command")
		return node
	
	# This function is only used for procedure calls
	def getFunctionCallNode(self, line):
		print("getFunctionCall " + line)
		for i in range(len(line)):
			if line[i] == ' ':
				funcName = line[:i]
				if self.functionExists(funcName):
					node = self.doc.createElement("call")
					node.setAttribute("function", funcName)
					
					# Parameters
					parameterString = line[i+1:]
					for parameter in parameterString.split(','):
						parameter = parameter.strip()
						paramNode = self.doc.createElement("parameter")
						paramNode.appendChild(self.parseExpr(parameter))
						node.appendChild(paramNode)
					
					return node
			
			if not isVarChar(line[i]):
				return None
		return None
	
	def parseExpr(self, expr):
		node = self.getFunctionCallNode(expr)
		if node is not None:
			return node
		else:
			node = self.parser.buildXMLTree(expr)
			if node.nodeType == Node.TEXT_NODE:
				raise CompilerException("Unknown command")
			return node
	
	def compileXMLToCode(self, code):
		pass
	
	def getName(self):
		return "BPC"