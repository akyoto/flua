####################################################################
# Header
####################################################################
# Syntax:   Flua Code
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
from flua.Compiler.Config import *
from flua.Compiler.Input.bpc import *

####################################################################
# Variables
####################################################################
# Used by XML -> BPC compiler

# Syntax
SYNTAX_BPC = 0
SYNTAX_CPP = 1
SYNTAX_RUBY = 2
SYNTAX_PYTHON = 3
currentSyntax = SYNTAX_BPC

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
	"compiler-flag",
	"expression",
	"public-member",
]

xmlToBPCSingleLineExpr = {
	"return" : "return",
	"include" : "include",
	"break" : "break",
	"continue" : "continue",
	"throw" : "throw",
	"extends-class" : "",
	"implements-interface" : "",
	"yield" : "yield",
	"assert" : "assert",
}

# The contents of those nodes will be formatted 
wrapperMultipleElements = {
	"code" : "",
	
	"if-block" : "",
	"try-block" : "",
	
	"operators" : "operator",
	"iterators" : "iterator",
	"get" : "get",
	"set" : "set",
	"casts" : "to",
	
	"extern" : "extern",
}

xmlToBPCBlock = {
	"template" : "template",
	"extends" : "extends",
	"implements" : "implements",
	"else" : "else",
	"private" : "private",
	"atomic" : "atomic",
	"define" : "define",
	"const" : "const",
	"compiler-flags" : "compilerflags",
	"public" : "public",
	#"static" : "static"
	
	# TODO: Metadata
	"require" : "require",
	"ensure" : "ensure",
	#"maybe" : "maybe",
	#"test" : "test",
}

xmlToBPCExprBlock = {
	"target" : ["target", "name", "code"],
	"namespace" : ["namespace", "name", "code"],
	"if" : ["if", "condition", "code"],
	"else-if" : ["elif", "condition", "code"],
	"try" : ["try", "", "code"],
	"parallel" : ["parallel", "", "code"],
	"begin" : ["begin", "", "code"],
	"case" : ["", "values", "code"],
	"while" : ["while", "condition", "code"],
	"in" : ["in", "expression", "code"],
	"on" : ["on", "expression", "code"],
	"catch" : ["catch", "variable", "code"],
	"switch" : ["switch", "value", "case"],
	"pattern" : ["pattern", "type", ""],
	"shared" : ["shared", "", "code"],
	"test" : ["test", "", "code"],
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
	"iterator-type",
}

