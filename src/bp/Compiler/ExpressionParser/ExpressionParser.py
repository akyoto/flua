####################################################################
# Header
####################################################################
# Expression parser

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
from bp.Compiler.Utils import *

####################################################################
# Classes
####################################################################
class Operator:
	UNARY = 1
	BINARY = 2
	TERNARY = 3
	
	def __init__(self, text, name, dataType):
		self.text = text
		self.textLen = len(text)
		self.name = name
		self.type = dataType

class OperatorLevel:
	
	def __init__(self):
		self.operators = []
		
	def addOperator(self, op):
		self.operators.append(op)

class ExpressionParser:
	
	def __init__(self):
		self.operatorLevels = []
		#self.recursionLevel = 0
		self.doc = parseString("<expr></expr>")
		
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
		
	#def getDebugPrefix(self):
	#	return "   " * self.recursionLevel
		
	def buildCleanExpr(self, expr):
		#self.recursionLevel += 1
		
		#expr = expr.replace(" ", "")
		# Identifier + Space + Identifier = Invalid instruction
		exprLen = len(expr)
		for i in range(exprLen):
			if expr[i] == ' ':
				# TODO: Handle '([{' and ')]}' correctly
				if i + 1 < exprLen and i >= 1 and isVarChar(expr[i - 1]) and isVarChar(expr[i + 1]): #and expr[i + 1:i + 11] != "bp_string_":
					raise CompilerException("Operator missing: %s" % (expr[:i].strip() + " ↓ " + expr[i+1:].strip()))
		
		expr = expr.replace(" ", "")
		exprLen = len(expr)
		i = 0
		lastOccurence = 0
		start = 0
		end = 0
		bracketCounter = 0
		operators = None
		operandLeft = ""
		operandRight = ""
		char = ''
		
		#print(self.getDebugPrefix() + " * buildCleanExpr: " + expr)
		
		# For every operator level
		for opLevel in self.operatorLevels:
			i = 0
			while i < exprLen:
				operators = opLevel.operators
				
				# For every operator in the current level
				for op in operators:
					if i < exprLen - op.textLen and expr[i:i+op.textLen] == op.text:
						lastOccurence = i
					else:
						lastOccurence = -1
					
					if lastOccurence is not -1:
						if lastOccurence == exprLen - 1:
							raise CompilerException("Missing operand")
						if isVarChar(expr[lastOccurence + op.textLen]) or expr[lastOccurence + op.textLen] == '(' or op.text == '(' or expr[lastOccurence + op.textLen] == '[' or op.text == '[':
							if op.type == Operator.BINARY:
								
								# Left operand
								start = lastOccurence - 1

								while start >= 0 and (isVarChar(expr[start]) or ((expr[start] == ')' or expr[start] == ']') and start == lastOccurence - 1)):
									if expr[start] == ')' or expr[start] == ']':
										bracketCounter = 1
									else:
										bracketCounter = 0

									# Move to last part of the bracket
									while bracketCounter > 0 and start > 0:
										start -= 1
										if expr[start] == ')' or expr[start] == ']':
											bracketCounter += 1
										elif expr[start] == '(' or expr[start] == '[':
											bracketCounter -= 1
									start -= 1

								operandLeft = expr[start+1:lastOccurence]

								# Right operand
								end = lastOccurence + op.textLen

								if op.text == '[' or op.text == '(' or (expr[end] == '(' and end == lastOccurence + op.textLen) or (expr[end] == '[' and end == lastOccurence + op.textLen):
									bracketCounter = 1
								else:
									bracketCounter = 0

								while end < exprLen and (bracketCounter > 0 or isVarChar(expr[end]) or (end == lastOccurence + op.textLen and (expr[end] == '(' or expr[end] == '['))):
									# Move to last part of the bracket
									while bracketCounter > 0 and end < exprLen:
										if expr[end] == '(' or expr[end] == '[':
											bracketCounter += 1
										elif expr[end] == ')' or expr[end] == ']':
											bracketCounter -= 1
											if bracketCounter == 1 and op.text != '[' and op.text != '(':
												end -= 1
												bracketCounter = 0
											elif bracketCounter == 0: # and expr[lastOccurence + op.textLen] != '(' and expr[lastOccurence + op.textLen] != '[':
												end -= 2
										end += 1
									end += 1

								operandRight = expr[lastOccurence + op.textLen:end]
								
								# Perform "no digits at the start of an identifier" check for the left operator
								if operandLeft:
									operandLeftStartsWithDigit = operandLeft[0].isdigit()
									if operandLeftStartsWithDigit:
										for c in operandLeft:
											if not c.isdigit():
												if isVarChar(c):
													if operandLeft[0] != '0' or operandLeft[1] != 'x':
														raise CompilerException("Identifiers must not begin with a digit: '%s'" % (operandLeft))
												else:
													break
								
								# Perform "no digits at the start of an identifier" check for the right operator
								if operandRight:
									operandRightStartsWithDigit = operandRight[0].isdigit()
									if operandRightStartsWithDigit:
										for c in operandRight:
											if not c.isdigit():
												if isVarChar(c):
													if operandRight[0] != '0' or operandRight[1] != 'x':
														raise CompilerException("Identifiers must not begin with a digit: '%s'" % (operandRight))
												else:
													break
								
								#if op.text != "(":
								#	if (operandRight and operandRight[0].isdigit() and not operandRight.isdigit()):
								#		raise CompilerException("ERZA RIGHT %s %s %s" % (operandLeft, op.text, operandRight))
								
