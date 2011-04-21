####################################################################
# Header
####################################################################
# Target:   C++ Code
# Author:   Eduard Urbach

####################################################################
# License
####################################################################
# (C) 2011  Eduard Urbach
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
from Output.cpp.datatypes import *
from Output.cpp.CPPClass import *

####################################################################
# Classes
####################################################################
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
		self.localClasses = []
		self.localFunctions = []
		
		# XML tag : C++ keyword, condition tag name, code tag name
		self.paramBlocks = {
			"if" : ["if", "condition", "code"],
			"else-if" : [" else if", "condition", "code"],
			"while" : ["while", "condition", "code"]
		}
		
		# Inserted for mathematical expressions
		self.exprPrefix = ""
		self.exprPostfix = ""
		
		# Increment id
		self.compiler.fileCounter += 1
		self.id = "file_" + str(self.compiler.fileCounter)
		
		# Current
		self.currentClass = self.compiler.mainClass
		self.currentClassImpl = self.currentClass.requestImplementation("")
		self.currentFunction = None
		self.currentFunctionImpl = None
		
		# State
		self.inExtern = 0
		self.inGetter = 0
		self.inSetter = 0
		self.inTemplate = 0
		self.inAssignment = 0
		self.inConst = 0
		self.inUnmanaged = 0
		self.inOperators = 0
		self.inOperator = 0
		self.inTypeDeclaration = 0
		self.inFunction = 0
		
		# Codes
		self.header = "#ifndef " + self.id + "\n#define " + self.id + "\n\n"
		self.body = ""
		self.footer = "#endif\n"
		
		# Other code types
		self.stringsHeader = "\t// Strings\n";
		self.varsHeader = ""
		self.functionsHeader = "// Functions\n"
		self.classesHeader = ""
		self.actorClassesHeader = ""
		self.prototypesHeader = "\n// Prototypes\n"
		
	def compile(self):
		print("Output: " + self.file)
		
		# Find classes, functions, operators and external stuff
		self.scanAhead(self.codeNode)
		
		# Header
		self.header += "// Includes\n";
		for node in self.dependencies.childNodes:
			self.header += self.handleImport(node)
		
		# Strings
		for node in self.strings.childNodes:
			self.stringsHeader += "\t" + self.handleString(node)
		self.stringsHeader += "\n"
		
		# Top level code
		self.body += "// Module execution\n"
		self.body += "void exec_" + self.id + "() {\n"
		self.body += self.stringsHeader
		self.body += "\t// Code\n"
		self.body += self.parseChilds(self.codeNode, "\t" * self.currentTabLevel, ";\n")
		self.body += "}\n"
		
		# Variables
		self.varsHeader = "\n// Variables\n";
		for var in self.getTopLevelScope().variables.values():
			if var.isConst:
				self.varsHeader += "const " + var.getPrototype() + " = " + var.value + ";\n";
			else:
				self.varsHeader += var.getPrototype() + ";\n";
		self.varsHeader += "\n"
		
	def getParameterList(self, pNode):
		pList = []
		pTypes = []
		for node in pNode.childNodes:
			name = ""
			type = ""
			exprNode = node.childNodes[0]
			if isTextNode(exprNode):
				name = exprNode.nodeValue
			elif exprNode.tagName == "access":
				name = "__" + exprNode.childNodes[1].childNodes[0].nodeValue
			elif exprNode.tagName == "assign":
				name = self.parseExpr(exprNode.childNodes[0].childNodes[0])
			elif exprNode.tagName == "declare-type":
				name = self.parseExpr(exprNode.childNodes[0].childNodes[0])
				type = self.parseExpr(exprNode.childNodes[1].childNodes[0])
			else:
				raise CompilerException("Invalid parameter %s" % (exprNode.toxml()))
			pList.append(name)
			pTypes.append(type)
		return pList, pTypes
	
	def parseChilds(self, parent, prefix = "", postfix = ""):
		lines = ""
		for node in parent.childNodes:
			line = self.parseExpr(node)
			if line:
				lines += prefix + line + postfix
		return lines
	
	def parseExpr(self, node):
		# Return text nodes directly (if it is not a string)
		if isTextNode(node):
			if node.nodeValue.startswith("bp_string_"):
				return self.id + "_" + node.nodeValue
			else:
				if node.nodeValue == "self":
					return "this"
				else:
					return node.nodeValue
		
		tagName = node.tagName
		
		# Check which kind of tag it is
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
		elif tagName == "parameters":
			return self.parseChilds(node, "", ", ")[:-2]
		elif tagName == "parameter":
			return self.parseExpr(node.childNodes[0])
		elif tagName == "index":
			caller = self.parseExpr(node.childNodes[0].childNodes[0])
			callerType = self.getExprDataType(node.childNodes[0].childNodes[0])
			index = self.parseExpr(node.childNodes[1].childNodes[0])
			callerClassName = extractClassName(callerType)
			
			if callerClassName == "MemPointer" and isUnmanaged(callerType):
				return "%s[%s]" % (caller, index)
			
			memberFunc = "[]"
			virtualIndexCall = parseString("<call><operator><access><value>%s</value><value>%s</value></access></operator><parameters><parameter>%s</parameter></parameters></call>" % (node.childNodes[0].childNodes[0].toxml(), memberFunc, node.childNodes[1].childNodes[0].toxml())).documentElement
			
			return self.handleCall(virtualIndexCall)
		elif tagName == "class":
			return ""
		elif tagName == "function" or tagName == "operator":
			return ""
		elif tagName == "extern":
			return ""
		elif tagName == "operators":
			return ""
		elif tagName == "extern-function":
			return ""
		elif tagName == "template":
			return ""
		elif tagName == "target":
			return self.handleTarget(node)
		elif tagName == "new":
			return self.handleNew(node)
		elif tagName == "return":
			return self.handleReturn(node)
		elif tagName == "for":
			return self.handleFor(node)
		elif tagName == "include":
			fileName = node.childNodes[0].nodeValue
			self.compiler.includes.append((self.dir + fileName)[len(self.compiler.modDir):]) #+= "#include \"" + node.childNodes[0].nodeValue + "\"\n"
			return ""
		elif tagName == "const":
			return self.handleConst(node)
		elif tagName == "break":
			return "break"
		elif tagName == "continue":
			return "continue"
		elif tagName == "get" or tagName == "set":
			return ""
		elif node.tagName == "template-call":
			return self.handleTemplateCall(node)
		elif node.tagName == "declare-type":
			return self.handleTypeDeclaration(node)
		elif node.tagName == "unmanaged":
			return self.handleUnmanaged(node)
		elif node.tagName == "compiler-flags":
			return self.parseChilds(node, "", "")
		elif node.tagName == "compiler-flag":
			return self.handleCompilerFlag(node)
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
							return self.parseBinaryOperator(node, " / ", True)
						return self.parseBinaryOperator(node, " " + op.text + " ", True)
					elif op.type == Operator.UNARY:
						return op.text + "(" + self.parseExpr(node.childNodes[0]) + ")"
		
		return ""
	
	def handleParameters(self, pNode):
		pList = ""
		pTypes = []
		for node in pNode.childNodes:
			paramType = self.getExprDataType(node.childNodes[0])
			#paramType = self.translateTemplateParam(paramType)
			pList += self.parseExpr(node.childNodes[0]) + ", "
			pTypes.append(paramType)
		
		return pList[:len(pList)-2], pTypes
	
	def handleAccess(self, node):
		op1 = node.childNodes[0].childNodes[0]
		op2 = node.childNodes[1].childNodes[0]
		
		callerType = self.getExprDataType(op1)
		callerClassName = extractClassName(callerType)
		
		if callerClassName in self.compiler.mainClass.classes:
			if callerClassName == "MemPointer" and isTextNode(op2) and isUnmanaged(callerType):
				if op2.nodeValue == "data":
					return "(*%s)" % (self.parseExpr(op1))
			# TODO: Optimize
			# GET access
			isMemberAccess = self.isMemberAccessFromOutside(op1, op2)
			if isMemberAccess:
				#print("Replacing ACCESS with CALL: %s.%s" % (op1.toxml(), "get" + op2.nodeValue.title()))
				#if isTextNode(op1) and op1.nodeValue == "self":
				#	op1xml = "this"
				#else:
				op1xml = op1.toxml()
				
				getFunc = parseString("<call><function><access><value>%s</value><value>%s</value></access></function><parameters/></call>" % (op1xml, "get" + op2.nodeValue.title())).documentElement
				#print(getFunc.toprettyxml())
				return self.handleCall(getFunc)
		
		return self.parseBinaryOperator(node, "->")
	
	def handleNew(self, node):
		typeName = self.parseExpr(getElementByTagName(node, "type").childNodes[0])
		paramsNode = getElementByTagName(node, "parameters")
		paramsString, paramTypes = self.handleParameters(paramsNode)
		
		pos = typeName.find("<")
		if pos != -1:
			className = removeUnmanaged(typeName[:pos])
			
			# Actor
			if className == "Actor":
				actorBoundClass = extractClassName(typeName[pos+1:-1])
				self.compiler.mainClass.classes[actorBoundClass].usesActorModel = True
			elif className == "MemPointer":
				ptrType = typeName[pos+1:-1]
				if len(paramsNode.childNodes) > 1:
					raise CompilerException("Too many parameters for the MemPointer constructor (only size needed)")
				
				paramsString, paramTypes = self.handleParameters(paramsNode)
				
				#if ptrType in self.currentTemplateParams:
				#	ptrType = self.currentTemplateParams[ptrType]
				
				ptrType = self.currentClassImpl.translateTemplateName(ptrType)
				ptrType = adjustDataType(ptrType, True);
				return "new %s[%s]" % (ptrType, paramsString)
		
		self.implementFunction(typeName, "init", paramTypes)
		
		finalTypeName = adjustDataType(typeName, False)
		
		if self.inUnmanaged:
			return finalTypeName + "(" + paramsString + ")"
		else:
			return pointerType + "< " + finalTypeName + " >(new " + finalTypeName + "(" + paramsString + "))"
		
	def handleAssign(self, node):
		self.inAssignment += 1
		isSelfMemberAccess = False
		
		# Member access (setter)
		op1 = node.childNodes[0].childNodes[0]
		if not isTextNode(op1):
			if op1.tagName == "access":
				accessOp1 = op1.childNodes[0].childNodes[0]
				accessOp2 = op1.childNodes[1].childNodes[0]
				
				# data access from a pointer
				accessOp1Type = self.getExprDataType(accessOp1)
				if extractClassName(accessOp1Type) == "MemPointer" and accessOp2.nodeValue == "data" and isUnmanaged(accessOp1Type):
					return "*" + self.parseExpr(accessOp1) + " = " + self.parseExpr(node.childNodes[1])
				
				isMemberAccess = self.isMemberAccessFromOutside(accessOp1, accessOp2)
				if isMemberAccess:
					#print("Using setter for type '%s'" % (accessOp1type))
					setFunc = parseString("<call><function><access><value>%s</value><value>%s</value></access></function><parameters><parameter>%s</parameter></parameters></call>" % (accessOp1.toxml(), "set" + accessOp2.nodeValue.title(), node.childNodes[1].childNodes[0].toxml())).documentElement
					return self.handleCall(setFunc)
				#pass
				#variableType = self.getExprDataType(op1)
				#variableClass = self.compiler.classes[removeGenerics(variableType)]
			elif op1.tagName == "index":
				return self.parseExpr(node.childNodes[0]) + " = " + self.parseExpr(node.childNodes[1])
		
		variableName = self.parseExpr(node.childNodes[0].childNodes[0])
		value = self.parseExpr(node.childNodes[1].childNodes[0])
		valueType = self.getExprDataType(node.childNodes[1].childNodes[0])
		memberName = variableName
		
		if variableName.startswith("this->"):
			memberName = variableName[len("this->"):]
			isSelfMemberAccess = True
		
		if isSelfMemberAccess:
			var = CPPVariable(memberName, valueType, value, self.inConst, not valueType in nonPointerClasses, False)
			#if not variableName in self.currentClass.members:
			#	self.currentClass.addMember(var)
			
			if not memberName in self.currentClassImpl.members:
				self.currentClassImpl.addMember(var)
			
			variableExisted = True
		else:
			variableExisted = self.variableExistsAnywhere(variableName)
		
		if not variableExisted:
			var = CPPVariable(variableName, valueType, value, self.inConst, not valueType in nonPointerClasses, False)
			self.registerVariable(var)
				
			if self.inConst:
				if self.getCurrentScope() == self.getTopLevelScope():
					return ""
				else:
					return "const %s = %s" % (var.getFullPrototype(), value)
		#else:
		#	var = self.getVariableTypeAnywhere(variableName)
		
		#if not variable in self.currentClassImpl.members:
		#	self.currentClassImpl.add
		
		self.inAssignment -= 1
		
		# Inline type declarations
		declaredInline = (tagName(node.childNodes[0].childNodes[0]) == "declare-type")
		
		if self.getCurrentScope() == self.getTopLevelScope():
			return variableName + " = " + value
		elif variableExisted:
			return variableName + " = " + value
		elif declaredInline:
			return variableName + " = " + value
		else:
			return var.getPrototype() + " = " + value
		
		return variableName + " = " + value
		
	def getClass(self, className):
		if className == "":
			return self.compiler.mainClass
		elif className in self.compiler.mainClass.classes:
			return self.compiler.mainClass.classes[className]
		else:
			raise CompilerException("Class '%s' has not been defined" % (className))
		
	def handleCall(self, node):
		caller, callerType, funcName = self.getFunctionCallInfo(node)
		
		params = getElementByTagName(node, "parameters")
		paramsString, paramTypes = self.handleParameters(params)
		
		callerClassName = extractClassName(callerType)
		callerClass = self.getClass(callerClassName)
		
		# MemPointer.free
		if funcName == "free" and callerClassName == "MemPointer":
			return "delete [] %s" % (caller)
		
		if not funcName.startswith("bp_"):
			if not funcName in callerClass.functions:
				if funcName[0].islower():
					raise CompilerException("Function '%s.%s' has not been defined" % (callerType, funcName))
				else:
					raise CompilerException("Class '%s' has not been defined" % (funcName))
			func = callerClass.functions[funcName]
			
			funcImpl = self.implementFunction(callerType, funcName, paramTypes)
			fullName = funcImpl.getName()
			
			if callerClass in nonPointerClasses:
				return ["::", caller + "."][caller != ""] + fullName + "(" + paramsString + ")"
			else:
				return ["::", caller + "->"][caller != ""] + fullName + "(" + paramsString + ")"
		else:
			return funcName + "(" + paramsString + ")"
		
	def getClassImplementationByTypeName(self, typeName):
		className = extractClassName(typeName)
		templateValues = extractTemplateValues(typeName)
		return self.getClass(className).requestImplementation(splitParams(templateValues))
		
	def implementFunction(self, typeName, funcName, paramTypes):
		key = typeName + "." + funcName + "(" + ", ".join(paramTypes) + ")"
		if key in self.compiler.funcImplCache:
			return self.compiler.funcImplCache[key]
		
		className = extractClassName(typeName)
		if not funcName in self.getClass(className).functions:
			raise CompilerException("The '%s' function of class '%s' has not been defined" % (funcName, className))
		func = self.getClass(className).getMatchingFunction(funcName, paramTypes)
		definedInFile = func.cppFile
		
		# Push
		oldFunc = definedInFile.currentFunction
		
		# Implement
		definedInFile.currentFunction = func
		funcImpl = definedInFile.implementLocalFunction(typeName, funcName, paramTypes)
		
		# Pop
		definedInFile.currentFunction = oldFunc
		
		if className == "":
			self.prototypesHeader += funcImpl.getPrototype()
		
		self.compiler.funcImplCache[key] = funcImpl
		return funcImpl
		
	def implementLocalFunction(self, typeName, funcName, paramTypes):
		className = extractClassName(typeName)
		
		# Save values
		oldGetter = self.inGetter
		oldSetter = self.inSetter
		oldOperator = self.inOperator
		oldImpl = self.currentClassImpl
		oldClass = self.currentClass
		oldFunction = self.currentFunction
		oldFunctionImpl = self.currentFunctionImpl
		self.inFunction += 1
		
		# Set new values
		self.currentClass = self.getClass(className)
		self.currentClassImpl = self.getClassImplementationByTypeName(typeName)
		
		node = self.currentFunction.node
		if node.tagName == "getter":
			self.inGetter += 1
		elif node.tagName == "setter":
			self.inSetter += 1
		elif node.tagName == "operator":
			self.inOperator += 1
		
		# Implement it
		funcImpl, codeExists = self.currentClassImpl.requestFuncImplementation(funcName, paramTypes)
		self.currentFunctionImpl = funcImpl
		
		if not codeExists:
			funcNode = funcImpl.func.node
			codeNode = getElementByTagName(funcNode, "code")
			
			self.pushScope()
			if typeName:
				self.getCurrentScope().variables["self"] = CPPVariable("self", typeName, "", False, True, False)
			parameters, funcStartCode = self.getParameterDefinitions(getElementByTagName(funcNode, "parameters"), paramTypes)
			
			funcImpl.setCode(funcStartCode + self.parseChilds(codeNode, "\t" * self.currentTabLevel, ";\n"))
			
			self.popScope()
		
		# Load previous values
		self.inFunction -= 1
		self.currentFunction = oldFunction
		self.currentFunctionImpl = oldFunctionImpl
		self.inGetter = oldGetter
		self.inSetter = oldSetter
		self.inOperator = oldOperator
		self.currentClass = oldClass
		self.currentClassImpl = oldImpl
		
		return funcImpl
		
	def getParameterDefinitions(self, pNode, types):
		pList = ""
		funcStartCode = ""
		counter = 0
		typesLen = len(types)
		
		for node in pNode.childNodes:
			#if isElemNode(node.childNodes[0]) and node.childNodes[0].tagName == "declare-type":
			#	name = node.childNodes[0].childNodes[0].childNodes[0].nodeValue
			#else:
			name = self.parseExpr(node.childNodes[0])
			
			# Not enough parameters
			if counter >= typesLen:
				raise CompilerException("You forgot to specify the parameter '%s' of the function '%s'" % (name, self.currentFunction.getName()))
			
			usedAs = types[counter]
			if name.startswith("this->"):
				member = name[len("this->"):]
				self.currentClassImpl.addMember(CPPVariable(member, usedAs, "", False, not usedAs in nonPointerClasses, False))
				name = "__" + member
				funcStartCode += "\t" * self.currentTabLevel + "this->" + member + " = " + name + ";\n"
			
			declaredInline = (tagName(node.childNodes[0]) == "declare-type")
			if not declaredInline:
				self.getCurrentScope().variables[name] = CPPVariable(name, usedAs, "", False, not usedAs in nonPointerClasses, False)
				pList += adjustDataType(usedAs) + " " + name + ", "
			else:
				definedAs = self.getVariableTypeAnywhere(name)
				pList += adjustDataType(definedAs) + " " + name + ", "
				
				if definedAs != usedAs:
					if definedAs in nonPointerClasses and usedAs in nonPointerClasses:
						heavier = getHeavierOperator(definedAs, usedAs)
						if usedAs == heavier:
							compilerWarning("Information might be lost by converting '%s' to '%s' for the parameter '%s' in the function '%s'" % (usedAs, definedAs, name, self.currentFunction.getName()))
					else:
						raise CompilerException("'%s' expects the type '%s' where you used the type '%s' for the parameter '%s'" % (self.currentFunction.getName(), definedAs, usedAs, name))
			
			counter += 1
		
		return pList[:len(pList)-2], funcStartCode
		
	def handleUnmanaged(self, node):
		self.inUnmanaged += 1
		expr = self.parseExpr(node.childNodes[0])
		self.inUnmanaged -= 1
		return expr
		
	def parseBinaryOperator(self, node, connector, checkPointer = False):
		op1 = self.parseExpr(node.childNodes[0].childNodes[0])
		op2 = self.parseExpr(node.childNodes[1].childNodes[0])
		
		if op2 == "self":
			op2 = "this"
		
		if op1 == "self":
			op1 = "this"
		
