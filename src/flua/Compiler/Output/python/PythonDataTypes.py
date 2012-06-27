####################################################################
# Header
####################################################################
# Target:   Python data types
# Author:   Eduard Urbach

####################################################################
# License
####################################################################
# (C) 2012  Eduard Urbach
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
	"Bool" : "",
	"Byte" : "",
	"ConstChar" : "",
	"Short" : "",
	"Int" : "",
	"Int32" : "",
	"Int64" : "",
	"UInt32" : "",
	"UInt64" : "",
	"Size" : "",
	"Float" : "",
	"Float32" : "",
	"Float64" : "",
	"CString" : "",
	"BigInt" : "",
}

nonPointerTypes = dataTypeDefinitions

####################################################################
# Functions
####################################################################
#def adjustDataTypePY(type, adjustOuterAsWell = True):
#	if type in nonPointerTypes:
#		return type
#	else:
#		return "BP" + type.replace("<", "_").replace(">", "_").replace(", ", "__")
		
def adjustDataTypePY(type, adjustOuterAsWell = True):
	if type == "void" or type in nonPointerTypes:
		return type
	
	#classPrefix = pointerType + "<" + standardClassPrefix
	#classPostfix = ">"
	#classPrefix = "BP_PTR_DECL(" + standardClassPrefix
	#classPostfix = ")"
	classPrefix = standardClassPrefix
	classPostfix = ""
	
	pos = type.find('<')
	if pos != -1:
		params = splitParams(type[pos+1:-1])
		paramsNew = []
		for param in params:
			paramsNew.append(adjustDataTypePY(param))
		type = type[:pos] + "_" + "__".join(paramsNew) + "_"
	
	className = extractClassName(type)
	
	#if className == "MemPointer":
	#	if paramsNew:
	#		return paramsNew[0] + "*"
	#	else:
	#		raise CompilerException("You forgot to specify the data type of your MemPointer")
	
	if 1:#not isUnmanaged(type):
		if adjustOuterAsWell:
			type = classPrefix + type + classPostfix
		else:
			type = standardClassPrefix + type
	else:
		type = standardClassPrefix + removeUnmanaged(type)
	
	return type.replace("<", "_").replace(">", "_").replace(",  ", ",").replace(",", "__")
