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
# Global
####################################################################
pointerType = "boost::shared_ptr"

dataTypeWeights = {
	"Bool" : 1,
	"Byte" : 2,
	"Short" : 3,
	"Int" : 4,
	"Float" : 5,
	"Double" : 6
}

nonPointerClasses = {
	"Bool" : 1,
	"Byte" : 2,
	"Short" : 3,
	"Int" : 4,
	"Float" : 5,
	"Double" : 6,
	"String" : 7
}

####################################################################
# Classes
####################################################################
class CPPClass:
	
	def __init__(self, name, cppFile):
		self.name = name
		self.cppFile = cppFile
		self.functions = {}
		self.members = {}
		self.templateParams = []
		
	def mapTemplateParams(self, params):
		paramMap = {}
		paramsList = params.split(', ')
		for i in range(len(paramsList)):
			param = paramsList[i]
#			paramClass = removeGenerics(param)
#			pointer = ""
#			if not paramClass in nonPointerClasses:
#				paramClass = "BP" + paramClass
#				pointer = "*"
			paramMap[self.templateParams[i]] = param #+ pointer
		return paramMap
		
	def setTemplateParams(self, nList):
		self.templateParams = nList

class CPPVariable:
	
	def __init__(self, name, type, value, isConst, isPointer):
		self.name = name
		self.type = type
		self.value = value
		self.isConst = isConst
		self.isPointer = isPointer
	
	def getFullPrototype(self):
		return adjustDataType(self.type) + " " + self.name
		
class CPPFunction:
	
	def __init__(self, file, node):
		self.file = file
		self.node = node
		self.returnTypes = []
		self.implementations = {}
		
	def getName(self):
		return getElementByTagName(self.node, "name").childNodes[0].nodeValue

