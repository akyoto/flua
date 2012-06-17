####################################################################
# Header
####################################################################
# File:		DataType functions
# Author:   Eduard Urbach

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
	"UInt" : 6,
	"Size" : 6,
	"Int32" : 7,
	"UInt32" : 7,
	"Int64" : 8,
	"UInt64" : 8,
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
	if sign == "[]=" or sign == "set-index":
		return "operatorSetIndex"
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