autoNewlineBlock = {
	"while",
	"if-block",
	"try-block",
	"for",
	"foreach",
	"parallel-for",
	"parallel-foreach",
	"extern",
	"target",
	"switch",
	"ensure",
	"require",
	"test",
	"maybe",
	"class",
	"interface",
	"template",
	"get",
	"set",
	"operators",
	"casts",
	"namespace",
	"define",
	"parallel",
	"shared",
	"in",
	"atomic",
	"compiler-flags",
	"const",
	"on",
	"return",
	"extends",
	"implements",
	
	"function",
	"getter",
	"setter",
	"cast-definition",
	"operator",
	"iterator-type",
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
# Returns whether the 2 lines have something in common
def haveSomethingInCommon(line1, line2, child1 = None, child2 = None):
	if line1.startswith("import ") and line2.startswith("import "):
		return line1.split(".")[0] == line2.split(".")[0]

def nodeToBPCSaved(node, tabLevel, conv):
	if node.nodeType != Node.TEXT_NODE:
		nodeName = node.tagName
	else:
		nodeName = ""
	#print("NToBPC: " + nodeName)
	
	# First step: Identify nodes that aren't mapped to a specific
	# line and are therefore invalid.
	isInvalidNode = False
	isInvalidNodeToCheckNewlines = False
	
	if (nodeName == "if-block" or nodeName == "try-block"):
		isInvalidNode = True
	
	if (nodeName in elementsNoNewline):
		isInvalidNodeToCheckNewlines = True
	
	if conv:
		# Save the current length of the list
		oldLen = len(conv.lineToNode)
		
		# Add the node to the list
		if not isInvalidNode:
			conv.add(node)
	
	# Second step: Get the code that has been added by that node
	codeAdded = nodeToBPC(node, tabLevel, conv)
	
	# Remove last node if it did not add any code, e.g. import flua.Core
	if conv:
		if not codeAdded:
			#print("[LineConverter] Removing previously added node because it did not add any code: „%s“" % node.toxml())
			conv.removeLast()
			return codeAdded
		
		if conv:
			# This syntax adds a newline, we need to keep track of it in the converter
			if (
					currentSyntax == SYNTAX_CPP and codeAdded.endswith("}\n")
					or
					currentSyntax == SYNTAX_RUBY and codeAdded.endswith("end\n")
				):
				conv.add(None)
		
		if not isInvalidNodeToCheckNewlines:
			newLen = len(conv.lineToNode)
			codeLinesAdded = len(codeAdded.split("\n"))#codeAdded.count("\n") + 1
			nodeLinesAdded = newLen - oldLen
			
			# Debug
			if 0:
				print(
					oldLen,
					newLen,
					"|",
					codeLinesAdded,
					"-",
					nodeLinesAdded,
					"= " + str(codeLinesAdded - nodeLinesAdded) + " newlines added,",
					"<%s>" % nodeName,
					["Valid node.", "Invalid node."][isInvalidNode],
					["Valid to check newlines.", "Invalid to check newlines."][isInvalidNodeToCheckNewlines],
					"Code: " + codeAdded
				)
			
			#if nodeLinesAdded < codeLinesAdded:
			#	diff = codeLinesAdded - nodeLinesAdded
			#	for i in range(0, diff):
			#		print("[LineConverter] Filling space with empty nodes")
			#		conv.add(None)
	#else:
	#	print("isInvalidNodeToCheckNewlines")
	
	return codeAdded

def nodeToBPC(node, tabLevel = 0, conv = None):
	#global binaryOperatorTagToSymbol
	
	if node is None:
		return ""
	
	if node.nodeType == Node.TEXT_NODE:
		text = node.nodeValue
		if text.isspace():
			return ""
		elif text == "my":
			return ["my", "this", "self", "self"][currentSyntax]
		elif text.startswith("flua_string_"):
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
							if child.getAttribute("as-byte") == "true":
								return "'%s'" % decodeCDATA(child.childNodes[0].nodeValue)
							else:
								return '"%s"' % decodeCDATA(child.childNodes[0].nodeValue)
				except:
					raise CompilerException("Can't find string value of „%s“" % (text))
			return '""'
		elif text in {"_flua_slice_start", "_flua_slice_end"}:
			return ""
		
		return text
	
	# Correct wrong usage
	if node.nodeType != Node.ELEMENT_NODE:
		return nodeToBPC(node.documentElement, 0, conv)
	
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
		
		#return "%s(%s)" % (funcName, parameters)
		#print("%s(%s)" % (funcName, parameters))
		
		if node.parentNode and node.parentNode.nodeType == Node.ELEMENT_NODE and node.parentNode.tagName == "code":
			if parameters:
				if currentSyntax == SYNTAX_BPC and funcName.find(".") == -1:
					#print(funcName)
					#print(parameters)
					return "%s %s" % (funcName, parameters)
				else:
					return "%s(%s)" % (funcName, parameters)
			else:
				return "%s()" % (funcName)
		else:
			return "%s(%s)" % (funcName, parameters)
	# Parameters
	elif nodeName in {"parameters", "values", "default-get", "default-set"}:
		params = []
		for param in node.childNodes:
			paramCode = nodeToBPC(param, 0, conv)
			#if len(paramCode) >= 1 and paramCode[0] == '(' and paramCode[-1] == ')':
			#	shorterCode = paramCode[1:-1]
				
				# Test if it is valid
			#	if 0:#shorterCode.find("(") <= shorterCode.find(")"):
			#		paramCode = shorterCode
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
		tabbedNewline = tabs + "\n"
		prefix = ""
		previousChildName = ""
		previousLineType = 0
		currentLineType = 1
		wrapperExpr = list()
		
		for child in node.childNodes:
			# Child name
			if child.nodeType != Node.TEXT_NODE:
				childName = child.tagName
			else:
				childName = ""
			
			# Line type
			if childName in autoNewlineBlock:
				if childName in {"require", "ensure", "maybe"} or (childName == "test" and previousLineType == 3):
					currentLineType = 3
				else:
					currentLineType = 2
			elif childName == "comment":
				currentLineType = 0
			else:
				currentLineType = 1
			
			# Process line type
			prefix = ""
			if child.nodeType != Node.TEXT_NODE and child.hasAttribute("implemented") and child.getAttribute("implemented") == "false":
				pass
			elif previousLineType:
				if (currentLineType + previousLineType >= 3 or (currentLineType == 0 and previousLineType > 0)) and currentLineType != 3:
					prefix = tabbedNewline
			elif previousLineType == 0 and previousChildName == "comment" and currentLineType == 2 and childName in {"getter", "setter", "operator", "iterator-type"}:
				prefix = "\n"
			
			# Set previous line type
			previousLineType = currentLineType
			previousChildName = childName
			
			# Convert node
			if conv is not None:
				if prefix:
					conv.add(None)
				
				childCode = nodeToBPCSaved(child, tabLevel, conv)
			else:
				childCode = nodeToBPC(child, tabLevel, conv)
			
			# Add code parts
			if childName == "if-block" or childName == "try-block":
				codeParts.append(prefix)
				codeParts.append(childCode.rstrip())
				#if childCode[-1] != "\n":
				codeParts.append("\n")
				
				if currentSyntax == SYNTAX_RUBY:
					codeParts.append(tabs + "end\n")
			elif childName in {"default-get", "default-set"}:
				wrapperExpr.append(child.firstChild.firstChild.nodeValue)
			else:
				if nodeName != "code" and nodeName != "extern":
					codeParts.append(prefix)
					codeParts.append(tabs)
					codeParts.append(childCode)
				else:
					codeParts.append(prefix)
					codeParts.append(tabs)
					
					if childCode and (not childCode[-1] == "\n"):
						codeParts.append(childCode.rstrip())
						
						if currentSyntax == SYNTAX_CPP:
							if not childCode.endswith("}") and not currentLineType == 0:
								codeParts.append("\n")
								#codeParts.append(";\n")
							else:
								codeParts.append("\n")
						else:
							# All syntaxes except C++
							codeParts.append("\n")
					else:
						codeParts.append(childCode)
		
		if isVisibleBlock:
			if wrapperExpr:
				wrapperExprString = " " + ', '.join(wrapperExpr)
			else:
				wrapperExprString = ""
			
			if currentSyntax == SYNTAX_BPC:
				return "%s%s\n%s" % (wrapperMultipleElements[nodeName], wrapperExprString, ''.join(codeParts))
			elif currentSyntax == SYNTAX_CPP:
				return wrapperMultipleElements[nodeName] + wrapperExprString + " {\n" + ''.join(codeParts).rstrip() + "\n" + "\t" * (tabLevel - 1) + "}\n"
			elif currentSyntax == SYNTAX_RUBY:
				return wrapperMultipleElements[nodeName] + wrapperExprString + "\n" + ''.join(codeParts).rstrip() + "\n" + "\t" * (tabLevel - 1) + "end\n"
			elif currentSyntax == SYNTAX_PYTHON:
				return wrapperMultipleElements[nodeName] + wrapperExprString + ":\n" + ''.join(codeParts)
		
		return ''.join(codeParts)
	# Function definition
	elif nodeName in functionNodeTagNames:#== "function" or nodeName == "operator" or nodeName == "getter" or nodeName == "setter" or nodeName == "cast-definition":
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
		
		funcName = nodeToBPC(name, 0, conv)
		
		if node.nodeType != Node.TEXT_NODE and node.hasAttribute("implemented") and node.getAttribute("implemented") == "false":
			codeText = ""
			implemented = False
		else:
			codeText = nodeToBPC(code, tabLevel + 1, conv)
			implemented = True
		
		# Syntax
		if currentSyntax == SYNTAX_BPC:
			return "%s%s\n%s" % (funcName, paramsCode, codeText)
		elif currentSyntax == SYNTAX_RUBY:
			if implemented:
				endOfBlock = ("\t" * (tabLevel)) + "end\n"
			else:
				endOfBlock = ""
			return funcName + paramsCode + "\n" + codeText + endOfBlock
		elif currentSyntax == SYNTAX_CPP:
			if implemented:
				endOfBlock = ("\t" * (tabLevel)) + "}\n"
			else:
				endOfBlock = ""
			return funcName + " (" + paramsCode.strip() + ")" + ["", " {"][implemented] + "\n" + codeText + endOfBlock
		elif currentSyntax == SYNTAX_PYTHON:
			return "def " + funcName + "(" + paramsCode.strip() + ")" + ["", ":"][implemented] + "\n" + codeText
	elif nodeName == "comment":
		return "#" + decodeCDATA(node.childNodes[0].nodeValue)
	elif nodeName == "negative":
		if node.childNodes[0].firstChild.nodeType == Node.TEXT_NODE:
			return "-" + nodeToBPC(node.childNodes[0].firstChild, 0, conv)
		else:
			return "-(" + nodeToBPC(node.childNodes[0].firstChild, 0, conv) + ")"
	elif nodeName == "unmanaged":
		return "~" + nodeToBPC(node.childNodes[0], 0, conv)
	elif nodeName == "new":
		newType = nodeToBPC(getElementByTagName(node, "type"), 0, conv)
		newParams = nodeToBPC(getElementByTagName(node, "parameters"), 0, conv)
		
		if currentSyntax == SYNTAX_CPP:
			return "new %s(%s)" % (newType, newParams)
		else:
			return "%s(%s)" % (newType, newParams)
	elif nodeName == "module":
		header = getElementByTagName(node, "header")
		code = getElementByTagName(node, "code")
		return nodeToBPC(header, 0, conv) + nodeToBPC(code, 0, conv)
	elif nodeName == "header":
		depNode = getElementByTagName(node, "dependencies")
		return nodeToBPC(depNode, 0, conv)
	elif nodeName == "dependencies":
		deps = ""
		lastLine = ""
		hadSomethingInCommon = False
		
		for child in node.childNodes:
			if child.nodeType != Node.TEXT_NODE and child.tagName == "import":
				importCode = nodeToBPCSaved(child, 0, conv)
				
				if lastLine:
					if hadSomethingInCommon and not haveSomethingInCommon(importCode, lastLine):
						deps += "\n"
						hadSomethingInCommon = False
						
						# Keep line converter up to date
						if conv:
							conv.add(None)
					else:
						if haveSomethingInCommon(importCode, lastLine):
							hadSomethingInCommon = True
				
				if importCode:
					deps += importCode + "\n"
					
				lastLine = importCode
					
		if deps:
			if conv:
				conv.add(None)
			return deps + "\n"
		else:
			return ""
	elif nodeName == "import":
		importMod = node.childNodes[0].nodeValue.strip()
		
		# Imported by default
		if importMod == "flua.Core":
			return ""
		
		return "import " + importMod
	elif nodeName in {"for", "parallel-for"}:
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
		
		exprStart = " "
		blockStart = ""
		blockEnd = ""
		
		if currentSyntax == SYNTAX_RUBY:
			blockEnd = "end"
		elif currentSyntax == SYNTAX_CPP:
			exprStart = " ("
			blockStart = ") {"
			blockEnd = "}"
		elif currentSyntax == SYNTAX_PYTHON:
			blockStart = ":"
		
		if nodeName == "parallel-for":
			keyword = "pfor"
		else:
			keyword = "for"
		
		forLoop = "%s%s%s = %s %s %s%s\n%s%s%s" % (keyword, exprStart, iterator, start, toUntil, end, blockStart, loopCode, "\t" * tabLevel, blockEnd)
			
		return forLoop
	elif nodeName in {"foreach", "parallel-foreach"}:
		iterator = nodeToBPC(getElementByTagName(node, "iterator").firstChild, 0, conv)
		coll = nodeToBPC(getElementByTagName(node, "collection").firstChild, 0, conv)
		loopCode = nodeToBPC(getElementByTagName(node, "code"), tabLevel + 1, conv)
		
		counterNode = getElementByTagName(node, "counter")
		if counterNode:
			counter = " counting " + nodeToBPC(counterNode.firstChild, 0, conv)
		else:
			counter = ""
		
		exprStart = " "
		blockStart = ""
		blockEnd = ""
		
		if currentSyntax == SYNTAX_RUBY:
			blockEnd = "end"
		elif currentSyntax == SYNTAX_CPP:
			exprStart = " ("
			blockStart = ") {"
			blockEnd = "}"
		elif currentSyntax == SYNTAX_PYTHON:
			blockStart = ":"
		
		if nodeName == "parallel-foreach":
			keyword = "pfor"
		else:
			keyword = "for"
		
		return "%s%s%s in %s%s%s\n%s%s%s" % (keyword, exprStart, iterator, coll, counter, blockStart, loopCode, "\t" * tabLevel, blockEnd)
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
	elif nodeName == "extern-function" or nodeName == "extern-variable":
		nameNode = getElementByTagName(node, "name")
		typeNode = getElementByTagName(node, "type")
		typeName = ""
		
		if typeNode:
			typeName = nodeToBPC(typeNode, 0, conv)
			typeName = " : " + typeName
		
		return nodeToBPC(nameNode, 0, conv) + typeName
	elif nodeName == "class" or nodeName == "interface":
		nameNode = getElementByTagName(node, "name")
		codeNode = getElementByTagName(node, "code")
		className = nodeToBPC(nameNode, 0, conv)
		
		if className.startswith("Mutable"):
			className = className[len("Mutable"):]
		elif className.startswith("Immutable"):
			className = className[len("Immutable"):]
		
		if nodeName == "interface":
			keyword = "interface "
		else:
			if currentSyntax == SYNTAX_PYTHON:
				keyword = "class "
			else:
				keyword = ""
		
		if currentSyntax == SYNTAX_BPC:
			return keyword + className + "\n" + nodeToBPC(codeNode, tabLevel + 1 ,conv).rstrip() + "\n"
		if currentSyntax == SYNTAX_RUBY:
			return keyword + className + "\n" + nodeToBPC(codeNode, tabLevel + 1 ,conv).rstrip() + "\n" + ("\t" * (tabLevel)) + "end"
		if currentSyntax == SYNTAX_CPP:
			return keyword + className + " {\n" + nodeToBPC(codeNode, tabLevel + 1 ,conv).rstrip() + "\n" + ("\t" * (tabLevel)) + "}"
		if currentSyntax == SYNTAX_PYTHON:
			return keyword + className + ":\n" + nodeToBPC(codeNode, tabLevel + 1 ,conv).rstrip() + "\n"
	elif nodeName == "noop":
		return "..."
	# Single line
	elif nodeName in xmlToBPCSingleLineExpr:
		keyword = xmlToBPCSingleLineExpr[nodeName]
		
		if node.childNodes:
			if keyword:
				return "%s %s" % (keyword, nodeToBPC(node.childNodes[0], 0, conv))
			else:
				return nodeToBPC(node.childNodes[0], 0, conv)
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
		
		if currentSyntax == SYNTAX_RUBY and name == "elif":
			name = "elsif"
		
		if not code:
			code = "\t" * (tabLevel + 1) + "..."
		
		if currentSyntax == SYNTAX_BPC:
			return "%s%s%s\n%s" % (name, space, expr, code)
		elif currentSyntax == SYNTAX_PYTHON:
			return "%s%s%s:\n%s" % (name, space, expr, code)
		elif currentSyntax == SYNTAX_RUBY:
			if not name in {"if", "elsif", "else", "try", "catch"}:
				return "%s%s%s\n%s%send\n" % (name, space, expr.strip(), code, ("\t" * (tabLevel)))
			else:
				return "%s%s%s\n%s" % (name, space, expr.strip(), code)
		elif currentSyntax == SYNTAX_CPP:
			if code.endswith("}"):
				code += "\n"
				
			if not nodeName in {"target", "parallel"}:
				return "%s%s(%s) {\n%s%s}\n" % (name, " ", expr.strip(), code, ("\t" * (tabLevel)))
			else:
				return "%s%s%s {\n%s%s}\n" % (name, space, expr.strip(), code, ("\t" * (tabLevel)))
	# Blocks
	elif nodeName in xmlToBPCBlock:
		blockCode = ""
		tabs = ""
		if nodeName != "else":
			tabs = "\t" * (tabLevel + 1)
		for child in node.childNodes:
			if child.nodeType != Node.TEXT_NODE:
				blockCode += tabs + nodeToBPCSaved(child, tabLevel + 1, conv) + "\n"
		#if blockCode[-2].isspace():
		#	blockCode = blockCode.rstrip() + "\n"
		#else:
		#blockCode = blockCode + "\t" * tabLevel
		
		if currentSyntax == SYNTAX_BPC:
			return xmlToBPCBlock[nodeName] + "\n" + blockCode.rstrip() # + "\n" + ("\t" * (tabLevel)) + "#Here"
		elif currentSyntax == SYNTAX_PYTHON:
			return xmlToBPCBlock[nodeName] + ":\n" + blockCode.rstrip()
		elif currentSyntax == SYNTAX_CPP:
			return xmlToBPCBlock[nodeName] + " {\n" + blockCode.rstrip() + "\n" + ("\t" * (tabLevel)) + "}\n"
		elif currentSyntax == SYNTAX_RUBY:
			if not nodeName == "else":
				return xmlToBPCBlock[nodeName] + "\n" + blockCode.rstrip() + "\n" + ("\t" * (tabLevel)) + "end\n"
			else:
				return xmlToBPCBlock[nodeName] + "\n" + blockCode.rstrip() + "\n" + ("\t" * (tabLevel)) + "\n"
	elif nodeName == "not":
		return "not " + nodeToBPC(node.firstChild, 0, conv)
	elif nodeName == "meta":
		return ""
	# Binary operations
	elif nodeName in binaryOperatorTagToSymbol:
		op1 = node.childNodes[0].childNodes[0]
		op2 = node.childNodes[1].childNodes[0]
		space = " "
		prefix = ""
		postfix = ""
		
		op1bpc = nodeToBPC(op1, 0, conv)
		op2bpc = nodeToBPC(op2, 0, conv)
		
		if nodeName == "template-call":
			return op1bpc + "<" + op2bpc + ">"
		elif nodeName == "index":
			if op1bpc == "_flua_seq":
				op1bpc = ""
			
			return op1bpc + "[" + op2bpc + "]"
		elif nodeName == "slice":
			return op1bpc + "[" + op2bpc + "]"
		elif nodeName == "range":
			return op1bpc + ":" + op2bpc
		elif nodeName == "exists-in":
			return op1bpc + " in " + op2bpc
		# String parameters
		elif nodeName == "add" and (op1.nodeType == Node.TEXT_NODE and op1.nodeValue.startswith("flua_string_") and op2.nodeType == Node.TEXT_NODE and not isNumeric(op2.nodeValue)):
			if op2.nodeValue.startswith("flua_string_"):
				return '%s + %s' % (op1bpc, op2bpc)
			else:
				return '%s$%s"' % (op1bpc[:-1], op2bpc)
		elif nodeName == "add" and (op1bpc.startswith('"') and op1bpc.endswith('"')) and op2.nodeType == Node.TEXT_NODE:
			#String
			if op2.nodeValue.startswith("flua_string_"):
				# If the start of the string is a character for variables it's not safe to combine them
				if not isVarChar(op2bpc[1]):
					return '%s%s' % (op1bpc[:-1], op2bpc[1:])
				else:
					return '%s + %s' % (op1bpc, op2bpc)
			#Variable
			else:
				if isNumeric(op2.nodeValue):
					return '%s%s"' % (op1bpc[:-1], op2bpc)
				return '%s$%s"' % (op1bpc[:-1], op2bpc)
		
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
		elif hasHigherPriority(operationAbove, nodeName):
			prefix = "("
			postfix = ")"
		
		if nodeName == "in-range":
			op3 = node.childNodes[2].childNodes[0]
			op3bpc = nodeToBPC(op3, 0, conv)
			lowerSymbol = binaryOperatorTagToSymbol[node.getAttribute("lower-operation")]
			upperSymbol = binaryOperatorTagToSymbol[node.getAttribute("upper-operation")]
			return ''.join([prefix, op1bpc, space, lowerSymbol, space, op2bpc, space, upperSymbol, space, op3bpc, postfix])
		
		# Translate
		opSymbol = binaryOperatorTagToSymbol[nodeName]
		if opSymbol in translateLogicalOperatorSign:
			opSymbol = translateLogicalOperatorSign[opSymbol]
		
		return ''.join([prefix, op1bpc, space, opSymbol, space, op2bpc, postfix])
	
	raise CompilerException("Can't turn „%s“ into BPC code, unknown element tag" % (nodeName))

def getCalledFuncName(node):
	try:
		funcNameNode = getFuncNameNode(node)
	except:
		raise CompilerException("Invalid function call")
	
	caller = ""
	if funcNameNode.nodeType == Node.TEXT_NODE:
		funcName = funcNameNode.nodeValue
	else:
		caller = nodeToBPC(funcNameNode.childNodes[0].childNodes[0])
		funcName = funcNameNode.childNodes[1].childNodes[0].nodeValue
	
	if caller:
		funcName = caller + "." + funcName
	
	return funcName
