####################################################################
# Header
####################################################################
# Blitzprog Compiler
# 
# Website: www.blitzprog.de
# Started: 19.07.2008 (Sat, Jul 19 2008)

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
from Utils import *
from xml.dom.minidom import *

####################################################################
# Classes
####################################################################
class CompilerException(Exception):
	
	def __init__(self, value):
		self.value = value
		self.line = -1
		
	def getMsg(self):
		return self.value
		
	def getLine(self):
		return self.line
		
	def setLine(self, line):
		self.line = line
		
	def __str__(self):
		return repr(self.value)

class Operator:
	UNARY = 1
	BINARY = 2
	TERNARY = 3
	
	def __init__(self, text, name, type):
		self.text = text
		self.textLen = len(text)
		self.name = name
		self.type = type

class OperatorLevel:
	
	def __init__(self):
		self.operators = []
		
	def addOperator(self, op):
		self.operators.append(op)

class ExpressionParser:
	
	def __init__(self):
		self.operatorLevels = []
		self.doc = None
		
	def compileError(self, error):
		raise CompilerException(error)
		
	def addOperatorLevel(self, opLevel):
		self.operatorLevels.append(opLevel)
		
	def getOperatorName(self, opSign, opType):
		# For every operator level
		for opLevel in self.operatorLevels:
			# For every operator in the current level
			for op in opLevel.operators:
				if op.text == opSign and op.type == opType:
					return op.name
		return ""
	
	def similarOperatorExists(self, op2):
		# For every operator level
		for opLevel in self.operatorLevels:
			# For every operator in the current level
			for op in opLevel.operators:
				if op != op2 and op.text.find(op2.text) != -1:
					return True
		return False
		
	def buildOperation(self, expr):
		print("buildOperation.dirty: " + expr)
		
		bracketCounter = 0
		i = len(expr)
		while expr and expr[0] == '(' and expr[len(expr)-1] == ')' and bracketCounter == 0 and i == len(expr):
			#print("WHIIIIILE")
			bracketCounter = 1
			i = 1
			while i < len(expr) and (bracketCounter > 0 or expr[i] == ')'):
				if expr[i] == '(':
					bracketCounter += 1
				elif expr[i] == ')':
					bracketCounter -= 1
				i += 1
			
			if bracketCounter == 0 and i == len(expr):
				expr = expr[1:len(expr)-1]
				print("NEW EXPR: " + expr)
				
				# In order to continue the loop: Adjust i
				i = len(expr)
				
		print("buildOperation.clean: " + expr)
		
		# Left operand
		bracketCounter = 0
		i = 0
		while i < len(expr) and (isVarChar(expr[i]) or expr[i] == '('):
			while bracketCounter > 0 or (i < len(expr) and expr[i] == '('):
				if expr[i] == '(':
					bracketCounter += 1
				elif expr[i] == ')':
					bracketCounter -= 1
					if bracketCounter == 0:
						break
				i += 1
			i += 1
		
		if i == len(expr):
			return self.doc.createTextNode(expr)
		
		leftOperand = expr[:i]
		opIndex = i
		
		# Operator
		opIndexEnd = opIndex
		while opIndexEnd < len(expr) and not isVarChar(expr[opIndexEnd]) and not expr[opIndexEnd] == '(':
			opIndexEnd += 1
		operator = expr[opIndex:opIndexEnd]
		
		if leftOperand:
			opName = self.getOperatorName(operator, Operator.BINARY)
		else:
			opName = self.getOperatorName(operator, Operator.UNARY)
		
		if not opName:
			return self.doc.createTextNode(leftOperand)
		
		# Right operand
		bracketCounter = 0
		i = opIndex + len(operator)
		while i < len(expr) and (isVarChar(expr[i]) or expr[i] == '('):
			while bracketCounter > 0 or (i < len(expr) and expr[i] == '('):
				if expr[i] == '(':
					bracketCounter += 1
				elif expr[i] == ')':
					bracketCounter -= 1
					if bracketCounter == 0:
						break
				i += 1
			i += 1
		
		rightOperand = expr[opIndex+len(operator):i]
		
		leftOperandNode = None
		rightOperandNode = None
		
		if leftOperand and leftOperand[0] == '(':
			leftOperandNode = self.buildOperation(leftOperand[1:len(leftOperand)-1])
		else:
			leftOperandNode = self.doc.createTextNode(leftOperand)
			
		if rightOperand and rightOperand[0] == '(':
			rightOperandNode = self.buildOperation(rightOperand[1:len(rightOperand)-1])
		else:
			rightOperandNode = self.doc.createTextNode(rightOperand)
		
		print("---")
		print("OP: " + operator)
		print(leftOperand)
		print(rightOperand)
		print("---")
		
		node = self.doc.createElement(opName)
		lNode = self.doc.createElement("value")
		rNode = self.doc.createElement("value")
		
		# Unary operator
		if leftOperand:
			node.appendChild(lNode)
		node.appendChild(rNode)
		
		lNode.appendChild(leftOperandNode)
		rNode.appendChild(rightOperandNode)
		
		return node
		
	def buildXMLTree(self, expr):
		self.doc = parseString("<expr></expr>")
		node = self.doc.documentElement
		
		print("buildXMLTree: " + expr)
		
		expr = self.buildCleanExpr(expr)
		opNode = self.buildOperation(expr)
		self.adjustXMLTree(opNode)
		
		node.appendChild(opNode)
		return node.firstChild
	
	def adjustXMLTree(self, node):
		# Adjust node
		if node.nodeType == Node.ELEMENT_NODE:
			if node.tagName == "separate":
				node.tagName = "parameters"
				
				# 'parameters' sub nodes
				child = node.firstChild
				while child is not None:
					if child.hasChildNodes() and child.firstChild.nodeType == Node.ELEMENT_NODE and child.firstChild.tagName == "separate":
						for param in child.firstChild.childNodes:
							node.insertBefore(param.cloneNode(True), child)
						oldChild = child
						child = node.firstChild
						node.removeChild(oldChild)
						continue
					child = child.nextSibling
				
				# 'parameter' tag name
				for child in node.childNodes:
					child.tagName = "parameter"
			elif node.tagName == "call":
				node.firstChild.tagName = "function"
				params = node.childNodes[1].firstChild.cloneNode(True)
				if params.nodeType == Node.TEXT_NODE and params.nodeValue:
					allParams = self.doc.createElement("parameters")
					thisParam = self.doc.createElement("parameter")
					
					thisParam.appendChild(params)
					allParams.appendChild(thisParam)
					node.appendChild(allParams)
				elif params.nodeType == Node.ELEMENT_NODE:
					print(params.tagName)
					if params.tagName == "parameters":
						for child in params:
							node.appendChild(child.cloneNode(True))
					else:
						node.appendChild(params)
				else:
					#allParams = self.doc.createElement("parameters")
					#node.appendChild(allParams)
					pass
				node.removeChild(node.childNodes[1])
				
				# Clean up whitespaces
				for child in node.childNodes:
					if child.nodeType == Node.TEXT_NODE:
						node.removeChild(child)
			elif node.tagName == "access":
				try:
					if node.childNodes[1].firstChild.tagName == "call":
						node.tagName = "call"
						node.firstChild.tagName = "object"
						secondValue = node.childNodes[1]
						callNode = secondValue.firstChild
						
						for child in callNode.childNodes:
							node.appendChild(child.cloneNode(True))
						node.removeChild(node.childNodes[1])
						node.childNodes[1].tagName = "function"
						node.childNodes[2].tagName = "parameters"
				except AttributeError:
					pass
				except:
					raise
		
		# Recursive
		for child in node.childNodes:
			self.adjustXMLTree(child)
	def buildCleanExpr(self, expr):
		expr = expr.replace(" ", "")
		
		print("buildCleanExpr: " + expr)
		
		# For every operator level
		for opLevel in self.operatorLevels:
			# For every operator in the current level
			for op in opLevel.operators:
				lastOccurence = expr.find(op.text)
				while lastOccurence is not -1:
					if lastOccurence == len(expr) - 1:
						raise CompilerException("Missing operand")
					if isVarChar(expr[lastOccurence + len(op.text)]) or expr[lastOccurence + len(op.text)] == '(' or op.text == '(':
						if op.type == Operator.BINARY:
							# Left operand
							start = lastOccurence - 1
							
							while start >= 0 and (isVarChar(expr[start]) or (expr[start] == ')' and start == lastOccurence - 1)):
								if expr[start] == ')':
									bracketCounter = 1
								else:
									bracketCounter = 0
								
								# Move to last part of the bracket
								while bracketCounter > 0 and start > 0:
									start -= 1
									if expr[start] == ')':
										bracketCounter += 1
									elif expr[start] == '(':
										bracketCounter -= 1
								start -= 1
							
							operandLeft = expr[start+1:lastOccurence];
							
							# Right operand
							end = lastOccurence + op.textLen
							while end < len(expr) and (isVarChar(expr[end]) or (expr[end] == '(' and end == lastOccurence + 1)):
								if op.text == '(' or (expr[end] == '(' and end == lastOccurence + 1):
									bracketCounter = 1
								else:
									bracketCounter = 0
								
								# Move to last part of the bracket
								while bracketCounter > 0 and end < len(expr)-1:
									end += 1
									if expr[end] == '(':
										bracketCounter += 1
									elif expr[end] == ')':
										bracketCounter -= 1
								end += 1
							
							operandRight = expr[lastOccurence+op.textLen:end];
							
							print("  buildCleanExpr: " + operandLeft + " [" + op.text + "] " + operandRight)
							
							# Bind
							#=======================================================
							print(expr)
							if start >= 0:
								print("START[" + str(start) + "]: " + expr[start])
							else:
								print("START: " + "OUT OF STRING")
							
							if end < len(expr):
								print("END[" + str(end) + "]: " + expr[end])
							else:
								print("END: " + "OUT OF STRING")
							#=======================================================
							
							if operandLeft and (operandRight and ((start < 0 or expr[start] != '(') or (end >= len(expr) or expr[end] != ')')) or op.text == "("):
								if op.text != "(":
									expr = expr[:lastOccurence - len(operandLeft)] + "(" + operandLeft + op.text + operandRight + ")" + expr[lastOccurence + len(op.text) + len(operandRight):]
								else:
									expr = expr[:lastOccurence - len(operandLeft)] + "((" + operandLeft + ")#" + op.text + operandRight + ")" + expr[lastOccurence + len(op.text) + len(operandRight):]
								print("EX.BINARY: " + expr)
							else:
								print("EX.BINARY expression change denied: [" + op.text + "]")
							
						elif op.type == Operator.UNARY and (lastOccurence <= 0 or (isVarChar(expr[lastOccurence - 1]) == False and expr[lastOccurence - 1] != ')')):
							print("Unary check for operator [" + op.text + "]")
							#print("  Unary.lastOccurence: " + str(lastOccurence))
							#print("  Unary.expr[lastOccurence - 1]: " + expr[lastOccurence - 1])
							#print("  Unary.isVarChar(expr[lastOccurence - 1]): " + str(isVarChar(expr[lastOccurence - 1])))
							
							# Right operand
							end = lastOccurence + op.textLen
							while end < len(expr) and (isVarChar(expr[end]) or (expr[end] == '(' and end == lastOccurence + 1)):
								if expr[end] == '(' and end == lastOccurence + 1:
									bracketCounter = 1
								else:
									bracketCounter = 0
								
								# Move to last part of the bracket
								while bracketCounter > 0 and end < len(expr)-1:
									end += 1
									if expr[end] == '(':
										bracketCounter += 1
									elif expr[end] == ')':
										bracketCounter -= 1
								end += 1
							
							operandRight = expr[lastOccurence+op.textLen:end];
							
							print("[" + op.text + "] " + operandRight)
							
							start = lastOccurence - 1
							
							if (start < 0 or expr[start] != '(') or (end >= len(expr) or expr[end] != ')'):
								expr = expr[:lastOccurence] + "(" + op.text + operandRight + ")" + expr[lastOccurence + len(op.text) + len(operandRight):]
								lastOccurence += 1
								print("EX.UNARY: " + expr)
							else:
								print("EX.UNARY expression change denied: [" + op.text + "]")
						else:
							# If a binary version does not exist it means the operator has been used incorrectly
							if not self.similarOperatorExists(op):
								raise CompilerException("Syntax error concerning the unary operator [" + op.text + "]")
					elif expr[lastOccurence + len(op.text)] != '(':
						if self.similarOperatorExists(op):
							pass
						else:
							raise CompilerException("Operator [" + op.text + "] expects a valid expression (encountered '" + expr[lastOccurence + len(op.text)] + "')")
					lastOccurence = expr.find(op.text, lastOccurence + len(op.text))
		return expr

####################################################################
# Main
####################################################################
if __name__ == '__main__':
	try:
		parser = ExpressionParser()
		
		# Mul, Div
		operators = OperatorLevel()
		operators.addOperator(Operator("*", "multiply", Operator.BINARY))
		operators.addOperator(Operator("/", "divide", Operator.BINARY))
		parser.addOperatorLevel(operators)
		
		# Add, Sub
		operators = OperatorLevel()
		operators.addOperator(Operator("+", "add", Operator.BINARY))
		operators.addOperator(Operator("-", "substract", Operator.BINARY))
		parser.addOperatorLevel(operators)
		
		tree = parser.buildXMLTree("(2 + 5) * 3")
		
		print(tree.toprettyxml())
	except:
		printTraceback()