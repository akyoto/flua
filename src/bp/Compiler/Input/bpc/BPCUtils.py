####################################################################
# Header
####################################################################
# Syntax:   Blitzprog Code
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
from bp.Compiler.Input.bpc import *

####################################################################
# Variables
####################################################################
# Used by XML -> BPC compiler

# Elements that simply wrap value nodes
wrapperSingleElement = [
	"name",
	"iterator",
	"from",
	"to",
	"until",
	"type",
	"value",
	"condition",
	"variable",
]

wrapperMultipleElements = {
	"code" : "",
	
	"if-block" : "",
	"try-block" : "",
	
	"operators" : "operator",
	"set" : "set",
	"get" : "get",
	"casts" : "to",
}

xmlToBPCBlock = {
	"template" : "template",
	"else" : "else",
	"private" : "private",
	"extern" : "extern",
	#"static" : "static"
	
	# TODO: Metadata
	"require" : "require",
	"ensure" : "ensure",
	"maybe" : "maybe",
	"test" : "test"
}

xmlToBPCExprBlock = {
	"target" : ["target", "name", "code"],
	"namespace" : ["namespace", "name", "code"],
	"if" : ["if", "condition", "code"],
	"else-if" : ["elif", "condition", "code"],
	"try" : ["try", "", "code"],
	"case" : ["", "values", "code"],
	"while" : ["while", "condition", "code"],
	"catch" : ["catch", "variable", "code"],
	"switch" : ["switch", "value", "case"]
}

xmlToBPCSingleLineExpr = {
	"return" : "return",
	"include" : "include",
	"const" : "const",
	"break" : "break",
	"continue" : "continue",
	"throw" : "throw"
}

elementsNoNewline = [
	"if", "else-if", "else",
	"try", "catch", "case", "import"
]

#functionNodeNames = {
#	"function",
#	"operator",
#	"setter",
#	"getter",
#	"cast-definition"
#}

functionNodeTagNames = {
	"function",
	"getter",
	"setter",
	"cast-definition",
	"operator",
}

autoNewlineBlock = {
	"while",
	"if-block",
	"try-block",
	"for",
	"extern",
	"target",
	"switch",
	"ensure",
	"require",
	"test",
	"maybe",
	"class",
	"template",
	"get",
	"set",
	"operators",
	"casts",
	
	"function",
	"getter",
	"setter",
	"cast-definition",
	"operator",
}

####################################################################
# Classes
####################################################################
class LineToNodeConverter:
	
	def __init__(self):
		self.lineToNode = []
		
	def add(self, node):
		self.lineToNode.append(node)
		
	def removeLast(self):
		if self.lineToNode:
			self.lineToNode.pop()
		
	def getNode(self, index):
		return self.lineToNode[index]

####################################################################
# Functions
####################################################################
def nodeToBPCSaved(node, tabLevel, conv):
	nodeName = node.tagName
	
	# First step
	isInvalidNode = False
	isInvalidNodeToCheckNewlines = False
	if (nodeName == "if-block" or nodeName == "try-block"):
		isInvalidNode = True
	if (nodeName in elementsNoNewline):
		isInvalidNodeToCheckNewlines = True
	
	if conv:
		oldLen = len(conv.lineToNode)
		if not isInvalidNode:
			conv.add(node)
	
	# Second step
	codeAdded = nodeToBPC(node, tabLevel, conv)
	
	# e.g. import bp.Core
	if not codeAdded:
		conv.removeLast()
		return codeAdded
	
	if conv and not isInvalidNodeToCheckNewlines:
		newLen = len(conv.lineToNode)
		codeLinesAdded = len(codeAdded.split("\n"))#codeAdded.count("\n") + 1
		nodeLinesAdded = newLen - oldLen
		#print(oldLen, newLen, "|", codeLinesAdded, "-", nodeLinesAdded, "=", codeLinesAdded - nodeLinesAdded, nodeName, isInvalidNode, isInvalidNodeToCheckNewlines, codeAdded)
		
		if nodeLinesAdded < codeLinesAdded:
			diff = codeLinesAdded - nodeLinesAdded
			for i in range(0, diff):
				conv.add(None)
	#else:
	#	print("isInvalidNodeToCheckNewlines")
	
	return codeAdded

