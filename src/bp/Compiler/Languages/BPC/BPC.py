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
		
	def initExprParser(self):
		self.parser = ExpressionParser()
		
		# Mul, Div
		operators = OperatorLevel()
		operators.addOperator(Operator("*", "multiply", Operator.BINARY))
		operators.addOperator(Operator("/", "divide", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
		# Add, Sub
		operators = OperatorLevel()
		operators.addOperator(Operator("+", "add", Operator.BINARY))
		operators.addOperator(Operator("-", "substract", Operator.BINARY))
		self.parser.addOperatorLevel(operators)
		
	def compileCodeToXML(self, code):
		lines = code.split('\n')
		self.doc = parseString("<root><header><title/><dependencies/></header><code></code></root>")
		self.initExprParser()
		
		root = self.doc.documentElement
		lastTabCount = 0
		currentNode = root.getElementsByTagName("code")[0]
		lastNode = currentNode
		
		for line in lines:
			if line:
				tabCount = 0
				while tabCount < len(line) and line[tabCount] == '\t':
					tabCount += 1
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
		if startswith(line, "if"):
			node = self.doc.createElement("if")
			condition = self.doc.createElement("condition")
			code = self.doc.createElement("code")
			
			condition.appendChild(self.parseExpr(line[3:]))
			
			node.appendChild(condition)
			node.appendChild(code)
		else:
			# Is it a function call?
			node = self.parseExpr(line)
			if node is None:
				# TODO: Error msg
				pass
		return node
	
	# This function is only used for procedure calls
	def getFunctionCallNode(self, line):
		for i in range(len(line)):
				if line[i] == ' ':
					funcName = line[:i]
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
		return None
	
	def parseExpr(self, expr):
		node = self.getFunctionCallNode(expr)
		if node is not None:
			return node
		else:
			return self.parser.buildXMLTree(expr) #self.doc.createTextNode(expr)
	
	def compileXMLToCode(self, code):
		pass
	
	def getName(self):
		return "BPC"