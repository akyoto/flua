####################################################################
# Header
####################################################################
# Target:   C++ Code
# Author:   Eduard Urbach

####################################################################
# License
####################################################################
# (C) 2008  Eduard Urbach
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
from ExpressionParser import *
from Utils import *
import codecs
import subprocess

####################################################################
# Classes
####################################################################
class CPPClass:
	
	def __init__(self, name, cppFile):
		self.name = name
		self.cppFile = cppFile
		self.functions = {}
		self.members = {}
		
class CPPVariable:
	
	def __init__(self, name, type, value, isConst = False):
		self.name = name
		self.type = type
		self.value = value
		self.isConst = isConst
		
class CPPFunction:
	
	def __init__(self, file, node):
		self.file = file
		self.node = node
		self.implementations = {}
		
	def getName(self):
		return getElementByTagName(self.node, "name").childNodes[0].nodeValue

class FunctionImplRequest:
	
	def __init__(self, name, paramTypes):
		self.name = name
		self.paramTypes = paramTypes
		self.implementation = ""
		
	def getName(self):
		return self.name
		
	def getPrototype(self):
		return self.name + "(" + ", ".join(self.paramTypes) + ")"
	
	def isImplemented(self):
		return self.implementation != ""

class CPPOutputCompiler:
	
	def __init__(self, inpCompiler):
		self.inputCompiler = inpCompiler
		self.inputFiles = inpCompiler.getCompiledFiles()
		self.compiledFiles = dict()
		self.compiledFilesList = []
		self.projectDir = self.inputCompiler.projectDir
		self.modDir = inpCompiler.modDir
		self.stringCounter = 0;
		self.fileCounter = 0;
		self.outputDir = ""
		self.mainFile = ""
		self.globalScope = Scope()
		self.implementationRequests = {}
		self.functionTypes = {}
		
		self.classes = {}
		self.classes[""] = CPPClass("", None)
	
	def compile(self, inpFile):
		cppOut = CPPOutputFile(self, inpFile)
		self.compiledFiles[inpFile] = cppOut
		self.compiledFilesList.insert(0, cppOut)
		
		for imp in inpFile.importedFiles:
			inFile = self.inputCompiler.getFileInstanceByPath(imp)
			if (not inFile in self.compiledFiles):
				self.compile(inFile)
		
		cppOut.compile()
		
#		self.inputFiles.reverse()
#		for inpFile in self.inputFiles:
#			cppOut = CPPOutputFile(self, inpFile)
#			cppOut.compile()
#			self.compiledFiles[inpFile] = cppOut
#			self.compiledFilesList.append(cppOut)
			
		# 2 times because at the first run there might have appeared new calls
#		for i in range(2):
#			for cppFile in self.compiledFiles.values():
#				cppFile.implement()
	
	def writeToFS(self, dirOut):
		dirOut = fixPath(os.path.abspath(dirOut)) + "/"
		self.outputDir = dirOut
		
		for cppFile in self.compiledFiles.values():
			fileOut = dirOut + stripExt(os.path.relpath(cppFile.file, self.projectDir)) + "-out.hpp"
			
			# Directory structure
			concreteDirOut = os.path.dirname(fileOut)
			if not os.path.isdir(concreteDirOut):
				os.makedirs(concreteDirOut)
			
			with open(fileOut, "w") as outStream:
				outStream.write(cppFile.getCode())
			
			# CPP main file
			if cppFile.isMainFile:
				hppFile = os.path.basename(fileOut)
				
				fileOut = dirOut + stripExt(cppFile.file[len(self.projectDir):]) + "-out.cpp"
				self.mainFile = fileOut
				
				# Write main file
				with open(fileOut, "w") as outStream:
					outStream.write("#include \"" + hppFile + "\"\n\nint main(int argc, char *argv[]) {\n" + self.getFileExecList() + "\treturn 0;\n}\n")
		
	def build(self):
		exe = stripExt(self.mainFile)
		if os.path.isfile(exe):
			os.unlink(exe)
		
		cmd = ["g++", self.mainFile, "-o", exe, "-I" + self.outputDir, "-I" + self.modDir]
		try:
			proc = subprocess.Popen(cmd)
			proc.wait()
		except OSError:
			print("Couldn't start g++")
		
		return exe
	
	def execute(self, exe):
		cmd = [exe]
		
		try:
			proc = subprocess.Popen(cmd)
			proc.wait()
		except OSError:
			print("Build process failed")
	
	def getFileExecList(self):
		files = ""
		for cppFile in self.compiledFilesList:
			files += "\texec_" + cppFile.id + "();\n"
		return files
	
	def getTargetName(self):
		return "C++"
	
