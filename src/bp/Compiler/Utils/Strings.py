####################################################################
# Header
####################################################################
# String functions

####################################################################
# License
####################################################################
# This file is part of Blitzprog.

# Blitzprog is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Blitzprog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Blitzprog.  If not, see <http://www.gnu.org/licenses/>.

####################################################################
# Imports
####################################################################
import os

####################################################################
# Functions
####################################################################

def fixPath(stri):
	newPath = stri.replace("\\", "/")
	if newPath.endswith("/"):
		return newPath
	else:
		return newPath + "/"

def fixID(stri):
	return stri.replace(".", "_").replace(" ", "__")

def isVarChar(char):
	return char.isalnum() or char == '_'

def countTabs(line):
	tabCount = 0
	lineLen = len(line)
	while tabCount < lineLen and line[tabCount] == '\t':
		tabCount += 1
	
	return tabCount

def isBPStringIdentifier(stri):
	return stri.startswith("bp_string_")

def isNumeric(stri):
	parts = stri.split(".")
	numParts = len(parts)
	if numParts == 2:
		return parts[0].isdigit() and parts[1].isdigit()
	elif numParts == 1:
		return stri.isdigit()
	else:
		return False

def startsWith(stri, prefix):
	stri = stri.lower()
	prefix = prefix.lower()
	return stri.startswith(prefix) and (len(prefix) == len(stri) or stri[len(prefix)].isspace())

def stripExt(stri):
	pos = stri.rfind(".")
	if pos != -1:
		return stri[:pos]
	return stri

def stripAll(path):
	return stripExt(os.path.basename(path))
	
def stripDir(path):
	return os.path.basename(path)

def extractDir(path):
	newPath = os.path.dirname(path)
	if newPath.endswith("/"):
		return newPath
	else:
		return newPath + "/"

def getNextWhitespacePos(stri, fromIndex):
	striLen = len(stri)
	while fromIndex < striLen and not stri[fromIndex].isspace():
		fromIndex += 1
	if fromIndex == striLen:
		return -1
	return fromIndex

def getNextNonWhitespacePos(stri, fromIndex):
	striLen = len(stri)
	while fromIndex < striLen and stri[fromIndex].isspace():
		fromIndex += 1
	if fromIndex == striLen:
		return -1
	return fromIndex

def capitalize(stri):
	return stri[0].upper() + stri[1:]

def extractClassName(name):
	return removeUnmanaged(removeGenerics(name))

def extractTemplateValues(name):
	pos = name.find('<')
	if pos == -1:
		return ""
	return name[pos + 1:-1]

def removeGenerics(typeName):
	pos = typeName.find('<')
	if pos != -1:
		return typeName[:pos]
	return typeName

def removeUnmanaged(type):
	return type.replace("~", "")

def splitParams(line):
	params = []
	bracketCounter = 0
	lastStart = 0
	
	for i in range(len(line)):
		c = line[i]
		if c == '<':
			bracketCounter += 1
		elif c == '>':
			bracketCounter -= 1
		elif c == ',' and bracketCounter == 0:
			param = line[lastStart:i]
			lastStart = i + 1
			params.append(param.strip())
	
	lastParam = line[lastStart:].strip()
	if lastParam:
		params.append(lastParam)
	return params

def buildPostfix(paramTypes):
	postfix = ""
	for dataType in paramTypes:
		postfix += "__" + dataType.replace("<", "_").replace(">", "_").replace("~", "_").replace(",", "_").replace(" ", "")
	return postfix

# These functions do NOT rely on each other
def isNotOperatorSign(char):
	return char.isalnum() or char.isspace() or char in "_(){}"

def isDefinitelyOperatorSign(char):
	return char in '+-*/=%&|:!\\~'

def mustNotBeNextToExpr(char):
	return char.isalnum() or char == '_'
