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
# This file is part of Flua.
# 
# Flua is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Flua is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Flua.  If not, see <http://www.gnu.org/licenses/>.

####################################################################
# Imports
####################################################################
from flua.Compiler.Utils import *
from flua.Compiler.Output import *

####################################################################
# Globals
####################################################################
dataTypeDefinitions = {
	"Bool" : "bool",
	"Byte" : "char",
	"ConstChar" : "const char",
	"Int16" : "short",
	"UInt16" : "unsigned short",
	"Int" : "int_fast32_t",
	"Int32" : "int32_t",
	"Int64" : "int64_t",
	"UInt" : "uint32_t",
	"UInt32" : "uint32_t",
	"UInt64" : "uint64_t",
	"Size" : "size_t",
	"Float" : "float",
	"Float32" : "float",
	"Float64" : "double",
	"CString" : "char*",
	"BigInt" : "mpz_class",
	"DataType" : "int",
}

####################################################################
# Functions
####################################################################
def adjustDataTypeCPP(type, adjustOuterAsWell = True):
	if type == "void" or type in nonPointerClasses:
		return type
	
	#classPrefix = pointerType + "<" + standardClassPrefix
	#classPostfix = ">"
	#classPrefix = "BP_PTR_DECL(" + standardClassPrefix
	#classPostfix = ")"
	
	#classPrefix = standardClassPrefix
	classPostfix = "*"
	
	pos = type.find('<')
	
	if type[:pos] == "Tuple":
		return standardClassPrefix + type.replace("<", "_").replace(">", "_").replace(",", "_").replace(" ", "") + classPostfix
	
	if pos != -1:
		paramsNew = [adjustDataTypeCPP(param) for param in splitParams(type[pos+1:-1])]
		type = "%s<%s>" % (type[:pos], ", ".join(paramsNew))
	
	className = extractClassName(type)
	
	if className == "MemPointer":
		if paramsNew:
			return paramsNew[0] + "*"
		else:
			raise CompilerException("You forgot to specify the data type of your MemPointer")
	
	if not isUnmanaged(type):
		if adjustOuterAsWell:
			type = "%s%s%s" % (standardClassPrefix, type, classPostfix)
		else:
			type = standardClassPrefix + type
	else:
		type = standardClassPrefix + removeUnmanaged(type)
	
	return type.replace("<", "< ").replace(">", " >").replace("  ", " ")

# Old version
#===============================================================================
# def adjustDataTypeCPP2(type, adjustOuterAsWell = True, templateParamsMap = {}):
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

#print(adjustDataTypeCPP("Float"))
#print(adjustDataTypeCPP2("Float"))
#print(adjustDataTypeCPP("Point"))
#print(adjustDataTypeCPP2("Point"))
#print(adjustDataTypeCPP("Point<Int, Int>"))
#print(adjustDataTypeCPP2("Point<Int, Int>"))
#print(adjustDataTypeCPP("Circle<Point<Int, Test>, Float>"))
#print(adjustDataTypeCPP2("Circle<Point<Int, Test>, Float>"))
#print(adjustDataTypeCPP("~Point"))
#print(adjustDataTypeCPP2("~Point"))
#print(adjustDataTypeCPP("MemPointer<Int>"))
#print(adjustDataTypeCPP2("MemPointer<Int>"))
#print(adjustDataTypeCPP("~MemPointer<Int>"))
#print(adjustDataTypeCPP2("~MemPointer<Int>"))
#raise CompilerException("done")