#		if checkPointer:
#			op1type = self.getExprDataType(node.childNodes[0].childNodes[0])
#			print("%s%s%s (%s)" % (op1, connector, op2, op1 + " is a '" + op1type + "'"))
#			if (not op1type in nonPointerClasses) and (not isUnmanaged(op1type)) and (not connector == " == "):
#				return self.exprPrefix + op1 + "->operator" + connector.replace(" ", "") + "(" + op2 + ")" + self.exprPostfix
		
		# Float conversion if needed
		if connector != " / ":
			return self.exprPrefix + op1 + connector + op2 + self.exprPostfix
		else:
			return self.exprPrefix + "float(" + op1 + ")" + connector + op2 + self.exprPostfix
		
	def getFunctionCallInfo(self, node):
		if getElementByTagName(node, "function"):
			funcNameNode = getElementByTagName(node, "function").childNodes[0]
		else:
			funcNameNode = getElementByTagName(node, "operator").childNodes[0]
		
		caller = ""
		callerType = ""
		if isTextNode(funcNameNode): #and funcNameNode.tagName == "access":
			funcName = funcNameNode.nodeValue
		else:
			#print("XML: " + funcNameNode.childNodes[0].childNodes[0].toxml())
			callerType = self.getExprDataType(funcNameNode.childNodes[0].childNodes[0])
			caller = self.parseExpr(funcNameNode.childNodes[0].childNodes[0])
			funcName = funcNameNode.childNodes[1].childNodes[0].nodeValue
			#print(callerType + "::" + funcName)
		
		return caller, callerType, correctOperators(funcName)
		
	def getCombinationResult(self, operation, operatorType1, operatorType2):
		if operatorType1 in dataTypeWeights and operatorType2 in dataTypeWeights:
			if operation == "divide":
				dataType = getHeavierOperator(operatorType1, operatorType2)
				if dataType == "Double":
					return dataType
				else:
					return "Float"
			elif operation == "less" or operation == "greater" or operation == "less-or-equal" or operation == "greater-or-equal":
				return "Bool"
			else:
				return getHeavierOperator(operatorType1, operatorType2)
		else:
			if operatorType1.startswith("~MemPointer"):
				if operation == "index":
					return operatorType1[len("~MemPointer<"):-1]
				if operatorType2.startswith("~MemPointer"):
					if operation == "subtract":
						return "Size"
				if operation == "add":
					return operatorType1
				return self.getCombinationResult(operation, "Size", operatorType2)
			if operatorType2.startswith("~MemPointer"):
				return self.getCombinationResult(operation, operatorType1, "Size")
			
			# TODO: Remove temporary fix
			if operation == "index" and operatorType1.startswith("Array<"):
				return operatorType1[len("Array<"):-1]
			
			raise CompilerException("Could not find an operator for the operation: " + operation + " " + operatorType1 + " " + operatorType2)
		
	def scanAhead(self, parent):
		for node in parent.childNodes:
			if isElemNode(node):
				if node.tagName == "class":
					self.scanClass(node)
				elif node.tagName == "function" or node.tagName == "operator":
					self.scanFunction(node)
				elif node.tagName == "getter":
					self.inGetter += 1
					result = self.scanFunction(node)
					self.inGetter -= 1
				elif node.tagName == "setter":
					self.inSetter += 1
					result = self.scanFunction(node)
					self.inSetter -= 1
				elif node.tagName == "extern":
					self.inExtern += 1
					self.scanAhead(node)
					self.inExtern -= 1
				elif node.tagName == "operators":
					self.inOperators += 1
					self.scanAhead(node)
					self.inOperators -= 1
				elif node.tagName == "get" or node.tagName == "set":
					self.scanAhead(node)
				elif node.tagName == "template":
					self.inTemplate += 1
					self.scanTemplate(node)
					self.inTemplate -= 1
				elif node.tagName == "extern-function":
					self.scanExternFunction(node)
	
	def scanTemplate(self, node):
		pNames, pTypes = self.getParameterList(node)
		self.currentClass.setTemplateNames(pNames)
	
	def scanClass(self, node):
		name = getElementByTagName(node, "name").childNodes[0].nodeValue
		extendingClass = False
		
		self.pushScope()
		
		if name in self.compiler.mainClass.classes:
			refClass = self.compiler.mainClass.classes[name]
			extendingClass = True
			oldClass = self.currentClass
			self.currentClass = refClass
		else:
			refClass = CPPClass(name)
			self.pushClass(refClass)
			self.localClasses.append(self.currentClass)
		
		self.scanAhead(getElementByTagName(node, "code"))
		
		if extendingClass:
			self.currentClass = oldClass
		else:
			self.popClass()
		self.popScope()
	
	def scanFunction(self, node):
		name = getElementByTagName(node, "name").childNodes[0].nodeValue
		
		if self.inGetter:
			getElementByTagName(node, "name").childNodes[0].nodeValue = name = "get" + name.title()
		elif self.inSetter:
			getElementByTagName(node, "name").childNodes[0].nodeValue = name = "set" + name.title()
		
		# Index operator
		name = correctOperators(name)
		
		newFunc = CPPFunction(self, node)
		paramNames, paramTypesByDefinition = self.getParameterList(getElementByTagName(node, "parameters"))
		newFunc.paramNames = paramNames
		newFunc.paramTypesByDefinition = paramTypesByDefinition
		#debug("Types:" + str(newFunc.paramTypesByDefintion))
		self.currentClass.addFunction(newFunc)
		
		if self.currentClass.name == "":
			self.localFunctions.append(newFunc)
	
	def scanExternFunction(self, node):
		name = getElementByTagName(node, "name").childNodes[0].nodeValue
		types = node.getElementsByTagName("type")
		type = "void"
		
		if types:
			type = types[0].childNodes[0].nodeValue
		
		self.compiler.mainClass.addExternFunction(name, type)
	
	def getVariableScopeAnywhere(self, name):
		scope = self.getVariableScope(name)
		if scope:
			return scope
		
		raise CompilerException("Unknown variable: " + name)
	
	def getVariableTypeAnywhere(self, name):
		var = self.getVariable(name)
		if var:
			#if var.type in self.currentTemplateParams:
			#	return self.currentTemplateParams[var.type]
			return var.type
		
		if name in self.currentClassImpl.members:
			return self.currentClassImpl.members[name].type
		
		if name in self.compiler.mainClassImpl.members:
			return self.compiler.mainClassImpl.members[name].type
		
		#print(self.getTopLevelScope().variables)
		#print(self.compiler.globalScope.variables)
		if name in self.compiler.mainClass.classes:
			raise CompilerException("You forgot to create an instance of the class '" + name + "' by using brackets")
		raise CompilerException("Unknown variable: " + name)
	
	def variableExistsAnywhere(self, name):
		if self.variableExists(name) or (name in self.currentClassImpl.members) or (name in self.compiler.mainClassImpl.members):
			#print(name + " exists")
			return 1
		#print(name + " doesn't exist")
		return 0
	
	def isMemberAccessFromOutside(self, op1, op2):
		op1Type = self.getExprDataType(op1)
		op1ClassName = extractClassName(op1Type)
		#print(("get" + op2.nodeValue.title()) + " -> " + str(self.compiler.classes[op1Type].functions.keys()))
		
		if not op1ClassName in self.compiler.mainClass.classes:
			return False
		
		accessingGetter = ("get" + op2.nodeValue.title()) in self.getClass(op1ClassName).functions
		if isTextNode(op2) and (accessingGetter or (op2.nodeValue in self.getClassImplementationByTypeName(op1Type).members)):
			#print(self.currentFunction.getName() + " -> " + varGetter)
			#print(self.currentFunction.getName() == varGetter)
			
			if not (isTextNode(op1) and op1.nodeValue == "self"):
				# Make a virtual call
				return True
		
		return False
	
	def getCallDataType(self, node):
		caller, callerType, funcName = self.getFunctionCallInfo(node)
		params = getElementByTagName(node, "parameters")
		paramsString, paramTypes = self.handleParameters(params)
		
		#if funcName == "distance":
		#	debugStop()
		
		if not funcName.startswith("bp_"):
			callerClassImpl = self.getClassImplementationByTypeName(callerType)
			#funcImpl = callerClassImpl.getFuncImplementation(funcName, paramTypes)
			#funcImpl, codeExists = callerClassImpl.requestFuncImplementation(funcName, paramTypes)
			funcImpl = self.implementFunction(callerType, funcName, paramTypes)
			#debug("Return types: " + str(funcImpl.returnTypes))
			#debug(self.compiler.funcImplCache)
			#debug("Return type of '%s' is '%s' (callerType: '%s')" % (funcImpl.getName(), funcImpl.getReturnType(), callerType))
			return funcImpl.getReturnType()
		else:
			if not (funcName in self.compiler.mainClass.externFunctions):
				raise CompilerException("Function '" + funcName + "' has not been defined")
			
			return self.compiler.mainClass.externFunctions[funcName]
	
	def getExprDataType(self, node):
		dataType = self.getExprDataTypeClean(node)
		return dataType#self.currentClassImpl.translateTemplateName(dataType)
	
	def getExprDataTypeClean(self, node):
		if isTextNode(node):
			if node.nodeValue.isdigit():
				return "Int"
			elif node.nodeValue.replace(".", "").isdigit():
				return "Float"
			elif node.nodeValue.startswith("bp_string_"):
				return "~MemPointer<ConstChar>"
			elif node.nodeValue == "True" or node.nodeValue == "False":
				return "Bool"
			#elif node.nodeValue == "self":
			#	return self.currentClassImpl.getName()
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
				callerClassName = extractClassName(callerType)
				callerClass = self.getClass(callerClassName)
				memberName = node.childNodes[1].childNodes[0].nodeValue
				
