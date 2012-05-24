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
from bp.Compiler.Output import *

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
def adjustDataTypePY(type, adjustOuterAsWell = True):
	if type in nonPointerTypes:
		return type
	else:
		return "BP" + type
