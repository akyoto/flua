####################################################################
# Header
####################################################################
# Target:   C++ data types
# Author:   Eduard Urbach

####################################################################
# License
####################################################################
# (C) 2011  Eduard Urbach
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
# Global
####################################################################
pointerType = "Ptr"
standardClassPrefix = "BP"

dataTypeDefinitions = {
	"Bool" : "bool",
	"Byte" : "char",
	"ConstChar" : "const char",
	"Short" : "short",
	"Int" : "int_fast32_t",
	"Int32" : "int32_t",
	"Int64" : "int64_t",
	"UInt32" : "uint32_t",
	"UInt64" : "uint64_t",
	"Size" : "size_t",
	"Float" : "float",
	"Float32" : "float",
	"Float64" : "double",
	"CString" : "Byte *",
	"BigInt" : "mpz_class",
}

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

def adjustDataType(type, adjustOuterAsWell = True):
	if type == "void" or type in nonPointerClasses:
		return type
	
	#classPrefix = pointerType + "<" + standardClassPrefix
	#classPostfix = ">"
	#classPrefix = "BP_PTR_DECL(" + standardClassPrefix
	#classPostfix = ")"
	classPrefix = standardClassPrefix
	classPostfix = "*"
	
	pos = type.find('<')
	if pos != -1:
		params = splitParams(type[pos+1:-1])
		paramsNew = []
		for param in params:
			paramsNew.append(adjustDataType(param))
		type = type[:pos] + "<" + ", ".join(paramsNew) + ">"
	
	className = extractClassName(type)
	
	if className == "MemPointer":
		return paramsNew[0] + "*"
	
	if not isUnmanaged(type):
		if adjustOuterAsWell:
			type = classPrefix + type + classPostfix
		else:
			type = standardClassPrefix + type
	else:
		type = standardClassPrefix + removeUnmanaged(type)
	return type.replace("<", "< ").replace(">", " >").replace("  ", " ")

# Old version
#===============================================================================
# def adjustDataType2(type, adjustOuterAsWell = True, templateParamsMap = {}):
#	if type == "void" or type in nonPointerClasses:
#		return type
#	
#	if type in templateParamsMap:
#		return templateParamsMap[type]
#	
#	# Adjust template params
#	pos = type.find('<')
#	postFixCount = 0
#	typeName = ""
#	className = ""
#	standardClassPrefix = "BP"
#	actorPrefix = "ActorWrapper"
#	
#	classPrefix = pointerType + "<" + standardClassPrefix
#	classPostfix = ">"
#	
#	# Actors
#	type = replaceActorGenerics(type, actorPrefix)
#	
#	if adjustOuterAsWell:
#		if pos != -1:
#			className = type[:pos]
#		else:
#			className = type
#		
#		classNameClean = removeUnmanaged(className)
#		if (not classNameClean in nonPointerClasses): #and (not classNameClean in templateParams):
#			# Unmanaged
#			if className.startswith("~"):
#				if classNameClean == "MemPointer":
#					innerType = type[pos+1:-1]
#					innerClass = extractClassName(innerType)
#					#debugStop()
#					if innerClass in nonPointerClasses: #or innerClass in templateParams:
#						type = innerType + "*"
#						postFixCount += 1
#						pos = 0
#					else:
#						type = classPrefix + innerType + classPostfix + "*"
#						postFixCount += len(classPostfix) + 1
#						pos += len(classPrefix)
#				else:
#					type = standardClassPrefix + type[1:]
#			else:
#				pos += len(classPrefix)
#				postFixCount += len(classPostfix)
#				type = classPrefix + type + classPostfix
#	else:
#		type = standardClassPrefix + type
#	
#	while 1:
#		pos = type.find('<', pos)
#		if pos == -1:
#			break
#		postFixCount += 1
#		typeNames = type[pos+1:-postFixCount]
#		
#		# TODO: This contains a bug...remove it! T< Point<A, B>, C >
#		# TODO: This splitting absolutely does not work...replace it!
#		for typeName in splitParams(typeNames):
#			typeName = typeName.strip()
#			className = extractClassName(typeName)
#			
#			if className in nonPointerClasses: #or className in templateParams:
#				pos += 1
#			else:
#				type = type[:pos+1] + classPrefix + type[pos+1:-postFixCount] + classPostfix + type[-postFixCount:]
#				
#				# Because of the postfix pointer sign
#				postFixCount += 1
#				
#				# Because of the prefixes
#				pos += len(classPrefix) + len(classPostfix) + 1
#	
#	return type.replace("<", "< ").replace(">", " >")
#===============================================================================

#print(adjustDataType("Float"))
#print(adjustDataType2("Float"))
#print(adjustDataType("Point"))
#print(adjustDataType2("Point"))
#print(adjustDataType("Point<Int, Int>"))
#print(adjustDataType2("Point<Int, Int>"))
#print(adjustDataType("Circle<Point<Int, Test>, Float>"))
#print(adjustDataType2("Circle<Point<Int, Test>, Float>"))
#print(adjustDataType("~Point"))
#print(adjustDataType2("~Point"))
#print(adjustDataType("MemPointer<Int>"))
#print(adjustDataType2("MemPointer<Int>"))
#print(adjustDataType("~MemPointer<Int>"))
#print(adjustDataType2("~MemPointer<Int>"))
#raise CompilerException("done")