#				templateParams = self.getTemplateParams(removeUnmanaged(callerType), callerClassName, callerClass)
#				print("getExprDataTypeClean:")
#				print("Member: %s" % (memberName))
#				print("callerType: " + callerType)
#				print("callerClassName: " + callerClassName)
#				print("templateParams: " + str(templateParams))
#				callerClassImpl = callerClass.implementations["_".join(templateParams.values())]
#				print("Class implementations: " + str(callerClass.implementations))
#				callerClass.debugMembers()
#				print("Picking implementation '" + callerClassImpl.getParamString() + "'")
				callerClassImpl = self.getClassImplementationByTypeName(callerType)
				
				if memberName in callerClassImpl.members:
					#debug("Member '" + memberName + "' does exist")
					memberType = callerClassImpl.members[memberName].type
#					print(memberType)
#					print(callerType)
#					print(callerClassName)
#					print(self.currentTemplateParams)
#					print(templateParams)
#					print("-----")
					return self.currentClassImpl.translateTemplateName(memberType)
				else:
					pass
					#debug("Member '" + memberName + "' doesn't exist")
					
					# data access from a pointer
					if callerClassName == "MemPointer" and memberName == "data":
						return callerType[callerType.find('<')+1:-1]
					
					memberFunc = "get" + memberName.title()
					virtualGetCall = parseString("<call><function><access><value>%s</value><value>%s</value></access></function><parameters/></call>" % (node.childNodes[0].childNodes[0].toxml(), memberFunc)).documentElement
					return self.getCallDataType(virtualGetCall)
				