class FunctionImplRequest:
	
	def __init__(self, name, paramTypes):
		self.name = name
		self.paramTypes = paramTypes
		self.implementation = ""
		
	def buildPostfix(self):
		postfix = ""
		for dataType in self.paramTypes:
			postfix += "__" + dataType.replace("<", "_").replace(">", "_")
		return postfix
		
	def getName(self):
		return self.name
		
	def getPrototype(self):
		return self.name + self.buildPostfix() + "(" + ", ".join(self.paramTypes) + ")"
	
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
		self.libsDir = fixPath(os.path.abspath(inpCompiler.modDir + "../libs/"))
		self.stringCounter = 0;
		self.fileCounter = 0;
		self.outputDir = ""
		self.mainFile = None
		self.mainCppFile = ""
		self.globalScope = Scope()
		self.implementationRequests = {}
		self.functionTypes = {}
		
		self.classes = {}
		self.classes[""] = CPPClass("", None)
	
	def compile(self, inpFile):
		cppOut = CPPOutputFile(self, inpFile)
		
		if len(self.compiledFiles) == 0:
			self.mainFile = cppOut
		
		# This needs to be executed BEFORE the imported files have been compiled
		# It'll prevent a file from being processed twice
		self.compiledFiles[inpFile] = cppOut
		
		# Import files
		for imp in inpFile.importedFiles:
			inFile = self.inputCompiler.getFileInstanceByPath(imp)
			if (not inFile in self.compiledFiles):
				self.compile(inFile)
		
		# This needs to be executed AFTER the imported files have been compiled
		# It'll make sure the files are called in the correct (recursive) order
		self.compiledFilesList.append(cppOut)
		
		# After the dependencies have been compiled, compile itself
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
				self.mainCppFile = fileOut
				
				# Write main file
				with open(fileOut, "w") as outStream:
					outStream.write("#include <bp_decls.hpp>\n#include \"" + hppFile + "\"\n\nint main(int argc, char *argv[]) {\n" + self.getFileExecList() + "\treturn 0;\n}\n")
		
		# Decls file
		fileOut = dirOut + "bp_decls.hpp"
		with open(fileOut, "w") as outStream:
			outStream.write("#ifndef " + "bp__decls__hpp" + "\n#define " + "bp__decls__hpp" + "\n\n")
			
			# Basic data types
			for dataType in dataTypeWeights.keys():
				if dataType == "Byte":
					cDataType = "char"
				else:
					cDataType = dataType.lower()
				
				outStream.write("typedef %s %s;\n" % (cDataType, dataType))
			outStream.write("typedef %s %s;\n" % ("const char*", "String"))
			outStream.write("\n")
			
			for className, classObj in self.classes.items():
				if className:
					if classObj.templateParams:
						outStream.write("template <typename %s> " % (", typename ".join(classObj.templateParams)))
					outStream.write("class BP" + className + ";\n//typedef BP" + className + "* " + className + ";\n\n")
			
			for req in self.implementationRequests.values():
				protoType = req.getPrototype()
				if protoType.startswith("::"):
					protoType = protoType[2:]
					reqName = req.getName()
					funcType = self.functionTypes[reqName + req.buildPostfix()]
					outStream.write("inline " + funcType + " " + protoType + ";\n")
					
			outStream.write("\n#endif\n")
	
	def build(self):
		exe = stripExt(self.mainCppFile)
		if os.path.isfile(exe):
			os.unlink(exe)
		
		cmd = ["g++", self.mainCppFile, "-o", exe, "-I" + self.outputDir, "-I" + self.modDir, "-L" + self.libsDir, "-O3"]
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
		self.currentFunction = None
		
		self.inConst = False
		self.inClass = False
		self.inFunction = False
		
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
		
		#self.header += "\n#define String const char *\n"
		
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
				self.varsHeader += "const " + var.getFullPrototype() + " = " + var.value + ";\n";
			else:
				self.varsHeader += var.getFullPrototype() + ";\n";
		
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
		elif tagName == "for":
			return self.handleFor(node)
		elif tagName == "include":
			self.header += "#include \"" + node.childNodes[0].nodeValue + "\"\n"
			return ""
		elif tagName == "const":
			return self.handleConst(node)
		elif tagName == "break":
			return "break"
		elif tagName == "continue":
			return "continue"
		elif tagName == "template":
			return self.handleTemplate(node)
		elif node.tagName == "template-call":
			return self.handleTemplateCall(node)
		elif node.tagName == "declare-type":
			return self.handleTypeDeclaration(node)
		elif tagName == "noop":
			return ""
		
		# Check parameterized blocks
		if tagName in self.paramBlocks:
			paramBlock = self.paramBlocks[node.tagName]
			keywordName = paramBlock[0]
			paramTagName = paramBlock[1]
			codeTagName = paramBlock[2]
			
			condition = self.parseExpr(getElementByTagName(node, paramTagName).childNodes[0])
			
			if condition != "0":
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
		
	def handleTypeDeclaration(self, node):
		typeName = self.parseExpr(node.childNodes[1])
		varName = self.parseExpr(node.childNodes[0])
		
		if varName.startswith("this->"):
			varName = varName[len("this->"):]
			self.currentClass.members[varName] = typeName
			return ""
		
		if self.variableExistsAnywhere(varName):
			raise CompilerException("'" + varName + "' has already been defined.")
		else:
			# TODO: Non-member type declaration
			pass
			
		return ""
		
	def handleTemplate(self, node):
		self.currentClass.setTemplateParams(self.getParameterList(node))
		
	def handleTemplateCall(self, node):
		op1 = self.parseExpr(node.childNodes[0])
		op2 = self.parseExpr(node.childNodes[1])
		
		return op1 + "<" + op2 + ">"
		
	def handleAccess(self, node):
		return self.parseBinaryOperator(node, "->")
		
	def handleConst(self, node):
		self.inConst = True
		expr = self.handleAssign(node.childNodes[0])
		self.inConst = False
		
		return expr
		
	def registerVariable(self, var):
		#print("Registered variable '" + var.name + "' of type '" + var.type + "'")
		self.getCurrentScope().variables[var.name] = var
		if self.getCurrentScope() == self.getTopLevelScope():
			self.compiler.globalScope.variables[var.name] = var
		
	def handleAssign(self, node):
		variable = self.parseExpr(node.childNodes[0])
		value = self.parseExpr(node.childNodes[1])
		valueTypeOriginal = self.getExprDataType(node.childNodes[1].childNodes[0])
		
		if variable.startswith("this->"):
			variable = variable[len("this->"):]
			
			if not variable in self.currentClass.members:
				self.currentClass.members[variable] = valueTypeOriginal
		
		variableExisted = self.variableExistsAnywhere(variable)
		
		if not variableExisted:
			var = CPPVariable(variable, valueTypeOriginal, value, self.inConst, not valueTypeOriginal in nonPointerClasses)
			self.registerVariable(var)
				
			if self.inConst:
				if self.getCurrentScope() == self.getTopLevelScope():
					return ""
				else:
					return "const %s = %s" % (var.getFullPrototype(), value)
			
			#print(variable + " = " + valueTypeOriginal)
			
		if variableExisted or self.getCurrentScope() == self.getTopLevelScope():
			return variable + " = " + value
		else:
			return var.getFullPrototype() + " = " + value
		
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
			postfix += "__" + dataType.replace("<", "_").replace(">", "_")
		return postfix
		
	def handleReturn(self, node):
		expr = self.parseExpr(node.childNodes[0])
		self.currentFunction.returnTypes.append(self.getExprDataType(node.childNodes[0]))
		return "return " + expr
		
	def handleNew(self, node):
		typeName = self.parseExpr(getElementByTagName(node, "type").childNodes[0])
		params = getElementByTagName(node, "parameters")
		
		# Template params
		className = ""
		pos = typeName.find("<")
		if pos != -1:
			className = typeName[:pos]
		else:
			className = typeName
		
		paramsString, paramTypes = self.handleParameters(params)
		
		oldClass = self.currentClass
		self.currentClass = self.compiler.classes[className]
		
		# Implement init
		funcName = "init"
		func = self.currentClass.functions[funcName]
		
		self.inClass = True
		
		func.implementations[self.buildCallPostfix(paramTypes)] = self.implementFunction(func.node, paramTypes, "\t")
		
		self.inClass = False
		self.currentClass = oldClass
		
		finalTypeName = adjustDataType(typeName, False)
		return pointerType + "< " + finalTypeName + " >(new " + finalTypeName + "(" + paramsString + "))"
		
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
		callerClass = removeGenerics(callerType)
		
		params = getElementByTagName(node, "parameters")
		
		paramsString, paramTypes = self.handleParameters(params)
		implRequest = FunctionImplRequest(callerType + "::" + funcName, paramTypes)
		
		fullName = funcName + self.buildCallPostfix(paramTypes)
		
		if not funcName.startswith("bp_"):
			if not implRequest.getPrototype() in self.compiler.implementationRequests:
				self.compiler.implementationRequests[implRequest.getPrototype()] = implRequest
				#print("Requested implementation of " + implRequest.getPrototype())
				
				if funcName in self.compiler.classes[callerClass].functions:
					func = self.compiler.classes[callerClass].functions[funcName]
				else:
					raise CompilerException("Function '" + funcName + "' has not been defined")
				
				self.oldClass = self.currentClass
				self.currentClass = self.compiler.classes[callerClass]
				
				oldFunction = self.currentFunction
				self.currentFunction = self.currentClass.functions[funcName]
				
				if callerType:
					definedInFile = self.currentClass.cppFile
					definedInFile.currentClass = self.currentClass
					definedInFile.currentFunction = self.currentFunction
					implementation = definedInFile.implementFunction(func.node, implRequest.paramTypes)
					self.currentFunction.implementations[self.buildCallPostfix(paramTypes)] = implementation
				else:
					definedInFile = func.file
					definedInFile.currentFunction = self.currentFunction
					implementation = definedInFile.implementFunction(func.node, implRequest.paramTypes)
					definedInFile.functionsHeader += implementation
					
					prototype = "inline " + self.compiler.functionTypes[callerType + "::" + fullName] + " " + fullName + "(" + ", ".join(paramTypes) + ");\n"
					self.prototypesHeader += prototype
					
					#if self.oldClass.cppFile != self:
					#	self.oldClass.cppFile.prototypesHeader += prototype
						#self.oldClass.cppFile.functionsHeader += implementation
				self.currentFunction = oldFunction
				self.currentClass = self.oldClass
			
			if callerClass in nonPointerClasses:
				return ["", caller + "."][caller != ""] + fullName + "(" + paramsString + ")"
			else:
				return ["", caller + "->"][caller != ""] + fullName + "(" + paramsString + ")"
		else:
			return funcName + "(" + paramsString + ")"
		
	def implementFunction(self, node, types, tabLevel = ""):
		origName = name = getElementByTagName(node, "name").childNodes[0].nodeValue
		self.currentFunction = self.currentClass.functions[name]
		
		#if self.inClass:
		#	tabLevel *= self.currentTabLevel
		tabLevel = "\t" * self.currentTabLevel
		
		self.pushScope()
		self.getCurrentScope().variables["self"] = CPPVariable("self", self.currentClass.name, "", False, True)
		
		# Add class variables to scope
		for memberName, memberType in self.currentClass.members.items():
			self.getCurrentScope().variables[memberName] = CPPVariable(memberName, memberType, "", False, (not memberType in nonPointerClasses))
		
		self.inFunction = True
		self.currentFunction.returnTypes = []
		
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
		
		for type in self.currentFunction.returnTypes:
			if type in dataTypeWeights:
				heaviest = self.heavierOperator(heaviest, type)
			else:
				return type
		
		if heaviest:
			return heaviest
		else:
			return "void"
		
	def handleFor(self, node):
		fromNodeContent = getElementByTagName(node, "from").childNodes[0]
		fromType = self.getExprDataType(fromNodeContent)
		
		iterExpr = self.parseExpr(getElementByTagName(node, "iterator").childNodes[0])
		fromExpr = self.parseExpr(fromNodeContent)
		toExpr = self.parseExpr(getElementByTagName(node, "to").childNodes[0])
		#stepExpr = self.parseExpr(getElementByTagName(node, "step").childNodes[0])
		
		self.pushScope()
		var = CPPVariable(iterExpr, fromType, fromExpr, False)
		typeInit = ""
		if not self.variableExistsAnywhere(iterExpr):
			self.getCurrentScope().variables[iterExpr] = var
			typeInit = fromType + " "
		code = self.parseChilds(getElementByTagName(node, "code"), "\t" * self.currentTabLevel, ";\n")
		self.popScope()
		
		return "for(%s%s = %s; %s <= %s; ++%s) {\n%s%s}" % (typeInit, iterExpr, fromExpr, iterExpr, toExpr, iterExpr, code, "\t" * self.currentTabLevel)
		
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
		self.getTopLevelScope().variables[id] = CPPVariable(id, "String", value, False, False)
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
			pList += adjustDataType(types[counter]) + " " + name + ", "
			self.getCurrentScope().variables[name] = CPPVariable(name, types[counter], "", False, not types[counter] in nonPointerClasses)
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
		if operatorType1 in dataTypeWeights and operatorType2 in dataTypeWeights:
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
		
		weight1 = dataTypeWeights[operatorType1]
		weight2 = dataTypeWeights[operatorType2]
		
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
				typeNode = getElementByTagName(node, "type").childNodes[0]
				
				if isTextNode(typeNode):
					return typeNode.nodeValue
				else:
					# Template parameters
					return self.parseExpr(typeNode)
					#return typeNode.childNodes[0].childNodes[0].nodeValue
			elif node.tagName == "call":
				if self.inFunction:
					# Recursive functions: Try to guess
					if self.currentFunction and getElementByTagName(node, "function").childNodes[0].nodeValue == self.currentFunction.getName():
						if self.currentFunction.returnTypes:
							return self.currentFunction.returnTypes[0]
						else:
							raise CompilerException("Unknown data type for recursive call: " + self.currentFunction.getName())
						
				return self.getCallDataType(node)
			elif node.tagName == "access":
				callerType = self.getExprDataType(node.childNodes[0].childNodes[0])
				memberType = self.compiler.classes[callerType].members[node.childNodes[1].childNodes[0].nodeValue]
				
				return memberType
			elif len(node.childNodes) == 2:
				op1 = node.childNodes[0].childNodes[0]
				op2 = node.childNodes[1].childNodes[0]
				
				if self.inFunction and self.currentFunction:
					# Recursive functions: Try to guess
					if tagName(op2) == "call" and getElementByTagName(op2, "function").childNodes[0].nodeValue == self.currentFunction.getName():
						if self.currentFunction.returnTypes:
							return self.currentFunction.returnTypes[0]
						else:
							return self.getExprDataType(op1)
					elif tagName(op1) == "call" and getElementByTagName(op1, "function").childNodes[0].nodeValue == self.currentFunction.getName():
						if self.currentFunction.returnTypes:
							return self.currentFunction.returnTypes[0]
						else:
							return self.getExprDataType(op2)
				
				return self.getCombinationResult(node.tagName, self.getExprDataType(op1), self.getExprDataType(op2))
			
		raise CompilerException("Unknown data type for: " + node.toxml())
		
	def getCallDataType(self, node):
		caller, callerType, funcName = self.getCallFunction(node)
		params = getElementByTagName(node, "parameters")
		
		paramsString, paramTypes = self.handleParameters(params)
		
		if not funcName.startswith("bp_"):
			funcName += self.buildCallPostfix(paramTypes)
			
			callerClassName = removeGenerics(callerType)
			
			templatesUsed = 0
			if callerClassName != callerType:
				templatesUsed = 1
				callerClass = self.compiler.classes[callerClassName]
				templateParams = callerType[len(callerClassName) + 1: -1]
				translateTemplateParams = callerClass.mapTemplateParams(templateParams)
			
			if not (callerClassName + "::" + funcName) in self.compiler.functionTypes:
				raise CompilerException("Function '" + (callerClassName + "::" + funcName) + "' has not been defined")
			
			if templatesUsed:
				return translateTemplateParams[self.compiler.functionTypes[callerClassName + "::" + funcName]]
			else:
				return self.compiler.functionTypes[callerClassName + "::" + funcName]
		else:
			if not (funcName) in self.compiler.functionTypes:
				raise CompilerException("Function '" + funcName + "' has not been defined")
			
			return self.compiler.functionTypes[funcName]
	
	def getVariableTypeAnywhere(self, name):
		var = self.getVariable(name)
		if var:
			return var.type
		
		if name in self.compiler.globalScope.variables:
			return self.compiler.globalScope.variables[name].type
		
		#print(self.getTopLevelScope().variables)
		#print(self.compiler.globalScope.variables)
		if name in self.compiler.classes:
			raise CompilerException("You forgot to create an instance of the class '" + name + "' by using brackets")
		raise CompilerException("Unknown variable: " + name)
	
	def getVariableScopeAnywhere(self, name):
		scope = self.getVariableScope(name)
		if scope:
			return scope
		
		if name in self.compiler.globalScope.variables:
			return self.compiler.globalScope
		
		raise CompilerException("Unknown variable: " + name)
		
	def variableExistsAnywhere(self, name):
		if self.variableExists(name) or (name in self.compiler.globalScope.variables) or (name in self.currentClass.members):
			#print(name + " exists")
			return 1
		#print(name + " doesn't exist")
		return 0
		
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
				
				code += "~" + prefix + classObj.name + "() {bp_print(\"Destructed " + classObj.name + "\");}"
				code += "\n"
				
				#self.typeDefsHeader += "class " + prefix + classObj.name + ";\ntypedef " + prefix + classObj.name + "* " + classObj.name + ";\n"
				if classObj.templateParams:
					self.classesHeader += "template <typename %s>\n" % (", typename ".join(classObj.templateParams))
				self.classesHeader += "class " + prefix + classObj.name + " {\npublic:\n" + code + "};\n"
		
		return self.header + self.typeDefsHeader + self.prototypesHeader + self.varsHeader + self.classesHeader + self.functionsHeader + "\n" + self.topLevel + "\n" + self.footer

####################################################################
# Functions
####################################################################
def adjustDataType(type, adjustOuterAsWell = True):
	# Adjust template params
	pos = type.find('<')
	postFixCount = 0
	typeName = ""
	className = ""
	standardClassPrefix = "BP"
	
	classPrefix = pointerType + "<" + standardClassPrefix
	classPostfix = ">"
	
	if adjustOuterAsWell:
		if pos != -1:
			className = type[:pos]
		else:
			className = type
			
		if not className in nonPointerClasses:
			pos += len(classPrefix)
			postFixCount += len(classPostfix)
			type = classPrefix + type + classPostfix
	else:
		type = standardClassPrefix + type
	
	while 1:
		pos = type.find('<', pos)
		if pos == -1:
			break
		postFixCount += 1
		typeName = type[pos+1:-postFixCount]
		className = removeGenerics(typeName)
		
		if className in nonPointerClasses:
			pos += 1
		else:
			type = type[:pos+1] + classPrefix + type[pos+1:-postFixCount] + classPostfix + type[-postFixCount:]
			
			# Because of the postfix pointer sign
			postFixCount += 1
			
			# Because of the prefixes
			pos += len(classPrefix) + len(classPostfix) + 1
	
	return type.replace("<", "< ").replace(">", " >")