def nodeToBPC(node, tabLevel = 0, conv = None):
	if node is None:
		return ""
	
	if isTextNode(node):
		text = node.nodeValue
		if text.isspace():
			return ""
		elif text.startswith("bp_string_"):
			stringContent = ""
			if node.parentNode:
				node = node.parentNode
				try:
					while node.tagName != "module":
						node = node.parentNode
					
					header = getElementByTagName(node, "header")
					strings = getElementByTagName(header, "strings")
					for child in strings.childNodes:
						if child.nodeType != Node.TEXT_NODE and child.tagName == "string" and child.getAttribute("id") == text:
							return '"%s"' % decodeCDATA(child.childNodes[0].nodeValue)#.strip()
				except:
					raise CompilerException("Can't find string value of '%s'" % (text))
			return '""'
		return text
	
	nodeName = node.tagName
	# Type declaration
	if nodeName == "declare-type":
		op1 = node.childNodes[0].childNodes[0]
		op2 = node.childNodes[1].childNodes[0]
		return nodeToBPC(op1, 0, conv) + " : " + nodeToBPC(op2, 0, conv)
	# Call
	elif nodeName == "call":
		funcName = getCalledFuncName(node)
		parameters = nodeToBPC(getElementByTagName(node, "parameters"), 0, conv)
		
		if node.parentNode.tagName == "code":
			if parameters:
				return "%s %s" % (funcName, parameters)
			else:
				return "%s()" % (funcName)
		else:
			return "%s(%s)" % (funcName, parameters)
	# Parameters
	elif nodeName == "parameters" or nodeName == "values":
		params = []
		for param in node.childNodes:
			paramCode = nodeToBPC(param, 0, conv)
			if len(paramCode) >= 1 and paramCode[0] == '(' and paramCode[-1] == ')':
				paramCode = paramCode[1:-1]
			params.append(paramCode)
		return ", ".join(params)
	#######################################################################
	# Code in general
	#######################################################################
	elif nodeName in wrapperMultipleElements:# or nodeName == "get" or nodeName == "set" or nodeName == "operators" or nodeName == "casts":
		codeParts = []
		
		isVisibleBlock = (nodeName != "code" and nodeName != "if-block" and nodeName != "try-block")
		
		if isVisibleBlock:
			tabLevel += 1
		
		tabs = "\t" * tabLevel
		prefix = ""
		previousLineType = 0
		currentLineType = 1
		
		for child in node.childNodes:
			if conv is not None:
				childCode = nodeToBPCSaved(child, tabLevel, conv)
			else:
				childCode = nodeToBPC(child, tabLevel, conv)
			
			# Child name
			childName = child.tagName
			
			# Line type
			if childName in autoNewlineBlock:
				if childName in {"require", "ensure", "maybe", "test"}:
					currentLineType = 3
				else:
					currentLineType = 2
			elif childName == "comment":
				currentLineType = 0
			else:
				currentLineType = 1
			
			# Process line type
			prefix = ""
			if previousLineType:
				if (currentLineType + previousLineType >= 3 or (currentLineType == 0 and previousLineType > 0)) and currentLineType != 3:
					prefix = tabs + "\n"
			
			# Set previous line type
			previousLineType = currentLineType
			
			# Add code parts
			if childName == "if-block" or childName == "try-block":
				codeParts.append(prefix)
				codeParts.append(childCode.rstrip())
				#if childCode[-1] != "\n":
				codeParts.append("\n")
			else:
				if nodeName != "code":
					codeParts.append(prefix)
					codeParts.append(tabs)
					codeParts.append(childCode)
				else:
					codeParts.append(prefix)
					codeParts.append(tabs)
					codeParts.append(childCode)
					if childCode[-1] != "\n":
						codeParts.append("\n")
		
		if isVisibleBlock:
			return wrapperMultipleElements[nodeName] + "\n" + ''.join(codeParts)
		
		return ''.join(codeParts)
	# Function definition
	elif nodeName == "function" or nodeName == "operator" or nodeName == "getter" or nodeName == "setter" or nodeName == "cast-definition":
		if nodeName == "cast-definition":
			name = getElementByTagName(node, "to")
		else:
			name = getElementByTagName(node, "name")
		params = getElementByTagName(node, "parameters")
		code = getElementByTagName(node, "code")
		paramsCode = ""
		if params:
			paramsCode = nodeToBPC(params, 0, conv)
			if paramsCode:
				paramsCode = " " + paramsCode
		return nodeToBPC(name, 0, conv) + paramsCode + "\n" + nodeToBPC(code, tabLevel + 1, conv)
	elif nodeName == "comment":
		return "#" + decodeCDATA(node.childNodes[0].nodeValue)
	elif nodeName == "negative":
		return "-(" + nodeToBPC(node.childNodes[0], 0, conv) + ")"
	elif nodeName == "unmanaged":
		return "~" + nodeToBPC(node.childNodes[0], 0, conv)
	elif nodeName == "new":
		return "%s(%s)" % (nodeToBPC(getElementByTagName(node, "type"), 0, conv), nodeToBPC(getElementByTagName(node, "parameters"), 0, conv))
	elif nodeName == "module":
		header = getElementByTagName(node, "header")
		code = getElementByTagName(node, "code")
		return nodeToBPC(header, 0, conv) + nodeToBPC(code, 0, conv)
	elif nodeName == "header":
		depNode = getElementByTagName(node, "dependencies")
		return nodeToBPC(depNode, 0, conv)
	elif nodeName == "dependencies":
		deps = ""
		for child in node.childNodes:
			if child.nodeType != Node.TEXT_NODE and child.tagName == "import":
				importCode = nodeToBPCSaved(child, 0, conv)
				if importCode:
					deps += importCode + "\n"
					
		if deps:
			if conv:
				conv.add(None)
			return deps + "\n"
		else:
			return ""
	elif nodeName == "import":
		importMod = node.childNodes[0].nodeValue.strip()
		
		# Imported by default
		if importMod == "bp.Core":
			return ""
		
		return "import " + importMod
	elif nodeName == "for":
		iterator = nodeToBPC(getElementByTagName(node, "iterator"), 0, conv)
		start = nodeToBPC(getElementByTagName(node, "from"), 0, conv)
		loopCode = nodeToBPC(getElementByTagName(node, "code"), tabLevel + 1, conv)
		
		toUntil = ""
		toNode = getElementByTagName(node, "to")
		untilNode = getElementByTagName(node, "until")
		if toNode:
			toUntil = "to"
			end = nodeToBPC(toNode, 0, conv)
		elif untilNode:
			toUntil = "until"
			end = nodeToBPC(untilNode, 0, conv)
		else:
			raise CompilerException("Missing <to> or <until> node")
		
		return "for %s = %s %s %s\n%s" % (iterator, start, toUntil, end, loopCode)
	elif nodeName == "parameter":
		if node.childNodes:
			if len(node.childNodes) == 1:
				return nodeToBPC(node.childNodes[0], 0, conv)
			else:
				# Default value
				nameNode = getElementByTagName(node, "name")
				valueNode = getElementByTagName(node, "default-value")
				return nodeToBPC(nameNode.childNodes[0], 0, conv) + " = " + nodeToBPC(valueNode.childNodes[0], 0, conv)
		else:
			return ""
	# Wraps a single element
	elif nodeName in wrapperSingleElement:
		if node.childNodes:
			return nodeToBPC(node.childNodes[0], 0, conv)
		else:
			return ""
	elif nodeName == "extern-function":
		nameNode = getElementByTagName(node, "name")
		typeNode = getElementByTagName(node, "type")
		typeName = ""
		
		if typeNode:
			typeName = nodeToBPC(typeNode, 0, conv)
			typeName = " : " + typeName
		
		return nodeToBPC(nameNode, 0, conv) + typeName
	elif nodeName == "class":
		nameNode = getElementByTagName(node, "name")
		codeNode = getElementByTagName(node, "code")
		return nodeToBPC(nameNode, 0, conv) + "\n" + nodeToBPC(codeNode, tabLevel + 1 ,conv).rstrip() + "\n"
	elif nodeName == "noop":
		return "..."
	# Single line
	elif nodeName in xmlToBPCSingleLineExpr:
		keyword = xmlToBPCSingleLineExpr[nodeName]
		
		if node.childNodes:
			return "%s %s" % (keyword, nodeToBPC(node.childNodes[0], 0, conv))
		else:
			return keyword
	# Blocks with an expression at the beginning
	elif nodeName in xmlToBPCExprBlock:
		exprBlock = xmlToBPCExprBlock[nodeName]
		exprNode = getElementByTagName(node, exprBlock[1])
		expr = ""
		space = ""
		if exprNode:
			expr = nodeToBPC(exprNode, 0, conv)
		name = exprBlock[0]
		if name and expr:
			space = " "
		
		if nodeName != "switch":
			code = nodeToBPC(getElementByTagName(node, exprBlock[2]), tabLevel + 1, conv)
		else:
			tabs = "\t" * (tabLevel + 1)
			code = ""
			childNodeName = exprBlock[2]
			for child in node.childNodes:
				if child.nodeType != Node.TEXT_NODE and child.tagName == childNodeName:
					code += tabs + nodeToBPCSaved(child, tabLevel + 1, conv)
		return "%s%s%s\n%s" % (name, space, expr, code)
	# Blocks
	elif nodeName in xmlToBPCBlock:
		blockCode = ""
		tabs = ""
		if nodeName != "else":
			tabs = "\t" * (tabLevel + 1)
		for child in node.childNodes:
			if child.nodeType != Node.TEXT_NODE:
				blockCode += tabs + nodeToBPC(child, tabLevel + 1, conv) + "\n"
		#if blockCode[-2].isspace():
		#	blockCode = blockCode.rstrip() + "\n"
		#else:
		#blockCode = blockCode + "\t" * tabLevel
		return xmlToBPCBlock[nodeName] + "\n" + blockCode.rstrip()# + "\n" + ("\t" * (tabLevel)) + "#Here"
	elif nodeName == "not":
		return "not " + nodeToBPC(node.firstChild, 0, conv)
	# Binary operations
	elif nodeName in binaryOperatorTagToSymbol:
		op1 = node.childNodes[0].childNodes[0]
		op2 = node.childNodes[1].childNodes[0]
		space = " "
		prefix = ""
		postfix = ""
		
		if nodeName == "template-call":
			return nodeToBPC(op1, 0, conv) + "<" + nodeToBPC(op2, 0, conv) + ">"
		elif nodeName == "index":
			return nodeToBPC(op1, 0, conv) + "[" + nodeToBPC(op2, 0, conv) + "]"
		
		# Find operation "above" the current one
		if node.parentNode.tagName == "value":
			operationAbove = node.parentNode.parentNode.tagName
		else:
			operationAbove = node.parentNode.tagName
		
		if nodeName == "access":
			space = ""
			prefix = ""
			postfix = ""
		# Does it have higher or equal priority compared to the current one? If so, use brackets
		elif hasHigherOrEqualPriority(operationAbove, nodeName):
			prefix = "("
			postfix = ")"
		
		opSymbol = binaryOperatorTagToSymbol[nodeName]
		if opSymbol in translateLogicalOperatorSign:
			opSymbol = translateLogicalOperatorSign[opSymbol]
		
		return prefix + nodeToBPC(op1, 0, conv) + space + opSymbol + space + nodeToBPC(op2, 0, conv) + postfix
	
	raise CompilerException("Can't turn '%s' into pseudo code, unknown element tag" % (nodeName))

def getCalledFuncName(node):
	funcNameNode = getFuncNameNode(node)
	
	caller = ""
	if funcNameNode.nodeType == Node.TEXT_NODE:
		funcName = funcNameNode.nodeValue
	else:
		caller = nodeToBPC(funcNameNode.childNodes[0].childNodes[0])
		funcName = funcNameNode.childNodes[1].childNodes[0].nodeValue
	
	if caller:
		funcName = caller + "." + funcName
	
	return funcName
