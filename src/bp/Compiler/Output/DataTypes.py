####################################################################
# Imports
####################################################################
from bp.Compiler.Utils import *

####################################################################
# Global
####################################################################
standardClassPrefix = "BP"

dataTypeWeights = {
	"void" : 0,	# Added because of recursive functions
	"Bool" : 1,
	"Byte" : 2,
	"ConstChar" : 3,
	"Short" : 4,
	"Int" : 5,
	"Int32" : 6,
	"UInt32" : 6,
	"Int64" : 7,
	"UInt64" : 7,
	"Size" : 8,
	"BigInt" : 9,
	"Float" : 10,
	"Float32" : 11,
	"Float64" : 12,
	"CString" : 13,
}

nonPointerClasses = dataTypeWeights

####################################################################
# Functions
####################################################################
def canBeCastedTo(fromType, toType):
	# TODO: Implement this fully...
	if fromType in nonPointerClasses and toType in nonPointerClasses:
		return True
	elif fromType == toType:
		return True
	elif "~" + fromType == toType:
		return True
	else:
		return False

def removeUnmanaged(type):
	return type.replace("~", "")

def isUnmanaged(type):
	return type.startswith("~")

def replaceActorGenerics(type, actorPrefix):
	while 1:
		posActor = type.find('Actor<')
		if posActor != -1:
			type = actorPrefix + type[posActor + len('Actor<'):-1]
		else:
			break
	return type

def getHeavierOperator(operatorType1, operatorType2):
	if operatorType1 is None:
		return operatorType2
	if operatorType2 is None:
		return operatorType1
	
	weight1 = dataTypeWeights[operatorType1]
	weight2 = dataTypeWeights[operatorType2]
	
	if weight1 >= weight2:
		return operatorType1
	else:
		return operatorType2

def correctOperators(sign):
	if sign == "[]" or sign == "index":
		return "operatorIndex"
	elif sign == "[:]" or sign == "slice":
		return "operatorSlice"
	elif sign == "+" or sign == "add":
		return "operatorAdd"
	elif sign == "-" or sign == "subtract":
		return "operatorSubtract"
	elif sign == "*" or sign == "multiply":
		return "operatorMultiply"
	elif sign == "/" or sign == "divide":
		return "operatorDivide"
	elif sign == "=" or sign == "assign":
		return "operatorAssign"
	elif sign == "==" or sign == "equal":
		return "operatorEqual"
	elif sign == "!=" or sign == "not-equal":
		return "operatorNotEqual"
	
	return sign