#								if op.text == "&&":
#									print(">> " + operandLeft + " AND " + operandRight)
#									print(expr)
#									print(lastOccurence)
#									print(end)
#									print(expr[lastOccurence:end])
#									print(bracketCounter)
								
								#print(self.getDebugPrefix() + " * buildCleanExpr.operators: " + operandLeft + " [" + op.text + "] " + operandRight)
								
								# Bind
								#===================================================
								# #=======================================================
								# print(expr)
								# if start >= 0:
								#	print("START[" + str(start) + "]: " + expr[start])
								# else:
								#	print("START: " + "OUT OF STRING")
								# 
								# if end < exprLen:
								#	print("END[" + str(end) + "]: " + expr[end])
								# else:
								#	print("END: " + "OUT OF STRING")
								# #=======================================================
								#===================================================
								if operandLeft and (operandRight and ((start < 0 or expr[start] != '(') or (end >= exprLen or expr[end] != ')')) or op.text == "("):
									if op.text == "(":
										newOpText = "#"
										expr = "%s(%s)%s(%s)%s" % (expr[:lastOccurence - len(operandLeft)], operandLeft, newOpText, operandRight, expr[lastOccurence + op.textLen + len(operandRight) + 1:])
									elif op.text == "[":
										newOpText = "@"
										expr = "%s(%s)%s(%s)%s" % (expr[:lastOccurence - len(operandLeft)], operandLeft, newOpText, operandRight, expr[lastOccurence + op.textLen + len(operandRight) + 1:])
									else:
										expr = "%s(%s%s%s)%s" % (expr[:lastOccurence - len(operandLeft)], operandLeft, op.text, operandRight, expr[lastOccurence + op.textLen + len(operandRight):])
									exprLen = len(expr)
									#print(self.getDebugPrefix() + "    * Expression changed: " + expr)
								#else:
								#	pass
									#print(self.getDebugPrefix() + "    * Expression change denied for operator: [" + op.text + "]")
								
							elif op.type == Operator.UNARY and (lastOccurence <= 0 or (isVarChar(expr[lastOccurence - 1]) == False and expr[lastOccurence - 1] != ')')):
								#print("Unary check for operator [" + op.text + "]")
								#print("  Unary.lastOccurence: " + str(lastOccurence))
								#print("  Unary.expr[lastOccurence - 1]: " + expr[lastOccurence - 1])
								#print("  Unary.isVarChar(expr[lastOccurence - 1]): " + str(isVarChar(expr[lastOccurence - 1])))
								
								# Right operand
								end = lastOccurence + op.textLen
								while end < exprLen and (isVarChar(expr[end]) or ((expr[end] == '(' or expr[end] == '[') and end == lastOccurence + 1)):
									if (expr[end] == '(' or expr[end] == '[') and end == lastOccurence + 1:
										bracketCounter = 1
									else:
										bracketCounter = 0
									
									# Move to last part of the bracket
									while bracketCounter > 0 and end < exprLen-1:
										end += 1
										if expr[end] == '(' or expr[end] == '[':
											bracketCounter += 1
										elif expr[end] == ')' or expr[end] == ']':
											bracketCounter -= 1
									end += 1
								
								operandRight = expr[lastOccurence+op.textLen:end]
								
								#print("[" + op.text + "] " + operandRight)
								
								start = lastOccurence - 1
								
								if (start < 0 or expr[start] != '(') or (end >= exprLen or expr[end] != ')'):
									expr = expr[:lastOccurence] + "(" + op.text + operandRight + ")" + expr[lastOccurence + op.textLen + len(operandRight):]
									exprLen = len(expr)
									lastOccurence += 1
									#print("EX.UNARY: " + expr)
								else:
									pass
									#print("EX.UNARY expression change denied: [" + op.text + "]")
							else:
								# If a binary version does not exist it means the operator has been used incorrectly
								if not self.similarOperatorExists(op):
									raise CompilerException("Syntax error concerning the unary operator [" + op.text + "]")
						elif expr[lastOccurence + op.textLen] != '(' and expr[lastOccurence + op.textLen] != '[':
							if self.similarOperatorExists(op):
								pass
							else:
								raise CompilerException("Operator [" + op.text + "] expects a valid expression (encountered '" + expr[lastOccurence + op.textLen] + "')")
							#lastOccurence = expr.find(op.text, lastOccurence + op.textLen)
						i += op.textLen
				else:
					i += 1
		
		#self.recursionLevel -= 1
		return expr
		
	def buildOperation(self, expr):
		#self.recursionLevel += 1
		
		# Debug info
		#print(self.getDebugPrefix() + " * buildOperation.dirty: " + expr)
		
		# Remove unnecessary brackets
		bracketCounter = 0
		i = len(expr)
		while expr and expr[0] == '(' and expr[len(expr)-1] == ')' and bracketCounter == 0 and i == len(expr):
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
				#print("NEW EXPR: " + expr)
				
				# In order to continue the loop: Adjust i
				i = len(expr)
				
		#print("    * buildOperation.clean: " + expr)
		
		# Left operand
		bracketCounter = 0
		i = 0
		while i < len(expr) and (isVarChar(expr[i]) or expr[i] == '('):
			while i < len(expr) and (bracketCounter > 0 or expr[i] == '('):
				if expr[i] == '(' or expr[i] == '[':
					bracketCounter += 1
				elif expr[i] == ')' or expr[i] == ']':
					bracketCounter -= 1
					if bracketCounter == 0:
						break
				i += 1
			i += 1
		
		if i == len(expr):
			#self.recursionLevel -= 1
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
		
		#print("---")
		#print("OP: " + operator)
		#print(leftOperand)
		#print(rightOperand)
		#print("---")
		
		node = self.doc.createElement(opName)
		lNode = self.doc.createElement("value")
		rNode = self.doc.createElement("value")
		
		# Unary operator
		if leftOperand:
			node.appendChild(lNode)
		node.appendChild(rNode)
		
		lNode.appendChild(leftOperandNode)
		rNode.appendChild(rightOperandNode)
		