#				templatesUsed = (callerClassName != callerType)
#				
#				if templatesUsed:
#					templateParams = callerType[len(callerClassName) + 1: -1]
#					translateTemplateParams = callerClass.mapTemplateParams(templateParams)
#					
#					if memberType in translateTemplateParams:
#						return translateTemplateParams[memberType]
#					else:
#						return memberType
#				else:
#					return memberType
			elif node.tagName == "unmanaged":
				self.inUnmanaged += 1
				expr = self.getExprDataTypeClean(node.childNodes[0].childNodes[0])
				self.inUnmanaged -= 1
				return "~" + expr
			elif node.tagName == "negative":
				return self.getExprDataTypeClean(node.childNodes[0].childNodes[0])
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
	
	def registerVariable(self, var):
		#debug("Registered variable '" + var.name + "' of type '" + var.type + "'")
		self.getCurrentScope().variables[var.name] = var
		#self.currentClassImpl.addMember(var)
	
	def handleFor(self, node):
		fromNodeContent = getElementByTagName(node, "from").childNodes[0]
		toLimiterNode = getElementByTagName(node, "to")
		
		if toLimiterNode:
			toNodeContent = toLimiterNode.childNodes[0]
			operator = "<="
		else:
			toNodeContent = getElementByTagName(node, "until").childNodes[0]
			operator = "<"
		
		fromType = self.getExprDataType(fromNodeContent)
		
		iterExpr = self.parseExpr(getElementByTagName(node, "iterator").childNodes[0])
		fromExpr = self.parseExpr(fromNodeContent)
		toExpr = self.parseExpr(toNodeContent)
		toType = self.getExprDataType(toNodeContent)
		#stepExpr = self.parseExpr(getElementByTagName(node, "step").childNodes[0])
		
		self.pushScope()
		var = CPPVariable(iterExpr, getHeavierOperator(fromType, toType), fromExpr, False, False, False)
		typeInit = ""
		if not self.variableExistsAnywhere(iterExpr):
			self.getCurrentScope().variables[iterExpr] = var
			typeInit = var.type + " "
		code = self.parseChilds(getElementByTagName(node, "code"), "\t" * self.currentTabLevel, ";\n")
		self.popScope()
		
		return "for(%s%s = %s; %s %s %s; ++%s) {\n%s%s}" % (typeInit, iterExpr, fromExpr, iterExpr, operator, toExpr, iterExpr, code, "\t" * self.currentTabLevel)
	
	def handleReturn(self, node):
		expr = self.parseExpr(node.childNodes[0])
		retType = self.getExprDataType(node.childNodes[0])
		self.currentFunctionImpl.returnTypes.append(retType)
		#debug("Returning '%s' with type '%s' on current func '%s' with implementation '%s'" % (expr, retType, self.currentFunction.getName(), self.currentFunctionImpl.getName()))
		return "return " + expr
	
	def handleTypeDeclaration(self, node):
		self.inTypeDeclaration += 1
		typeName = self.currentClassImpl.translateTemplateName(self.parseExpr(node.childNodes[1]))
		varName = self.parseExpr(node.childNodes[0])
		self.inTypeDeclaration -= 1
		
		if varName.startswith("this->"):
			varName = varName[len("this->"):]
			self.currentClassImpl.addMember(CPPVariable(varName, typeName, "", False, not extractClassName(typeName) in nonPointerClasses, False))
			return ""
		
		if self.variableExistsAnywhere(varName):
			raise CompilerException("'" + varName + "' has already been defined as a %s variable of the type '" % (["local", "global"][self.getVariableScopeAnywhere(varName) == self.getTopLevelScope()]) + self.getVariableTypeAnywhere(varName) + "'")
		else:
			#print("Declaring '%s' as '%s'" % (varName, typeName))
			var = CPPVariable(varName, typeName, "", self.inConst, not typeName in nonPointerClasses, False)
			self.registerVariable(var)
			return varName
			#return adjustDataType(typeName, True) + " " + varName
			
		return varName
	
	def handleConst(self, node):
		self.inConst += 1
		expr = self.handleAssign(node.childNodes[0])
		self.inConst -= 1
		
		return expr
	
	def handleTemplateCall(self, node):
		op1 = self.parseExpr(node.childNodes[0].childNodes[0])
		op2 = self.parseExpr(node.childNodes[1].childNodes[0])
		
		# Template translation
		op1 = self.currentClassImpl.translateTemplateName(op1)
		op2 = self.currentClassImpl.translateTemplateName(op2)
		
		return op1 + "<" + op2 + ">"
	
	def handleString(self, node):
		id = self.id + "_" + node.getAttribute("id")
		value = node.childNodes[0].nodeValue
		line = id + " = \"" + value + "\";\n"
		var = CPPVariable(id, "CString", value, False, False, True)
		#self.currentClassImpl.addMember(var)
		self.getTopLevelScope().variables[id] = var
		self.compiler.stringCounter += 1
		return line
	
	def handleElse(self, node):
		self.pushScope()
		code = self.parseChilds(getElementByTagName(node, "code"), "\t" * self.currentTabLevel, ";\n")
		self.popScope()
		
		return " else {\n" + code + "\t" * self.currentTabLevel + "}"
	
	def handleTarget(self, node):
		name = getElementByTagName(node, "name").childNodes[0].nodeValue
		if name == self.compiler.getTargetName():
			return self.parseChilds(getElementByTagName(node, "code"), "\t" * self.currentTabLevel, ";\n")
	
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
	
	def pushScope(self):
		self.currentTabLevel += 1
		ScopeController.pushScope(self)
		
	def popScope(self):
		self.currentTabLevel -= 1
		ScopeController.popScope(self)
	
	def pushClass(self, classObj):
		self.currentClass.addClass(classObj)
		self.currentClass = classObj
		
	def popClass(self):
		self.currentClass = self.currentClass.parent
		
	def inClass(self):
		return self.currentClass.name == ""
	
	def writeFunctions(self):
		for func in self.localFunctions:
			for funcImpl in func.implementations.values():
				self.functionsHeader += "%s\n" % (funcImpl.getFullCode())
	
	def writeClasses(self):
		prefix = "BP"
		
		for classObj in self.localClasses:
			if not classObj.isExtern:
				for classImplId, classImpl in classObj.implementations.items():
					code = ""
					
					# Functions
					for funcImpl in classImpl.funcImplementations.values():
						if funcImpl.getFuncName() != "init":
							code += "\t" + funcImpl.getFullCode() + "\n"
						else:
							code += "\t" + funcImpl.getConstructorCode() + "\n"
					
					# Private members
					code += "private:\n"
					for member in classImpl.members.values():
						#print(member.name + " is of type " + member.type)
						code += "\t" + adjustDataType(member.type, True) + " " + member.name + ";\n"
					
					code += "\t\n"
					
					# Templates
					templatePrefix = ""
					templatePostfix = ""
					if classObj.templateNames:
						templatePrefix += "template <>\n"
						templatePostfix = classImpl.getTemplateValuesString(True)
						#self.classesHeader += "template <typename %s>\n" % (", typename ".join(classObj.templateParams))
					
					# Comment
					self.classesHeader += "// %s\n" % (prefix + classObj.name + templatePostfix)
					self.classesHeader += templatePrefix
					
					# Add code to classes header
					self.classesHeader += "class %s" % (prefix + classObj.name + templatePostfix) + " {\npublic:\n" + code + "};\n\n"
	
	def getCode(self):
		self.writeFunctions()
		self.writeClasses()
		return self.header + self.prototypesHeader + self.varsHeader + self.functionsHeader + self.classesHeader + self.actorClassesHeader + self.body + self.footer