class CPPOutputFile(ScopeController):
	
	def __init__(self, compiler, inpFile):
		self.currentTabLevel = 0
		
		ScopeController.__init__(self)
		
		self.compiler = compiler
		self.file = inpFile.file
		self.root = inpFile.getRoot()
		self.isMainFile = inpFile.isMainFile
		self.dir = inpFile.dir
		self.codeNode = getElementByTagName(self.root, "code")
		self.headerNode = getElementByTagName(self.root, "header")
		self.dependencies = getElementByTagName(self.headerNode, "dependencies")
		self.strings = getElementByTagName(self.headerNode, "strings")
		self.exprPrefix = ""
		self.exprPostfix = ""
		
		self.classes = dict()
		self.classes[""] = CPPClass("", self)
		self.compiler.classes[""].cppFile = self
		
		self.currentClass = self.compiler.classes[""]
		
		self.inConst = False
		self.inClass = False
		self.inFunction = False
		self.currentFuncReturnTypes = []
		
		self.dataTypeWeights = {
			"Bool" : 1,
			"Byte" : 2,
			"Short" : 3,
			"Int" : 4,
			"Float" : 5,
			"Double" : 6
		}
		
		# XML tag : C++ keyword, condition tag name, code tag name
		self.paramBlocks = {
			"if" : ["if", "condition", "code"],
			"else-if" : [" else if", "condition", "code"],
			"while" : ["while", "condition", "code"]
		}
		
		#self.id = self.file.replace("/", "_").replace(".", "_")
		self.id = "file_" + str(self.compiler.fileCounter)
		self.compiler.fileCounter += 1
		
		self.header = "#ifndef " + self.id + "\n#define " + self.id + "\n\n"
		self.topLevel = ""
		self.footer = "#endif\n"
		self.stringsHeader = ""
		self.varsHeader = ""
		self.functionsHeader = ""
		self.classesHeader = ""
		self.typeDefsHeader = "\n// Typedefs\n"
		self.prototypesHeader = "\n// Prototypes\n"
		
	def pushScope(self):
		self.currentTabLevel += 1
		ScopeController.pushScope(self)
		
	def popScope(self):
		self.currentTabLevel -= 1
		ScopeController.popScope(self)
		
	def compile(self):
		print("Output: " + self.file)
		
		# Find classes
		self.findDefinitions(self.codeNode)
		
		# Header
		self.header += "// Includes\n";
		for node in self.dependencies.childNodes:
			self.header += self.handleImport(node)
		
		self.header += "\n#define String const char *\n"
		
		# Functions
		self.functionsHeader += "\n// Functions\n";
		
		# Code
		self.topLevel += "// Module execution\n";
		self.topLevel += "void exec_" + self.id + "() {\n"
		
		# Strings
		self.stringsHeader = "\t// Strings\n";
		for node in self.strings.childNodes:
			self.stringsHeader += "\t" + self.handleString(node)
		self.stringsHeader += "\n\t// Code\n"
		
		self.topLevel += self.stringsHeader
		
		# Top level code
		self.topLevel += self.parseChilds(self.codeNode, "\t" * self.currentTabLevel, ";\n")
		self.topLevel += "}\n"
		
		# Variables
		self.varsHeader = "\n// Variables\n";
		for var in self.getTopLevelScope().variables.values():
			if var.isConst:
				self.varsHeader += "const " + var.type + " " + var.name + " = " + var.value + ";\n";
			else:
				self.varsHeader += var.type + " " + var.name + ";\n";
		
		#print(self.getCode())
		
	def parseChilds(self, parent, prefix = "", postFix = ""):
		lines = ""
		for node in parent.childNodes:
			line = self.parseExpr(node)
			if line:
				lines += prefix + line + postFix
		return lines
		
	def findDefinitions(self, parent):
		for node in parent.childNodes:
			if isTextNode(node):
				pass
			elif node.tagName == "class":
				self.handleClass(node)
			elif node.tagName == "function":
				self.handleFunction(node)
		
	def parseExpr(self, node):
		if isTextNode(node):
			if node.nodeValue.startswith("bp_string_"):
				return self.id + "_" + node.nodeValue
			else:
				return node.nodeValue
		
		tagName = node.tagName
		
		if tagName == "value":
			return self.parseExpr(node.childNodes[0])
		elif tagName == "access":
			return self.handleAccess(node)
		elif tagName == "assign":
			return self.handleAssign(node)
		elif tagName == "call":
			return self.handleCall(node)
		elif tagName == "if-block" or tagName == "try-block":
			return self.parseChilds(node, "", "")
		elif tagName == "else":
			return self.handleElse(node)
		elif tagName == "class":
			return ""
		elif tagName == "function":
			if self.currentClass.name == "":
				return ""
			return self.handleFunction(node)
		elif tagName == "extern":
			return self.handleExtern(node)
		elif tagName == "extern-function":
			return self.handleExternFunction(node)
		elif tagName == "target":
			return self.handleTarget(node)
		elif tagName == "new":
			return self.handleNew(node)
		elif tagName == "return":
			return self.handleReturn(node)
		elif tagName == "include":
			self.header += "#include \"" + node.childNodes[0].nodeValue + "\"\n"
			return ""
		elif tagName == "const":
			return self.handleConst(node)
		elif tagName == "noop":
			return ""
		
		# Check parameterized blocks
		if tagName in self.paramBlocks:
			paramBlock = self.paramBlocks[node.tagName]
			keywordName = paramBlock[0]
			paramTagName = paramBlock[1]
			codeTagName = paramBlock[2]
			
			condition = self.parseExpr(getElementByTagName(node, paramTagName).childNodes[0])
			
			self.pushScope()
			code = self.parseChilds(getElementByTagName(node, codeTagName), "\t" * self.currentTabLevel, ";\n")
			self.popScope()
			
			return keywordName + "(" + condition + ") {\n" + code + "\t" * self.currentTabLevel + "}"
		
		# Check operators
		for opLevel in self.compiler.inputCompiler.parser.operatorLevels:
			for op in opLevel.operators:
				if tagName == op.name:
					if op.type == Operator.BINARY:
						if op.text == "\\":
							return self.parseBinaryOperator(node, " / ")
						return self.parseBinaryOperator(node, " " + op.text + " ")
					elif op.type == Operator.UNARY:
						return op.text + "(" + self.parseExpr(node.childNodes[0]) + ")"
		
		return "";
		
	def handleAccess(self, node):
		return self.parseBinaryOperator(node, "->")
		
	def handleConst(self, node):
		self.inConst = True
		expr = self.parseExpr(node.childNodes[0])
		self.inConst = False
		
		return expr
		
	def handleAssign(self, node):
		variable = self.parseExpr(node.childNodes[0])
		value = self.parseExpr(node.childNodes[1])
		valueTypeOriginal = self.getExprDataType(node.childNodes[1].childNodes[0])
		
		variableExisted = self.variableExistsAnywhere(variable)
		
		if not variableExisted:
			var = CPPVariable(variable, valueTypeOriginal, value, self.inConst)
			self.getCurrentScope().variables[variable] = var
			if self.getCurrentScope() == self.getTopLevelScope():
				self.compiler.globalScope.variables[variable] = var
				
			if self.inConst:
				if self.getCurrentScope() == self.getTopLevelScope():
					return ""
				else:
					return "const %s %s = %s" % (valueTypeOriginal, variable, value)
			#print(variable + " = " + valueTypeOriginal)
		
		if variable.startswith("this->"):
			member = variable[len("this->"):]
			self.currentClass.members[member] = valueTypeOriginal
			
		if variableExisted or self.getCurrentScope() == self.getTopLevelScope():
			return variable + " = " + value
		else:
			return valueTypeOriginal + " " + variable + " = " + value
		
	def handleExtern(self, node):
		self.pushScope()
		code = self.parseChilds(node, "\t" * self.currentTabLevel, ";\n")
		self.popScope()
		
		return code
	
	def handleExternFunction(self, node):
		name = getElementByTagName(node, "name").childNodes[0].nodeValue
		types = node.getElementsByTagName("type")
		type = "void"
		
		if types:
			type = types[0].childNodes[0].nodeValue
		
		self.compiler.functionTypes[name] = type
		
		return ""
		
	def buildCallPostfix(self, types):
		postfix = ""
		for dataType in types:
			postfix += "__" + dataType
		return postfix
		
	def handleReturn(self, node):
		expr = self.parseExpr(node.childNodes[0])
		self.currentFuncReturnTypes.append(self.getExprDataType(node.childNodes[0]))
		return "return " + expr
		
	def handleNew(self, node):
		typeName = self.parseExpr(getElementByTagName(node, "type").childNodes[0])
		params = getElementByTagName(node, "parameters")
		
		paramsString, paramTypes = self.handleParameters(params)
		
		prefix = ""
		if not typeName in self.dataTypeWeights:
			prefix = "BP"
		
		oldClass = self.currentClass
		self.currentClass = self.compiler.classes[typeName]
		
		# Implement init
		funcName = "init"
		func = self.currentClass.functions[funcName]
		
		self.inClass = True
		
		func.implementations[self.buildCallPostfix(paramTypes)] = self.implementFunction(func.node, paramTypes, "\t")
		
		self.inClass = False
		self.currentClass = oldClass
		
		return "new " + prefix + typeName + "(" + paramsString + ")"
		
	def handleClass(self, node):
		name = getElementByTagName(node, "name").childNodes[0].nodeValue
		
		self.pushScope()
		self.inClass = True
		self.currentClass = self.classes[name] = self.compiler.classes[name] = CPPClass(name, self)
		
		code = self.parseChilds(getElementByTagName(node, "code"), "\t", ";\n")
		
		self.currentClass = self.compiler.classes[""]
		self.inClass = False
		self.popScope()
		
		return ""
		
	def handleFunction(self, node):
		name = getElementByTagName(node, "name").childNodes[0].nodeValue
		self.currentClass.functions[name] = CPPFunction(self, node)
		
		#print("Registered " + name)
		return ""
		
	def getCallFunction(self, node):
		funcNameNode = getElementByTagName(node, "function").childNodes[0]
		
		caller = ""
		callerType = ""
		if isTextNode(funcNameNode): #and funcNameNode.tagName == "access":
			funcName = funcNameNode.nodeValue
		else:
			callerType = self.getExprDataType(funcNameNode.childNodes[0].childNodes[0])
			caller = self.parseExpr(funcNameNode.childNodes[0].childNodes[0])
			funcName = funcNameNode.childNodes[1].childNodes[0].nodeValue
			#print(callerType + "::" + funcName)
		
		return caller, callerType, funcName
		
	def handleCall(self, node):
		caller, callerType, funcName = self.getCallFunction(node)
		
		params = getElementByTagName(node, "parameters")
		
		paramsString, paramTypes = self.handleParameters(params)
		implRequest = FunctionImplRequest(callerType + "::" + funcName, paramTypes)
		
		fullName = funcName + self.buildCallPostfix(paramTypes)
		
		if not funcName.startswith("bp_"):
			if not implRequest.getPrototype() in self.compiler.implementationRequests:
				self.compiler.implementationRequests[implRequest.getPrototype()] = implRequest
				#print("Requested implementation of " + implRequest.getPrototype())
				
				if funcName in self.compiler.classes[callerType].functions:
					func = self.compiler.classes[callerType].functions[funcName]
				else:
					raise CompilerException("Function '" + funcName + "' has not been defined")
				
				self.oldClass = self.currentClass
				self.currentClass = self.compiler.classes[callerType]
				if callerType:
					self.currentClass.functions[funcName].implementations[self.buildCallPostfix(paramTypes)] = self.implementFunction(func.node, implRequest.paramTypes)
				else:
					cppFile = self
					cppFile.functionsHeader += self.implementFunction(func.node, implRequest.paramTypes)
					
					prototype = "inline " + self.compiler.functionTypes[callerType + "::" + fullName] + " " + fullName + "(" + ", ".join(paramTypes) + ");\n"
					cppFile.prototypesHeader += prototype
					
					if self.oldClass:
						self.oldClass.cppFile.prototypesHeader += prototype
				self.currentClass = self.oldClass
			
			if callerType in self.dataTypeWeights:
				return ["", caller + "."][caller != ""] + fullName + "(" + paramsString + ")"
			else:
				return ["", caller + "->"][caller != ""] + fullName + "(" + paramsString + ")"
		else:
			return funcName + "(" + paramsString + ")"
		
	def implementFunction(self, node, types, tabLevel = ""):
		origName = name = getElementByTagName(node, "name").childNodes[0].nodeValue
		
		#if self.inClass:
		#	tabLevel *= self.currentTabLevel
		
		self.pushScope()
		self.getCurrentScope().variables["self"] = CPPVariable("self", self.currentClass.name, "")
		
		# Add class variables to scope
		for memberName, memberType in self.currentClass.members.items():
			self.getCurrentScope().variables[memberName] = CPPVariable(memberName, memberType, "")
		
		self.inFunction = True
		self.currentFuncReturnTypes = []
		
		parameters, funcStartCode = self.getParameterDefinitions(getElementByTagName(node, "parameters"), types)
		code = self.parseChilds(getElementByTagName(node, "code"), tabLevel + "\t", ";\n")
		
		self.inFunction = False
		self.popScope()
		
		funcReturnType = self.getFunctionReturnType()
		
		name = self.currentClass.name + "::" + name
		#print(name + self.buildCallPostfix(types) + " -> " + funcReturnType)
		self.compiler.functionTypes[name + self.buildCallPostfix(types)] = funcReturnType
		
		funcName = funcReturnType + " " + origName + self.buildCallPostfix(types)
		if self.inClass and name == self.currentClass.name + "::init":
			funcName = "BP" + self.currentClass.name
		
		return "inline " + funcName + "(" + parameters + ") {\n" + funcStartCode + code + tabLevel + "}\n\n"