#		if operator == "=" and leftOperandNode.nodeType == Node.TEXT_NODE:
#			if self.getCurrentScope().containsVariable(leftOperand):
#				pass
#			else:
#				#print("Variable declaration: " + leftOperand)
#				self.getCurrentScope().addVariable(GenericVariable(leftOperand, "Unknown"))
		
		# Right operand missing
		if len(rightOperand) == 0:
			if operator == "=":
				raise CompilerException("You need to assign a valid value to '%s'" % leftOperand)
			raise CompilerException("Operator [" + operator + "] expects a second operator")
		
		#self.recursionLevel -= 1
		
		return node
		
	def buildXMLTree(self, expr):
		#print(" * buildXMLTree: " + expr)
		if not expr:
			raise CompilerException("Expression missing")
		if expr[0] != '~' and isDefinitelyOperatorSign(expr[0]):
			raise CompilerException("Invalid expression: '%s'" % expr)
		
		#node = self.doc.createElement("expr")
		
		# TODO: Remove double whitespaces
		
		# TODO: Check this:
		expr = expr.replace(" is not ", " != ")
		
		# Whitespaces are required!
		expr = expr.replace("\t", " ")
		expr = expr.replace(" and ", " && ")
		expr = expr.replace(" or ", " || ")
		expr = expr.replace(" is ", " == ")
		#expr = expr.replace(" in ", " }= ")
		
		if expr.startswith("-"):
			#print("------------- MINUS -----------")
			expr = "-(%s)" % expr[1:]
		
		# TODO: Optimize and correct this
		expr = " " + expr
		expr = expr.replace(" not ", "!")
		expr = expr.replace(" not(", "!(")
		expr = expr.replace("(not", "(!")
		expr = expr.replace("[not", "[!")
		#if expr.startswith(" not") and len(expr) > 4 and not isVarChar(expr[4]):
		#	expr = "!" + expr[4:]
		#print("buildXMLTree: " + expr)
		
		expr = self.buildCleanExpr(expr)
		opNode = self.buildOperation(expr)
		self.adjustXMLTree(opNode)
		
		#node.appendChild(opNode)
		return opNode#node.firstChild
	
	def adjustXMLTree(self, node):
		# Adjust node
		if node.nodeType == Node.ELEMENT_NODE:
			if node.tagName == "separate":
				node.tagName = "parameters"
				
				# 'parameters' sub nodes
				child = node.firstChild
				while child is not None:
					child.tagName = "parameter"
					
					# TODO: Optimize this
					
					# Put all nested "separates" on the same level
					if child.hasChildNodes() and child.firstChild.nodeType == Node.ELEMENT_NODE and child.firstChild.tagName == "separate":
						for param in child.firstChild.childNodes:
							node.insertBefore(param.cloneNode(True), child)
						
						node.removeChild(child)
						child = node.firstChild
						
						# 2
						#oldChild = child
						#child = node.firstChild
						#node.removeChild(oldChild)
						continue
					
					child = child.nextSibling
				
				# 'parameter' tag name
				#for child in node.childNodes:
				#	child.tagName = "parameter"
			elif node.tagName == "call":
				# Object based method calls will be ignored for this test
				node.firstChild.tagName = "function"
				
				node.replaceChild(self.getParametersNode(node.childNodes[1].firstChild), node.childNodes[1])
				
				# Clean up whitespaces
				#for child in node.childNodes:
				#	if child.nodeType == Node.TEXT_NODE:
				#		node.removeChild(child)
			elif node.tagName == "access":
				# Correct float values being interpreted as access calls
				value1 = node.childNodes[0].childNodes[0]
				value2 = node.childNodes[1].childNodes[0]
				
				if value1.nodeType == Node.TEXT_NODE and value2.nodeType == Node.TEXT_NODE and value1.nodeValue.isdigit() and value2.nodeValue.isdigit():
					parent = node.parentNode
					parent.insertBefore(self.doc.createTextNode(value1.nodeValue + "." + value2.nodeValue), node)
					parent.removeChild(node)
			# Slice operator
			elif node.tagName == "index":
				value1 = node.childNodes[0].childNodes[0]
				value2 = node.childNodes[1].childNodes[0]
				
				if value2.nodeType != Node.TEXT_NODE and value2.tagName == "declare-type":
					node.tagName = "slice"
					value2.tagName = "range"
					value2.childNodes[0].tagName = "from"
					value2.childNodes[1].tagName = "to"
			
			# Object-oriented call
