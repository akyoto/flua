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
	"parameter",
	"value",
	"condition",
	"variable"
]

wrapperMultipleElements = [
	"code",
	"extern",
	"if-block",
	"try-block"
]

xmlToBPCBlock = {
	"operators" : "operator",
	"template" : "template",
	"set" : "set",
	"get" : "get",
	"else" : "else",
	"private" : "private"
	#"static" : "static"
}

xmlToBPCExprBlock = {
	"target" : ["target", "name", "code"],
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
	"try", "catch", "case"
]

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
	isInvalidNode = (nodeName == "if-block" or nodeName == "try-block") #or (nodeName == "import" and node.childNodes[0].nodeValue == "bp.Core")
	isInvalidNodeToCheckNewlines = (nodeName in elementsNoNewline)
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
		#print(oldLen, newLen, "|", codeLinesAdded, "-", nodeLinesAdded, "=", codeLinesAdded - nodeLinesAdded, nodeName)
		
		if nodeLinesAdded < codeLinesAdded:
			diff = codeLinesAdded - nodeLinesAdded
			for i in range(0, diff):
				conv.add(None)
	return codeAdded

def nodeToBPC(node, tabLevel = 0, conv = None):
	if node is None:
		return ""
	
	if isTextNode(node):
		text = node.nodeValue
		if text.isspace():
			return ""
		if text.startswith("bp_string_"):
			stringContent = ""
			if node.parentNode:
				node = node.parentNode
				try:
					while node.tagName != "module":
						node = node.parentNode
					
					header = getElementByTagName(node, "header")
					strings = getElementByTagName(header, "strings")
					for child in strings.childNodes:
						if isElemNode(child) and child.tagName == "string" and child.getAttribute("id") == text:
							# TODO: Handle spaces and tabs for strings!
							return '"%s"' % child.childNodes[0].nodeValue.strip()
				except:
					raise CompilerException("Can't find string value of '%s'" % (text))
			return '""'
		return text
	
	nodeName = node.tagName
	# Type declaration
	if nodeName == "declare-type":
		op1 = node.childNodes[0].childNodes[0]
		op2 = node.childNodes[1].childNodes[0]
		return nodeToBPC(op1) + " : " + nodeToBPC(op2)
	# Call
	elif nodeName == "call":
		funcName = getCalledFuncName(node)
		parameters = nodeToBPC(getElementByTagName(node, "parameters"))
		
		if node.parentNode.tagName == "code":
			return "%s %s" % (funcName, parameters)
		else:
			return "%s(%s)" % (funcName, parameters)
	# Parameters
	elif nodeName == "parameters" or nodeName == "values":
		params = []
		for param in node.childNodes:
			paramCode = nodeToBPC(param)
			if len(paramCode) >= 1 and paramCode[0] == '(' and paramCode[-1] == ')':
				paramCode = paramCode[1:-1]
			params.append(paramCode)
		return ", ".join(params)
	# Code in general
	elif nodeName in wrapperMultipleElements:
		if nodeName == "extern":
			tabLevel += 1
		
		code = ""
		tabs = ""
		if nodeName == "code" or nodeName == "extern" :
			tabs = "\t" * tabLevel
		
		for child in node.childNodes:
			# Save nodes in array
			if conv:
				instruction = nodeToBPCSaved(child, tabLevel, conv)
			else:
				instruction = nodeToBPC(child, tabLevel)
			
			if instruction:
				newline = "\n"
				if len(instruction) >= 1 and instruction[0] == '(' and instruction[-1] == ')':
					instruction = instruction[1:-1]
				if child.tagName in elementsNoNewline:
					newline = ""
				
				code += tabs + instruction + newline
		
		code += "\t" * (tabLevel - 1)
		if nodeName == "extern":
			return "extern\n" + code
		#elif nodeName == "switch":
		#	switchExpr = nodeToBPC(getElementByTagName(node, "value"))
		#	return "switch %s\n%s" % (switchExpr, code)
		else:
			return code
	# Function definition
	elif nodeName == "function" or nodeName == "operator" or nodeName == "getter" or nodeName == "setter":
		name = getElementByTagName(node, "name")
		params = getElementByTagName(node, "parameters")
		code = getElementByTagName(node, "code")
		paramsCode = ""
		if params:
			paramsCode = nodeToBPC(params)
			if paramsCode:
				paramsCode = " " + paramsCode
		return nodeToBPC(name) + paramsCode + "\n" + nodeToBPC(code, tabLevel + 1, conv)
	elif nodeName == "negative":
		return "-(" + nodeToBPC(node.childNodes[0]) + ")"
	elif nodeName == "unmanaged":
		return "~" + nodeToBPC(node.childNodes[0])
	elif nodeName == "new":
		return "new %s(%s)" % (nodeToBPC(getElementByTagName(node, "type")), nodeToBPC(getElementByTagName(node, "parameters")))
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
			if isElemNode(child) and child.tagName == "import":
				deps += nodeToBPCSaved(child, 0, conv)
					
		if deps:
			return deps + "\n"
		else:
			return ""
	elif nodeName == "import":
		importMod = node.childNodes[0].nodeValue.strip()
		
		# Imported by default
		if importMod == "bp.Core":
			return ""
		
		return "import " + importMod + "\n"
	elif nodeName == "for":
		iterator = nodeToBPC(getElementByTagName(node, "iterator"))
		start = nodeToBPC(getElementByTagName(node, "from"))
		loopCode = nodeToBPC(getElementByTagName(node, "code"), tabLevel + 1, conv)
		
		toUntil = ""
		toNode = getElementByTagName(node, "to")
		untilNode = getElementByTagName(node, "until")
		if toNode:
			toUntil = "to"
			end = nodeToBPC(toNode)
		elif untilNode:
			toUntil = "until"
			end = nodeToBPC(untilNode)
		else:
			raise CompilerException("Missing <to> or <until> node")
		
		return "for %s = %s %s %s\n%s" % (iterator, start, toUntil, end, loopCode)
	elif nodeName in wrapperSingleElement:
		if node.childNodes:
			return nodeToBPC(node.childNodes[0])
		else:
			return ""
	elif nodeName == "extern-function":
		nameNode = getElementByTagName(node, "name")
		typeNode = getElementByTagName(node, "type")
		typeName = ""
		
		if typeNode:
			typeName = nodeToBPC(typeNode)
			typeName = " : " + typeName
		
		return nodeToBPC(nameNode) + typeName
	elif nodeName == "class":
		nameNode = getElementByTagName(node, "name")
		codeNode = getElementByTagName(node, "code")
		return nodeToBPC(nameNode) + "\n" + nodeToBPC(codeNode, tabLevel + 1)
	elif nodeName == "noop":
		return "..."
	elif nodeName in xmlToBPCSingleLineExpr:
		keyword = xmlToBPCSingleLineExpr[nodeName]
		
		if node.childNodes:
			return "%s %s" % (keyword, nodeToBPC(node.childNodes[0]))
		else:
			return keyword
	elif nodeName in xmlToBPCExprBlock:
		exprBlock = xmlToBPCExprBlock[nodeName]
		exprNode = getElementByTagName(node, exprBlock[1])
		expr = ""
		space = ""
		if exprNode:
			expr = nodeToBPC(exprNode)
		name = exprBlock[0]
		if name and expr:
			space = " "
		
		if nodeName != "switch":
			code = nodeToBPC(getElementByTagName(node, exprBlock[2]), tabLevel + 1, conv)
		else:
			code = "\t" * (tabLevel + 1)
			childNodeName = exprBlock[2]
			for child in node.childNodes:
				if isElemNode(child) and child.tagName == childNodeName:
					code += nodeToBPCSaved(child, tabLevel + 1, conv)
		return "%s%s%s\n%s" % (name, space, expr, code)
	elif nodeName in xmlToBPCBlock:
		blockCode = ""
		tabs = ""
		if nodeName != "else":
			tabs = "\t" * (tabLevel + 1)
		for child in node.childNodes:
			if isElemNode(child):
				blockCode += tabs + nodeToBPC(child, tabLevel + 1, conv) + "\n"
		blockCode = blockCode[:-1] + "\t" * tabLevel
		return xmlToBPCBlock[nodeName] + "\n" + blockCode
	elif nodeName in binaryOperatorTagToSymbol:
		op1 = node.childNodes[0].childNodes[0]
		op2 = node.childNodes[1].childNodes[0]
		space = " "
		prefix = "("
		postfix = ")"
		if nodeName == "access":
			space = ""
			#prefix = ""
			#postfix = ""
		
		return prefix + nodeToBPC(op1) + space + binaryOperatorTagToSymbol[nodeName] + space + nodeToBPC(op2) + postfix
	
	raise CompilerException("Can't turn '%s' into pseudo code, unknown element tag" % (nodeName))

def getCalledFuncName(node):
	funcNameNode = getFuncNameNode(node)
	
	caller = ""
	if isTextNode(funcNameNode):
		funcName = funcNameNode.nodeValue
	else:
		caller = nodeToBPC(funcNameNode.childNodes[0].childNodes[0])
		funcName = funcNameNode.childNodes[1].childNodes[0].nodeValue
	
	if caller:
		funcName = caller + "." + funcName
	
	return funcName