#		if self.inClass:
#			return tabLevel + "inline void " + name + "(" + parameters + ") {\n" + code + tabLevel + "}\n\n"
#		else:
#			self.functionsHeader += tabLevel + "inline void " + name + "(" + parameters + ") {\n" + code + tabLevel + "}\n\n"
#			return ""
		
	def getFunctionReturnType(self):
		heaviest = None
		
		for type in self.currentFuncReturnTypes:
			if type in self.dataTypeWeights:
				heaviest = self.heavierOperator(heaviest, type)
			else:
				return type
		
		if heaviest:
			return heaviest
		else:
			return "void"
		
	def handleElse(self, node):
		self.pushScope()
		code = self.parseChilds(getElementByTagName(node, "code"), "\t" * self.currentTabLevel, ";\n")
		self.popScope()
		
		return " else {\n" + code + "\t" * self.currentTabLevel + "}"
		
	def handleTarget(self, node):
		name = getElementByTagName(node, "name").childNodes[0].nodeValue
		if name == self.compiler.getTargetName():
			return self.parseChilds(getElementByTagName(node, "code"), "\t" * self.currentTabLevel, ";\n")
		
	def handleString(self, node):
		id = self.id + "_" + node.getAttribute("id")
		value = node.childNodes[0].nodeValue
		line = id + " = \"" + value + "\";\n"
		self.getTopLevelScope().variables[id] = CPPVariable(id, "String", value)
		self.compiler.stringCounter += 1
		return line
		
	def handleParameters(self, pNode):
		pList = ""
		pTypes = []
		for node in pNode.childNodes:
			pList += self.parseExpr(node.childNodes[0]) + ", "
			pTypes.append(self.getExprDataType(node.childNodes[0]))
		
		return pList[:len(pList)-2], pTypes
	
	def getParameterList(self, pNode):
		pList = []
		
		for node in pNode.childNodes:
			pList.append(self.parseExpr(node.childNodes[0]))
		
		return pList
	
	def getParameterDefinitions(self, pNode, types):
		pList = ""
		funcStartCode = ""
		counter = 0
		
		for node in pNode.childNodes:
			name = self.parseExpr(node.childNodes[0])
			if name.startswith("this->"):
				member = name[len("this->"):]
				self.currentClass.members[member] = types[counter]
				name = "__" + member
				funcStartCode += "\t" * self.currentTabLevel + "this->" + member + " = " + name + ";\n"
			pList += types[counter] + " " + name + ", "
			self.getCurrentScope().variables[name] = CPPVariable(name, types[counter], "")
			counter += 1
		
		return pList[:len(pList)-2], funcStartCode
	
	def handleImport(self, node):
		importedModulePath = node.childNodes[0].nodeValue.replace(".", "/")
		
		# Local
		importedFile = self.dir + importedModulePath + ".bpc"
		
		importedInFolder = self.dir + importedModulePath
		importedInFolder += "/" + stripAll(importedInFolder) + ".bpc"
		
		# Project
		pImportedFile = self.compiler.projectDir + importedModulePath + ".bpc"
		
		pImportedInFolder = self.compiler.projectDir + importedModulePath
		pImportedInFolder += "/" + stripAll(pImportedInFolder) + ".bpc"
		
		# Global
		gImportedFile = self.compiler.modDir + importedModulePath + ".bpc"
		
		gImportedInFolder = self.compiler.modDir + importedModulePath
		gImportedInFolder += "/" + stripAll(pImportedInFolder) + ".bpc"
		
		modPath = ""
		
		if os.path.isfile(importedFile):
			modPath = importedFile
		elif os.path.isfile(importedInFolder):
			modPath = importedInFolder
		elif os.path.isfile(pImportedFile):
			modPath = pImportedFile
		elif os.path.isfile(pImportedInFolder):
			modPath = pImportedInFolder
		elif os.path.isfile(gImportedFile):
			modPath = gImportedFile
		elif os.path.isfile(gImportedInFolder):
			modPath = gImportedInFolder
		
		if modPath.startswith(self.compiler.projectDir):
			modPath = modPath[len(self.compiler.projectDir):]
		elif modPath.startswith(self.compiler.modDir):
			modPath = modPath[len(self.compiler.modDir):]
		
		return "#include <" + stripExt(modPath) + "-out.hpp>\n"
		
	def parseBinaryOperator(self, node, connector):
		op1 = self.parseExpr(node.childNodes[0])
		op2 = self.parseExpr(node.childNodes[1])
		
		if op2 == "self":
			op2 = "this"
		
		if op1 == "self":
			op1 = "this"
		
		if connector != " / ":
			return self.exprPrefix + op1 + connector + op2 + self.exprPostfix
		else:
			return self.exprPrefix + "float(" + op1 + ")" + connector + op2 + self.exprPostfix
		
	def getCombinationResult(self, operation, operatorType1, operatorType2):
		if operatorType1 in self.dataTypeWeights and operatorType2 in self.dataTypeWeights:
			if operation == "divide":
				dataType = self.heavierOperator(operatorType1, operatorType2)
				if dataType == "Double":
					return dataType
				else:
					return "Float"
			else:
				return self.heavierOperator(operatorType1, operatorType2)
		else:
			raise CompilerException("Could not find an operator for the operation: " + operation + " " + operatorType1 + " " + operatorType2)
		
	def heavierOperator(self, operatorType1, operatorType2):
		if operatorType1 is None:
			return operatorType2
		if operatorType2 is None:
			return operatorType1
		
		weight1 = self.dataTypeWeights[operatorType1]
		weight2 = self.dataTypeWeights[operatorType2]
		
		if weight1 > weight2:
			return operatorType1
		else:
			return operatorType2
		
	def getExprDataType(self, node):
		if isTextNode(node):
			if node.nodeValue.isdigit():
				return "Int"
			elif node.nodeValue.replace(".", "").isdigit():
				return "Float"
			elif node.nodeValue.startswith("bp_string_"):
				return "String"
			else:
				return self.getVariableTypeAnywhere(node.nodeValue)
		else:
			# Binary operators
			if node.tagName == "new":
				# TODO: Template based types
				return getElementByTagName(node, "type").childNodes[0].nodeValue
			elif node.tagName == "call":
				return self.getCallDataType(node)
			elif node.tagName == "access":
				callerType = self.getExprDataType(node.childNodes[0].childNodes[0])
				memberType = self.compiler.classes[callerType].members[node.childNodes[1].childNodes[0].nodeValue]
				
				return memberType
			elif len(node.childNodes) == 2:
				return self.getCombinationResult(node.tagName, self.getExprDataType(node.childNodes[0].childNodes[0]), self.getExprDataType(node.childNodes[1].childNodes[0]))
			
		raise CompilerException("Unknown data type for: " + node.toxml())
		
	def getCallDataType(self, node):
		caller, callerType, funcName = self.getCallFunction(node)
		params = getElementByTagName(node, "parameters")
		
		paramsString, paramTypes = self.handleParameters(params)
		
		if not funcName.startswith("bp_"):
			funcName += self.buildCallPostfix(paramTypes)
		
		if not (callerType + "::" + funcName) in self.compiler.functionTypes:
			raise CompilerException("Function '" + funcName + "' has not been defined")
		
		return self.compiler.functionTypes[callerType + "::" + funcName]
		
	def variableExistsAnywhere(self, name):
		if self.variableExists(name) or (name in self.compiler.globalScope.variables):
			return 1
		
		return 0
	
	def getVariableTypeAnywhere(self, name):
		var = self.getVariable(name)
		if var:
			return var.type
		
		if name in self.compiler.globalScope.variables:
			return self.compiler.globalScope.variables[name].type
		
		raise CompilerException("Unknown variable: " + name)
	
	def getVariableScopeAnywhere(self, name):
		scope = self.getVariableScope(name)
		if scope:
			return scope
		
		if name in self.compiler.globalScope.variables:
			return self.compiler.globalScope
		
		raise CompilerException("Unknown variable: " + name)
		
	def getCode(self):
		for classObj in self.classes.values():
			if classObj.name != "":
				code = ""
				
				# Members
				for memberName, memberType in classObj.members.items():
					code += "\t" + memberType + " " + memberName + ";\n"
				
				code += "\t\n"
				
				# Functions
				for func in classObj.functions.values():
					for impl in func.implementations.values():
						code += "\t" + impl + "\n"
				prefix = "BP"
				
				self.typeDefsHeader += "class " + prefix + classObj.name + ";\ntypedef " + prefix + classObj.name + "* " + classObj.name + ";\n"
				self.classesHeader += "class " + prefix + classObj.name + " {\npublic:\n" + code + "};\n"
		
		return self.header + self.typeDefsHeader + self.prototypesHeader + self.varsHeader + self.functionsHeader + self.classesHeader + "\n" + self.topLevel + "\n" + self.footer