#			elif node.tagName == "access":
#				try:
#					if node.childNodes[1].firstChild.tagName == "call":
#						node.tagName = "call"
#						node.firstChild.tagName = "object"
#						secondValue = node.childNodes[1]
#						callNode = secondValue.firstChild
#						
#						for child in callNode.childNodes:
#							node.appendChild(child.cloneNode(True))
#						node.removeChild(node.childNodes[1])
#						node.childNodes[1].tagName = "function"
#						node.childNodes[2].tagName = "parameters"
#						
#						params = node.childNodes[2].firstChild.cloneNode(True)
#						node.appendChild(self.getParametersNode(params))
#						node.removeChild(node.childNodes[2])
#				except AttributeError:
#					pass
#				except:
#					raise
		
		# Recursive
		for child in node.childNodes:
			self.adjustXMLTree(child)
	
	# Helper methods
	def getParametersNode(self, params):
		# Text
		if params.nodeType == Node.TEXT_NODE and params.nodeValue:
			allParams = self.doc.createElement("parameters")
			thisParam = self.doc.createElement("parameter")
			
			thisParam.appendChild(params)
			allParams.appendChild(thisParam)
			return allParams
		# Elements
		elif params.nodeType == Node.ELEMENT_NODE:
			# Multiple parameters
			if params.tagName == "separate" or params.tagName == "parameters":
				return params
			# Single parameter (needs to be enclosed by parameter tags)
			else:
				allParams = self.doc.createElement("parameters")
				param = self.doc.createElement("parameter")
				param.appendChild(params.cloneNode(True))
				allParams.appendChild(param)
				return allParams
		# Exception
		else:
			# Empty text
			return self.doc.createElement("parameters")
		
# Helper functions
def getParameterFuncName(node):
	if node.firstChild.nodeType == Node.TEXT_NODE:
		return node.firstChild.nodeValue
	elif node.firstChild.tagName == "assign":
		return node.firstChild.firstChild.firstChild.nodeValue
	else:
		raise CompilerException("Invalid parameter initialization")
	
def getParameterDefaultValueNode(node):
	if node.firstChild.nodeType == Node.TEXT_NODE:
		return None
	elif node.firstChild.tagName == "assign":
		return node.firstChild.childNodes[1].firstChild
	else:
		raise CompilerException("Invalid parameter default value")
		
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
