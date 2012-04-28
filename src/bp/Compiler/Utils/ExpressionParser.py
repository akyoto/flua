from bp.Compiler.ExpressionParser import *

globalBPCParser = None

def getBPCExpressionParser():
	global globalBPCParser
	
	if globalBPCParser:
		return globalBPCParser
	
	parser = ExpressionParser()
	
	# See http://www.cppreference.com/wiki/operator_precedence
	
	# 1: Function calls
	operators = OperatorLevel()
	operators.addOperator(Operator("(", "call.unused", Operator.BINARY))
	operators.addOperator(Operator("§", "template-call", Operator.BINARY))
	parser.addOperatorLevel(operators)
	
	# 2: Access
	operators = OperatorLevel()
	operators.addOperator(Operator(".", "access", Operator.BINARY))
	operators.addOperator(Operator("[", "index.unused", Operator.BINARY))
	operators.addOperator(Operator("#", "call", Operator.BINARY))
	operators.addOperator(Operator("@", "index", Operator.BINARY))
	parser.addOperatorLevel(operators)
	
	# Loose pointer
	operators = OperatorLevel()
	operators.addOperator(Operator("~", "unmanaged", Operator.UNARY))
	parser.addOperatorLevel(operators)
	
	# Type declaration
	operators = OperatorLevel()
	operators.addOperator(Operator(":", "declare-type", Operator.BINARY))
	parser.addOperatorLevel(operators)
	
	# 3: Unary
	operators = OperatorLevel()
	operators.addOperator(Operator("!", "not", Operator.UNARY))
	operators.addOperator(Operator("-", "negative", Operator.UNARY))
	parser.addOperatorLevel(operators)
	
	# 5: Mul, Div
	operators = OperatorLevel()
	operators.addOperator(Operator("*", "multiply", Operator.BINARY))
	operators.addOperator(Operator("/", "divide", Operator.BINARY))
	operators.addOperator(Operator("\\", "divide-floor", Operator.BINARY))
	operators.addOperator(Operator("%", "modulo", Operator.BINARY))
	parser.addOperatorLevel(operators)
	
	# 6: Add, Sub
	operators = OperatorLevel()
	operators.addOperator(Operator("+", "add", Operator.BINARY))
	operators.addOperator(Operator("-", "subtract", Operator.BINARY))
	parser.addOperatorLevel(operators)
	
	# 7: Shift operations
	operators = OperatorLevel()
	operators.addOperator(Operator("<<", "shift-left", Operator.BINARY))
	operators.addOperator(Operator(">>", "shift-right", Operator.BINARY))
	parser.addOperatorLevel(operators)
	
	# 8: GT, LT
	operators = OperatorLevel()
	operators.addOperator(Operator(">=", "greater-or-equal", Operator.BINARY))
	operators.addOperator(Operator(">", "greater", Operator.BINARY))
	operators.addOperator(Operator("<=", "less-or-equal", Operator.BINARY))
	operators.addOperator(Operator("<", "less", Operator.BINARY))
	parser.addOperatorLevel(operators)
	
	# 9: Comparison
	operators = OperatorLevel()
	operators.addOperator(Operator("==", "equal", Operator.BINARY))
	operators.addOperator(Operator("!=", "not-equal", Operator.BINARY))
	operators.addOperator(Operator("~=", "almost-equal", Operator.BINARY))
	parser.addOperatorLevel(operators)
	
	# 13: Logical AND
	operators = OperatorLevel()
	operators.addOperator(Operator("&&", "and", Operator.BINARY))
	parser.addOperatorLevel(operators)
	
	# 14: Logical OR
	operators = OperatorLevel()
	operators.addOperator(Operator("||", "or", Operator.BINARY))
	parser.addOperatorLevel(operators)
	
	# 15: Ternary operator
	#	operators = OperatorLevel()
	#	operators.addOperator(Operator(":", "ternary-code", Operator.BINARY))
	#	parser.addOperatorLevel(operators)
	#	
	#	operators = OperatorLevel()
	#	operators.addOperator(Operator("?", "ternary-condition", Operator.BINARY))
	#	parser.addOperatorLevel(operators)
	
	# 16: Assign
	operators = OperatorLevel()
	operators.addOperator(Operator("+=", "assign-add", Operator.BINARY))
	operators.addOperator(Operator("-=", "assign-subtract", Operator.BINARY))
	operators.addOperator(Operator("*=", "assign-multiply", Operator.BINARY))
	operators.addOperator(Operator("/=", "assign-divide", Operator.BINARY))
	operators.addOperator(Operator("<<=", "assign-shift-left", Operator.BINARY))
	operators.addOperator(Operator(">>=", "assign-shift-right", Operator.BINARY))
	#operators.addOperator(Operator("}=", "assign-each-in", Operator.BINARY))
	operators.addOperator(Operator("=", "assign", Operator.BINARY))
	operators.addOperator(Operator("-->", "flow-delayed-to", Operator.BINARY))
	operators.addOperator(Operator("<--", "flow-delayed-from", Operator.BINARY))
	operators.addOperator(Operator("->", "flow-to", Operator.BINARY))
	operators.addOperator(Operator("<-", "flow-from", Operator.BINARY))
	parser.addOperatorLevel(operators)
	
	# Comma
	operators = OperatorLevel()
	operators.addOperator(Operator(",", "separate", Operator.BINARY))
	parser.addOperatorLevel(operators)
	
	# Build dictionary for the post processor
	for opLevel in parser.operatorLevels:
		for op in opLevel.operators:
			if op.type == Operator.BINARY:
				binaryOperatorTagToSymbol[op.name] = op.text
	
	globalBPCParser = parser
	return parser