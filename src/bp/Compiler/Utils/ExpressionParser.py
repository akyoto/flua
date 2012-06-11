####################################################################
# Header
####################################################################
# Expression parser utils

####################################################################
# License
####################################################################
# (C) 2012  Eduard Urbach
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
from bp.Compiler.ExpressionParser import *

####################################################################
# Global
####################################################################
globalBPCParser = None

# See http://www.cppreference.com/wiki/operator_precedence
bpOperatorLevels = [
	# 1: Function calls
	[
		Operator("(", "call.unused", Operator.BINARY),
		Operator("§", "template-call", Operator.BINARY),
	],
	
	# 2: Access
	[
		Operator(".", "access", Operator.BINARY),
		Operator("[", "index.unused", Operator.BINARY),
		Operator("#", "call", Operator.BINARY),
		Operator("@", "index", Operator.BINARY),
	],
	
	# Loose pointer
	[
		Operator("~", "unmanaged", Operator.UNARY),
	],
	
	# Type declaration
	[
		Operator(":", "declare-type", Operator.BINARY),
		Operator("}=", "exists-in", Operator.BINARY),
	],
	
	# 3: Unary
	[
		Operator("!", "not", Operator.UNARY),
		Operator("-", "negative", Operator.UNARY),
	],
	
	# 5: Mul, Div
	[
		Operator("*", "multiply", Operator.BINARY),
		Operator("/", "divide", Operator.BINARY),
		Operator("\\", "divide-floor", Operator.BINARY),
		Operator("%", "modulo", Operator.BINARY),
	],
	
	# 6: Add, Sub
	[
		Operator("+", "add", Operator.BINARY),
		Operator("-", "subtract", Operator.BINARY),
	],
		
	# 7: Shift operations
	[
		Operator("<<", "shift-left", Operator.BINARY),
		Operator(">>", "shift-right", Operator.BINARY),
	],
		
	# 8: GT, LT
	[
		Operator(">=", "greater-or-equal", Operator.BINARY),
		Operator(">", "greater", Operator.BINARY),
		Operator("<=", "less-or-equal", Operator.BINARY),
		Operator("<", "less", Operator.BINARY),
	],
		
	# 9: Comparison
	[
		Operator("==", "equal", Operator.BINARY),
		Operator("!=", "not-equal", Operator.BINARY),
		Operator("~=", "almost-equal", Operator.BINARY),
	],
	
	# 10: Bitwise AND
	[
		Operator("&", "bitwise-and", Operator.BINARY),
	],
	
	# 12: Bitwise OR
	[
		Operator("|", "bitwise-or", Operator.BINARY),
	],
	
	# 13: Logical AND
	[
		Operator("&&", "and", Operator.BINARY),
	],
		
	# 14: Logical OR
	[
		Operator("||", "or", Operator.BINARY),
	],
	
	# 15: Ternary operator
	#[
		#	operators = OperatorLevel()
		#	Operator(":", "ternary-code", Operator.BINARY),
		#	parser.addOperatorLevel(operators)
		#	
		#	operators = OperatorLevel()
		#	Operator("?", "ternary-condition", Operator.BINARY),
		#	parser.addOperatorLevel(operators)
	#],
		
	# 16: Assign
	[
		Operator("+=", "assign-add", Operator.BINARY),
		Operator("-=", "assign-subtract", Operator.BINARY),
		Operator("*=", "assign-multiply", Operator.BINARY),
		Operator("/=", "assign-divide", Operator.BINARY),
		Operator("<<=", "assign-shift-left", Operator.BINARY),
		Operator(">>=", "assign-shift-right", Operator.BINARY),
		#Operator("}=", "assign-each-in", Operator.BINARY),
		Operator("=", "assign", Operator.BINARY),
		Operator("-->", "flow-delayed-to", Operator.BINARY),
		Operator("<--", "flow-delayed-from", Operator.BINARY),
		Operator("->", "flow-to", Operator.BINARY),
		Operator("<-", "flow-from", Operator.BINARY),
	],
	
	# Comma
	[
		Operator(",", "separate", Operator.BINARY),
	]
]

translateLogicalOperatorSign = {
	"&&" : "and",
	"||" : "or"
}

####################################################################
# Functions
####################################################################
def hasHigherOrEqualPriority(operationA, operationB):
	aLevel = 0
	bLevel = 0
	count = 0
	for opLevel in bpOperatorLevels:
		count += 1
		for op in opLevel:
			if op.name == operationB:
				bLevel = -count
			
			if op.name == operationA:
				aLevel = -count
			
			if aLevel and bLevel:
				return aLevel >= bLevel
	
	return False

def hasHigherPriority(operationA, operationB):
	aLevel = 0
	bLevel = 0
	count = 0
	for opLevel in bpOperatorLevels:
		count += 1
		for op in opLevel:
			if op.name == operationB:
				bLevel = -count
			
			if op.name == operationA:
				aLevel = -count
			
			if aLevel and bLevel:
				return aLevel > bLevel
	
	return False

def getBPCExpressionParser():
	global globalBPCParser
	
	if globalBPCParser:
		return globalBPCParser
	
	parser = ExpressionParser()
	
	# Build the levels from the list
	for opLevel in bpOperatorLevels:
		operatorLevelObject = OperatorLevel()
		for operator in opLevel:
			operatorLevelObject.addOperator(operator)
		parser.addOperatorLevel(operatorLevelObject)
	
	# Build dictionary for the post processor
	for opLevel in parser.operatorLevels:
		for op in opLevel.operators:
			if op.type == Operator.BINARY:
				binaryOperatorTagToSymbol[op.name] = op.text
	
	binaryOperatorTagToSymbol["slice"] = "[:]"
	binaryOperatorTagToSymbol["range"] = ":"
	
	globalBPCParser = parser
	return parser
