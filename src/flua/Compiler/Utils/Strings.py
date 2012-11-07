####################################################################
# Header
####################################################################
# String functions

####################################################################
# License
####################################################################
# This file is part of Flua.

# Flua is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Flua is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Flua.  If not, see <http://www.gnu.org/licenses/>.

####################################################################
# Imports
####################################################################
import os

####################################################################
# Functions
####################################################################

#if os.name == "nt":
#        OS_SLASH = "\\"
#        OS_WRONG_SLASH = "/"
#else:
OS_SLASH = "/"
OS_WRONG_SLASH = "\\"

def fixPath(stri):
	newPath = stri.replace(OS_WRONG_SLASH, OS_SLASH)
	if os.path.isdir(newPath) and not newPath.endswith(OS_SLASH):
		return newPath + OS_SLASH
	
	return newPath
	
def fixPathNoEndSlash(stri):
	return stri.replace(OS_WRONG_SLASH, OS_SLASH)

def fixID(stri):
	return stri.replace(".", "_").replace(" ", "__")

def isVarChar(char):
	return char.isalnum() or char == '_'
	
def isVarName(name):
	for x in name:
		if not isVarChar(x):
			return False
	
	return True

def countTabs(line):
	tabCount = 0
	lineLen = len(line)
	while tabCount < lineLen and line[tabCount] == '\t':
		tabCount += 1
	
	return tabCount

def isBPStringIdentifier(stri):
	return stri.startswith("flua_string_")

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
	return fixPathNoEndSlash(stri)

def stripAll(path):
	return stripExt(os.path.basename(path))
	
def stripDir(path):
	return fixPathNoEndSlash(os.path.basename(path))

def extractDir(path):
	#if os.name == "nt":
	return fixPath(os.path.dirname(path))
	#else:
	#	return fixPath(os.path.dirname(path))
	
def extractExt(path):
	pos = path.find(".")
	
	if pos == -1:
		return ""
	
	return path[pos:]
	
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

def extractClassName(typeName):
	#return removeUnmanaged(removeGenerics(typeName))
	
	# Inlined version:
	pos = typeName.find('<')
	
	if pos != -1:
		return typeName[:pos].replace("~", "")
	
	return typeName.replace("~", "")

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

def normalizeName(name):
	return name.replace("<", "_").replace(">", "_").replace("~", "_").replace(",", "_").replace(" ", "")

def normalizeModName(name):
	return normalizeName(name.replace(" ", "_")).replace("-", "_")
	
def normalizeModPath(name):
	return normalizeModName(name).replace("/", ".")
	
def normalizeTopLevelModName(name):
	newName = ""
	for c in name.lower().replace(".", ""):
		if isVarChar(c):
			newName += c
		else:
			newName += "_"
	return newName

def buildPostfix(paramTypes):
	return "".join(["__" + normalizeName(dataType) for dataType in paramTypes])
	
	#postfix = ""
	#for dataType in paramTypes:
	#	postfix += "__" + normalizeName(dataType)
	#return postfix

# These functions do NOT rely on each other
def isNotOperatorSign(char):
	return char.isalnum() or char.isspace() or char in "_(){}"

def isDefinitelyOperatorSign(char):
	return char in '+-*/=%&|:!\\~'

def mustNotBeNextToExpr(char):
	return char.isalnum() or char == '_'
	
def matchesCurrentPlatform(name):
	if os.name == "nt" and name == "Windows":
		return True
	elif os.name == "posix" and name == "Linux":
		return True
		
	return False
