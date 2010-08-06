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
class Operator:
	UNARY = 1
	BINARY = 2
	TERNARY = 3
	
	def __init__(self, text, type):
		self.text = text
		self.textLen = len(text)
		self.type = type

class OperatorLevel:
	
	def __init__(self):
		self.operators = []
		
	def addOperator(self, op):
		self.operators.append(op)

class ExpressionParser:
	
	def __init__(self):
		self.operatorLevels = []
		
	def addOperatorLevel(self, opLevel):
		self.operatorLevels.append(opLevel)
	
	def buildXMLTree(self, expr):
		node = parseString("<expr></expr>").documentElement
		
		# TODO: Use it
		self.buildCleanExpr(expr)
		
		return node
	
	def buildCleanExpr(self, expr):
		expr = expr.replace(" ", "")
		exprLen = len(expr)
		
		# For every character in expr
		for i in range(0, exprLen):
			# For every operator level
			for opLevel in self.operatorLevels:
				# For every operator in the current level
				for op in opLevel.operators:
					if expr[i:i+op.textLen] == op.text:
						if op.type == Operator.BINARY:
							# Left operand
							start = i - 1
							while start >= 0 and (isVarChar(expr[start]) or expr[start] == ')'):
								bracketCounter = 1
								while bracketCounter > 0 and start > 0:
									start -= 1
									if expr[start] == ')':
										bracketCounter += 1
									elif expr[start] == '(':
										bracketCounter -= 1
								start -= 1
							
							operandLeft = expr[start+1:i];
							
							# Right operand
							end = i + op.textLen
							while end < len(expr) and isVarChar(expr[end]):
								end += 1
							operandRight = expr[i+1:end];
							
							print(operandLeft + " " + op.text + " " + operandRight)
		return expr

####################################################################
# Main
####################################################################
if __name__ == '__main__':
	try:
		parser = ExpressionParser()
		
		# Add, Sub
		operators = OperatorLevel()
		operators.addOperator(Operator("+", Operator.BINARY))
		operators.addOperator(Operator("-", Operator.BINARY))
		parser.addOperatorLevel(operators)
		
		tree = parser.buildXMLTree("(14 + (17 + 4)) + (21 - 42)")
		print(tree.toprettyxml())
	except:
		printTraceback()