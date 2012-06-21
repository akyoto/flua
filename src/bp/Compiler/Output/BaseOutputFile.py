####################################################################
# Header
####################################################################
# File:		Base class for output files
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
from bp.Compiler.Config import *
from bp.Compiler.Output import *
from bp.Compiler.Input.bpc.BPCUtils import *

####################################################################
# Globals
####################################################################
INT32_MAX = 2147483647
INT32_MIN = -2147483648

enableOperatorOverloading = {
	"add",
	"equal",
	"not-equal",
	"multiply"
}#{"add", "subtract", "multiply", "divide", "equal"}:

replacedNodeValues = {
	"from" : "bp__from",
	"char" : "bp__char",
	"int" : "bp__int",
	"bool" : "bp_bool",
}

####################################################################
# Classes
####################################################################
class BaseOutputFile(ScopeController):
	
	def __init__(self, compiler, file, root):
		ScopeController.__init__(self)
		
		self.compiler = compiler
		self.file = fixPath(file)
		self.dir = extractDir(file)
		
		# XML
		self.root = root
		self.codeNode = getElementByTagName(self.root, "code")
		self.headerNode = getElementByTagName(self.root, "header")
		self.dependencies = getElementByTagName(self.headerNode, "dependencies")
		self.strings = getElementByTagName(self.headerNode, "strings")
		self.stringsAsBytes = dict()
		
		# Local
		self.localClasses = []
		self.localFunctions = []
		self.additionalCodePerLine = []
		self.includes = []
		
		# Increment id
		self.compiler.fileCounter += 1
		self.id = "file_" + str(self.compiler.fileCounter)
		
		# Current
		self.currentClass = self.compiler.mainClass
		self.currentClassImpl = self.currentClass.requestImplementation([], [])
		self.currentFunction = None
		self.currentFunctionImpl = None
		
		# State
		self.inExtern = 0
		self.inGetter = 0
		self.inSetter = 0
		self.inCastDefinition = 0
		self.inTemplate = 0
		self.inAssignment = 0
		self.inConst = 0
		self.inUnmanaged = 0
		self.inOperators = 0
		self.inIterators = 0
		self.inCasts = 0
		self.inOperator = 0
		self.inTypeDeclaration = 0
		self.inFunction = 0
		self.inDefine = 0
		self.inExtends = 0
		self.inParallel = 0
		self.inShared = 0
		self.namespaceStack = []
		self.parallelBlockStack = []
		self.tuples = dict()
		self.tupleTypes = dict()
		self.onVariable = ""
		
		# TODO: Read from module meta data
		# Speed / Correctness
		self.checkDivisionByZero = True#self.compiler.checkDivisionByZero
		
		# Inserted for mathematical expressions
		self.exprPrefix = ""
		self.exprPostfix = ""
		
		# String class
		self.stringClassDefined = False
		
		# Element handlers
		self.directMapping = {
			"access" : self.handleAccess,
			"assign" : self.handleAssign,
			"call" : self.handleCall,
			"new" : self.handleNew,
			"else" : self.handleElse,
			"try" : self.handleTry,
			"catch" : self.handleCatch,
			"namespace" : self.handleNamespace,
			"target" : self.handleTarget,
			"return" : self.handleReturn,
			"yield" : self.handleYield,
			"for" : self.handleFor,
			"foreach" : self.handleForEach,
			"flow-to" : self.handleFlowTo,
			"const" : self.handleConst,
			"continue" : self.buildContinue,
			"parallel" : self.handleParallel,
			"shared" : self.handleShared,
			"in" : self.handleIn,
			"on" : self.handleOn,
			"unmanaged" : self.handleUnmanaged,
			"compiler-flag" : self.handleCompilerFlag,
			"template-call" : self.handleTemplateCall,
			
			# Ignored
			"class" : None,
			"function" : None,
			"operator" : None,
			"cast-definition" : None,
			"get" : None,
			"set" : None,
			"extern" : None,
			"operators" : None,
			"iterators" : None,
			"extern-function" : None,
			"extern-variable" : None,
			"template" : None,
			"require" : None,
			"ensure" : None,
			"define" : None,
		}
		
		# Syntax
		self.lineLimiter = ""
		self.myself = ""
		self.trySyntax = ""
		self.catchSyntax = ""
		self.throwSyntax = ""
		self.returnSyntax = ""
		self.memberAccessSyntax = ""
		self.singleParameterSyntax = ""
		self.parameterSyntax = ""
		self.newObjectSyntax = ""
		self.binaryOperatorSyntax = "%s%s%s%s%s"
		self.binaryOperatorDivideSyntax = "%s%s%s%s%s"
		self.pointerDerefAssignSyntax = ""
		self.assignSyntax = "%s = %s"
		self.assignFirstTimeSyntax = self.assignSyntax
		self.constAssignSyntax = ""
		self.callSyntax = "%s(%s)"
		self.externCallSyntax = self.callSyntax
		self.templateSyntax = ""
		
		# Memory management
		self.useGC = True
		
		# Debugging
		self.lastParsedNode = list()
	
	def compile(self):
		raise NotImplementedError()
	
	def createVariable(self, name, type, value, isConst, isPointer, isPublic):
		raise NotImplementedError()
	
	def castToNativeNumeric(self, variableType, value):
		return value
	
	def checkStringClass(self):
		# Implement operator = of the string class manually to enable assignments
		if self.compiler.needToInitStringClass:
			#self.implementFunction("UTF8String", correctOperators("="), ["~MemPointer<ConstChar>"])
			self.implementFunction("UTF8String", "init", [])
			self.implementFunction("UTF8String", "init", ["~MemPointer<Byte>"])
			self.compiler.needToInitStringClass = False
		
		if self.classExists("UTF8String") and self.stringClassDefined == False:
			self.compiler.needToInitStringClass = True
	
	def handleAssign(self, node):
		self.inAssignment += 1
		isSelfMemberAccess = False
		publicMemberAccess = False
		
		# Member access (setter)
		op1 = node.childNodes[0].childNodes[0]
		if not isTextNode(op1):
			if op1.tagName == "access":
				accessOp1 = op1.childNodes[0].childNodes[0]
				accessOp2 = op1.childNodes[1].childNodes[0]
				
				# data access from a pointer
				accessOp1Type = self.getExprDataType(accessOp1)
				if extractClassName(accessOp1Type) == "MemPointer" and accessOp2.nodeValue == "data": #and isUnmanaged(accessOp1Type):
					return self.pointerDerefAssignSyntax % (self.parseExpr(accessOp1), self.parseExpr(node.childNodes[1]))
				
				isMemberAccess, publicMemberAccess = self.isMemberAccessFromOutside(accessOp1, accessOp2)
				if isMemberAccess:
					#print("Using setter for type '%s'" % (accessOp1type))
					setFunc = self.cachedParseString("<call><function><access><value>%s</value><value>%s</value></access></function><parameters><parameter>%s</parameter></parameters></call>" % (accessOp1.toxml(), "set" + capitalize(accessOp2.nodeValue), node.childNodes[1].childNodes[0].toxml())).documentElement
					return self.handleCall(setFunc)
				elif publicMemberAccess:
					pass
				#pass
				#variableType = self.getExprDataType(op1)
				#variableClass = self.compiler.classes[removeGenerics(variableType)]
			elif op1.tagName == "index":
				indexCallerType = self.getExprDataType(op1.childNodes[0].firstChild)
				if indexCallerType.startswith("MemPointer") or indexCallerType.startswith("~MemPointer"):
					return self.parseExpr(node.childNodes[0]) + " = " + self.parseExpr(node.childNodes[1])
				else:
					memberFunc = "[]="
					
					obj = op1.childNodes[0].firstChild.toxml()
					key = op1.childNodes[1].firstChild.toxml()
					value = node.childNodes[1].childNodes[0].toxml()
					
					#print(obj)
					#print(key)
					#print(value)
					
					xmlCode = "<call><function><access><value>%s</value><value>%s</value></access></function><parameters><parameter>%s</parameter><parameter>%s</parameter></parameters></call>" % (obj, memberFunc, key, value)
					virtualSetIndexCall = self.cachedParseString(xmlCode).documentElement
					return self.handleCall(virtualSetIndexCall)
			# Multiple return values
			elif op1.tagName == "parameters":
				#return "int a, b; {%s} = *(%s)" % (self.parseExpr(op1), self.parseExpr(node.childNodes[1].childNodes[0]))
				
				# Build N assigns
				op2 = node.childNodes[1].childNodes[0]
				op2Expr = self.parseExpr(op2)
				valueType = self.getExprDataType(op2)
				numAssignments = len(op1.childNodes)
				tupleTypes = splitParams(valueType[valueType.find("<")+1:-1])
				
				if numAssignments != len(tupleTypes):
					raise CompilerException("'%s' returns %d values while there are %d assignments" % (nodeToBPC(op2), len(tupleTypes), numAssignments))
				
				code = []
				
				code.append(self.buildLine("%s _bp_tuple_%d = %s" % (self.adjustDataType(valueType), self.compiler.tupleUnbindCounter, op2Expr)))
				
				for i in range(numAssignments):
					varExpr = op1.childNodes[i].firstChild
					varType = tupleTypes[i]
					
					#valueVar = self.createVariable("_bp_tuple_%d->_%d" % (self.compiler.tupleUnbindCounter, i), varType, varExpr, self.inConst, not varType in nonPointerClasses, False)
					#self.registerVariable(valueVar)
					
					valueVar = "_bp_tuple_%d->_%d" % (self.compiler.tupleUnbindCounter, i)
					
					self.tupleTypes[valueVar] = varType
					
					virtualAssign = self.makeXMLAssign(varExpr.toxml(), valueVar)
					code.append(self.buildLine(self.handleAssign(virtualAssign)))
					
				code.append(self.buildLine("delete _bp_tuple_%d" % self.compiler.tupleUnbindCounter))
					
				self.compiler.tupleUnbindCounter += 1
				
				return ''.join(code)
		
		# Inline type declarations
		declaredInline = (tagName(node.childNodes[0].childNodes[0]) == "declare-type")
		
		# Inline declaration + top level scope = don't include type name
		variableName = self.getNamespacePrefix()
		if declaredInline and self.getCurrentScope() == self.getTopLevelScope():
			variableName += self.handleTypeDeclaration(node.childNodes[0].childNodes[0], insertTypeName = False)
		else:
			variableName += self.parseExpr(node.childNodes[0].childNodes[0])
		
		# In parameter definition?
		if (not isinstance(node.parentNode, Document)) and node.parentNode.tagName == "parameter":
			#print("----------")
			#print(declaredInline)
			#print(variableName)
			#print(self.getNamespacePrefix())
			#print("--xxx--")
			return variableName
		
		# Parse value
		if len(node.childNodes) == 2:
			if len(node.childNodes[1].childNodes) == 1:
				value = self.parseExpr(node.childNodes[1].childNodes[0], False)
			else:
				raise CompilerException("Invalid assignment value for '%s'" % (variableName))
		else:
			raise CompilerException("Invalid assignment value for '%s'" % (variableName))
		
		# Parse value type
		valueType = self.getExprDataType(node.childNodes[1].childNodes[0])
		
		if valueType == "void":
			raise CompilerException("'%s' which is assigned to '%s' does not return a value" % (nodeToBPC(node.childNodes[1].childNodes[0]), variableName))
		
		#if valueType.startswith("Tuple<"):
		#	raise CompilerException("'%s' returns multiple values, not just one" % (nodeToBPC(op2)))
		
		memberName = variableName
		
		# Did we define a type?
		try:
			variableType = self.getVariableTypeAnywhere(variableName)
		except:
			variableType = ""
		
		# Member access?
		if variableName.startswith(self.memberAccessSyntax):
			memberName = variableName[len(self.memberAccessSyntax):]
			memberName = self.fixMemberName(memberName)
			# TODO: Save it for the IDE
			#self.currentClass.possibleMembers[memberName] = variableType
			
			isSelfMemberAccess = True
		
		if isSelfMemberAccess or publicMemberAccess:
			var = self.createVariable(memberName, valueType, value, self.inConst, not valueType in nonPointerClasses, False)
			#if not variableName in self.currentClass.members:
			#	self.currentClass.addMember(var)
			
			if not memberName in self.currentClassImpl.members:
				self.currentClassImpl.addMember(var)
			
			variableExisted = True
		else:
			#print("Checking whether '%s' exists:" % variableName)
			variableExisted = self.variableExistsAnywhere(variableName)
			
			# If it exists as a member we do not care about it
			if variableExisted == 2:
				variableExisted = False
			
		# Need to register it here? 2 stands for class members
		if ((not variableExisted) or variableExisted == 2) and (not declaredInline):
			var = self.createVariable(variableName, valueType, value, self.inConst, not valueType in nonPointerClasses, False)
			
			# Check if we are in the top function level scope
			if self.currentFunctionImpl and self.getCurrentScope() != self.currentFunctionImpl.scope:
				self.registerVariableFuncScope(var)
				variableExisted = True
			else:
				self.registerVariable(var)
			
			if self.inConst:
				return self.buildConstAssignment(var, value)
		
		#else:
		#	var = self.getVariableTypeAnywhere(variableName)
		
		#if not variable in self.currentClassImpl.members:
		#	self.currentClassImpl.add
		
		# Int = BigInt
		if variableType in {"Int", "Int32", "Int64"} and valueType == "BigInt":
			value = self.castToNativeNumeric(variableType, value)
		
		self.inAssignment -= 1
		
		#print(node.toprettyxml())
		#print(variableName, "|", variableType, "|", value, "|", valueType)
		
		# Casts
		if variableExisted and variableType and variableType != valueType and not valueType in nonPointerClasses and not extractClassName(valueType) == "MemPointer":
			#debug("Need to cast %s to %s" % (valueType, variableType))
			#if variableType in nonPointerClasses:
			#	castType = "static_cast"
			#else:
			#	castType = "reinterpret_cast"
			value = "((%s)%sto%s())" % (value, self.ptrMemberAccessChar, normalizeName(variableType))
		
		#if isSelfMemberAccess:
		#	variableName = "%s_%s" % (self.memberAccessSyntax, memberName)
		
		# Unmanaged types
		if isUnmanaged(valueType) and not variableExisted:
			#print(variableName, " : ", variableType, " ||| ", value, " : ", valueType)
			return self.declareUnmanagedSyntax % (var.getPrototype(), value)
		elif self.getCurrentScope() == self.getTopLevelScope():
			return self.assignSyntax % (variableName, value)
		elif variableExisted:
			return self.assignSyntax % (variableName, value)
		elif declaredInline:
			return self.assignSyntax % (variableName, value) #+ ";//Declared inline"
		else:
			return self.assignFirstTimeSyntax % (var.getPrototype(), value)
	
	def parseBinaryOperator(self, node, connector, checkPointer = False):
		op1 = self.parseExpr(node.childNodes[0].childNodes[0])
		op2 = self.parseExpr(node.childNodes[1].childNodes[0])
		
		if op2 == "my":
			op2 = self.myself
		
		if op1 == "my":
			op1 = self.myself
			#op2 = "_" + op2
		
		#if connector == self.ptrMemberAccessChar:
		#	op2 = "_" + op2
		
#		if checkPointer:
#			op1type = self.getExprDataType(node.childNodes[0].childNodes[0])
#			print("%s%s%s (%s)" % (op1, connector, op2, op1 + " is a '" + op1type + "'"))
#			if (not op1type in nonPointerClasses) and (not isUnmanaged(op1type)) and (not connector == " == "):
#				return self.exprPrefix + op1 + "->operator" + connector.replace(" ", "") + "(" + op2 + ")" + self.exprPostfix
		
		connector = self.transformBinaryOperator(connector)
		
		# Division by zero
		if self.checkDivisionByZero and (connector == " / " or connector == " \\ "):
			self.addDivisionByZeroCheck(op2)
		
		if connector in {" + ", " - ", " * ", " / ", " \\ ", " & ", " | ", " && ", " || ", " % "}:
			self.exprPrefix = "("
			self.exprPostfix = ")"
		else:
			self.exprPrefix = ""
			self.exprPostfix = ""
		
		# Float conversion if needed
		if connector != " / ":
			return self.binaryOperatorSyntax % (self.exprPrefix, op1, connector, op2, self.exprPostfix)
		else:
			return self.binaryOperatorDivideSyntax % (self.exprPrefix, op1, connector, op2, self.exprPostfix)
	
	def getNamespacePrefix(self):
		namespacePrefix = '_'.join(self.namespaceStack)
		if namespacePrefix:
			return namespacePrefix + "_"
		else:
			return ""
	
	def handleCompilerFlag(self, node):
		return ""
	
	def fixMemberName(self, memberName):
		if memberName and memberName[0] == "_":
			memberName = memberName[1:]
		
		pos = memberName.find(self.ptrMemberAccessChar)
		if pos != -1:
			return memberName[:pos]
		
		return memberName
	
	def getParameterDefinitions(self, pNode, types, defaultValueTypes):
		if pNode is None:
			return "", ""
		
		pList = ""
		funcStartCode = ""
		counter = 0
		typesLen = len(types)
		
		parseExpr = self.parseExpr
		
		for node in pNode.childNodes:
			#if isElemNode(node.childNodes[0]) and node.childNodes[0].tagName == "declare-type":
			#	name = node.childNodes[0].childNodes[0].childNodes[0].nodeValue
			#else:
			if node.firstChild.nodeType != Node.TEXT_NODE and node.firstChild.tagName == "parameter":
				name = parseExpr(node.firstChild.firstChild)
			else:
				name = parseExpr(node.firstChild)
			
			#print("Name: " + name)
			#print(node.toprettyxml())
			
			if name in replacedNodeValues:
				name = replacedNodeValues[name]
			
			# Not enough parameters
			if counter >= typesLen:
				# Default values?
				if counter < len(defaultValueTypes) and defaultValueTypes[counter]:
					defaultValueType = defaultValueTypes[counter]
					adjustedDefaultValueType = self.adjustDataType(defaultValueType)
					#print("Using default parameter of type %s translated to %s" % (defaultValueType, adjustedDefaultValueType))
					self.registerVariable(self.createVariable(name, adjustedDefaultValueType, "", False, not adjustedDefaultValueType in nonPointerClasses, False))
					pList += self.buildSingleParameter(adjustedDefaultValueType, name) + ", "
					continue
				
				raise CompilerException("You forgot to specify the parameter '%s' of the function '%s'" % (name, self.currentFunction.getName()))
			
			usedAs = types[counter]
			
			# Typedefs
			usedAs = self.prepareTypeName(usedAs)
			
			# TODO: ...
			if name.startswith(self.memberAccessSyntax):
				member = name[len(self.memberAccessSyntax):]
				member = self.fixMemberName(member)
				
				#pos = member.find(self.ptrMemberAccessChar)
				#if pos != -1:
				#	member = member[:pos]
				
				self.currentClassImpl.addMember(self.createVariable(member, usedAs, "", False, not usedAs in nonPointerClasses, False))
				name = "__" + member
				funcStartCode += "\t\t" + self.memberAccessSyntax + member + " = " + name + self.lineLimiter
			
			if node.firstChild and node.firstChild.firstChild and tagName(node.childNodes[0].firstChild.firstChild) == "declare-type":
				declNode = node.childNodes[0].firstChild.firstChild
				declaredInline = True
			else:
				declNode = node.childNodes[0]
				declaredInline = (tagName(declNode) == "declare-type")
			
			if not declaredInline:
				#print("Variable %s used as '%s'" % (name, usedAs))
				self.getCurrentScope().variables[name] = self.createVariable(name, usedAs, "", False, not usedAs in nonPointerClasses, False)
				pList += self.buildSingleParameter(self.adjustDataType(usedAs), name) + ", "
			else:
				#for member in self.currentClassImpl.members.values():
				#	print(member.name)
				#	print(member.type)
				
				definedAs = self.parseExpr(declNode.childNodes[1], True) #self.getVariableTypeAnywhere(name)
				
				# Typedefs
				definedAs = self.prepareTypeName(definedAs)
				
				definedAs = self.currentClassImpl.translateTemplateName(definedAs)
				definedAs = self.addMissingTemplateValues(definedAs)
				
				# Implement it
				#if not definedAs in nonPointerClasses:
				#	try:
				#		self.getClassImplementationByTypeName(definedAs)
				#	except:
				#		pass
				
				#print("Defined: " + definedAs)
				#print(name)
				#print("------------")
				
				pList += self.buildSingleParameter(self.adjustDataType(definedAs), name) + ", "
				
				if definedAs != usedAs:
					if definedAs in nonPointerClasses and usedAs in nonPointerClasses:
						heavier = getHeavierOperator(definedAs, usedAs)
						if usedAs == heavier:
							compilerWarning("Information might be lost by converting '%s' to '%s' for the parameter '%s' in the function '%s'" % (usedAs, definedAs, name, self.currentFunction.getName()))
					else:
						raise CompilerException("'%s' expects the type '%s' where you used the type '%s' for the parameter '%s'" % (self.currentFunction.getName(), definedAs, usedAs, name))
			
			counter += 1
		
		return pList[:len(pList)-2], funcStartCode
	
	def scanPublicMember(self, node):
		name = node.firstChild.nodeValue
		#self.currentClass.addDefaultGetter(name)
		#self.currentClass.addDefaultSetter(name)
		self.currentClass.addPublicMember(name)
	
	#def scanDefaultGet(self, node):
	#	for child in node.childNodes:
	#		propertyName = child.firstChild.nodeValue
	#		self.currentClass.addDefaultGetter(propertyName)
			
	#def scanDefaultSet(self, node):
	#	for child in node.childNodes:
	#		propertyName = child.firstChild.nodeValue
	#		self.currentClass.addDefaultSetter(propertyName)
	
	def scanTemplate(self, node):
		pNames, pTypes, pDefaultValues, pDefaultValueTypes = self.getParameterList(node)
		self.currentClass.setTemplateNames(pNames, pDefaultValues)
		if self.currentClass.forceImplementation:
			self.currentClass.checkDefaultImplementation()
	
	def scanExtends(self, node):
		pNames, pTypes, pDefaultValues, pDefaultValueTypes = self.getParameterList(node)
		self.currentClass.setExtends([self.getClassImplementationByTypeName(className) for className in pNames])
	
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
			refClass = self.createClass(name, node)
			if refClass.isDefaultVersion:
				self.compiler.specializedClasses[refClass.getFinalName()] = refClass
			self.pushClass(refClass)
			self.localClasses.append(self.currentClass)
		
		self.scanAhead(getElementByTagName(node, "code"))
		
		if extendingClass:
			self.currentClass = oldClass
		else:
			self.popClass()
		self.popScope()
	
	# Namespaces
	def scanNamespace(self, node):
		name = getElementByTagName(node, "name").firstChild.nodeValue
		codeNode = getElementByTagName(node, "code")
		
		self.pushNamespace(name)
		self.scanAhead(codeNode)
		self.popNamespace()
	
	# Typedefs
	def scanDefine(self, node):
		defineWhat = self.parseExpr(node.firstChild.firstChild)
		defineAs = self.parseExpr(node.childNodes[1].firstChild)
		self.compiler.defines[defineWhat] = defineAs
	
	def scanFunction(self, node):
		if self.inCastDefinition:
			name = self.parseExpr(getElementByTagName(node, "to").childNodes[0], True)
			
			# Replace typedefs
			name = self.prepareTypeName(name)
		else:
			#print(node.toprettyxml())
			nameNode = getElementByTagName(node, "name")
			if nameNode.childNodes:
				name = nameNode.childNodes[0].nodeValue
			else:
				name = ""
		
		#if self.inGetter:
		#	getElementByTagName(node, "name").childNodes[0].nodeValue = name = "get" + capitalize(name)
		#elif self.inSetter:
		#	getElementByTagName(node, "name").childNodes[0].nodeValue = name = "set" + capitalize(name)
		# Index operator
		name = correctOperators(name)
		
		newFunc = self.createFunction(node)
		paramNames, paramTypesByDefinition, paramDefaultValues, paramDefaultValueTypes = self.getParameterList(getElementByTagName(node, "parameters"))
		newFunc.paramNames = paramNames
		newFunc.paramTypesByDefinition = paramTypesByDefinition
		newFunc.paramDefaultValues = paramDefaultValues
		newFunc.paramDefaultValueTypes = paramDefaultValueTypes
		#debug("Types:" + str(newFunc.paramTypesByDefintion))
		self.currentClass.addFunction(newFunc)
		
		if self.currentClass.name == "":
			self.localFunctions.append(newFunc)
		
		if isMetaDataTrue(getMetaData(node, "force-implementation")):
			newFunc.setForceImplementation(True)
		
		# Save variables for the IDE
		if self.compiler.background:
			self.tryGettingVariableTypes(newFunc)
		
	def tryGettingVariableTypes(self, func):
		func.assignNodes = findNodes(func.node, "assign")
		
	def scanExternFunction(self, node):
		name = self.getNamespacePrefix() + getElementByTagName(node, "name").childNodes[0].nodeValue
		types = node.getElementsByTagName("type")
		type = "void"
		
		if types:
			type = types[0].childNodes[0].nodeValue
		
		# TODO: Remove hardcoded
		if type == "CString":
			type = "~MemPointer<Byte>"
		
		# Typedefs
		type = self.prepareTypeName(type)
		
		self.compiler.mainClass.addExternFunction(name, type)
		
	def scanExternVariable(self, node):
		name = getElementByTagName(node, "name").childNodes[0].nodeValue
		types = node.getElementsByTagName("type")
		typeName = "Int"
		
		if types:
			typeName = types[0].childNodes[0].nodeValue
		
		# TODO: Remove hardcoded
		if typeName == "CString":
			typeName = "~MemPointer<Byte>"
		
		# Typedefs
		typeName = self.prepareTypeName(typeName)
		
		self.compiler.mainClass.addExternVariable(name, typeName)
	
	def handleNew(self, node):
		typeName = self.parseExpr(getElementByTagName(node, "type").childNodes[0], True)
		paramsNode = getElementByTagName(node, "parameters")
		paramsString, paramTypes = self.handleParameters(paramsNode)
		
		typeName = self.prepareTypeName(typeName)
		
		pos = typeName.find("<")
		if pos != -1:
			className = removeUnmanaged(typeName[:pos])
			classObj = self.getClass(className)
			
			# Actor
			if className == "Actor":
				actorBoundClass = extractClassName(typeName[pos+1:-1])
				self.compiler.mainClass.classes[actorBoundClass].usesActorModel = True
			elif className == "MemPointer":
				ptrType = typeName[pos+1:-1]
				if len(paramsNode.childNodes) > 1:
					raise CompilerException("Too many parameters for the MemPointer constructor (only size needed)")
				
				#if ptrType in self.currentTemplateParams:
				#	ptrType = self.currentTemplateParams[ptrType]
				
				ptrType = self.currentClassImpl.translateTemplateName(ptrType)
				ptrType = self.adjustDataType(ptrType, True)
				
				if self.inUnmanaged:
					return self.buildUnmanagedMemPtrWithoutGC(ptrType, paramsString)
				elif self.useGC:
					return self.buildUnmanagedMemPtrWithGC(ptrType, paramsString)
				else:
					raise CompilerException("To create a manageable object you need to enable the GC")
		else:
			classObj = self.getClass(typeName)
			typeName = self.addMissingTemplateValues(typeName)
		
		# Mutable / Immutable
		if classObj.name in self.compiler.specializedClasses:
			classObj = self.compiler.specializedClasses[classObj.name]
		
		# Default parameters for init
		paramTypes, paramsString = self.addDefaultParameters(typeName, "init", paramTypes, paramsString)
		
		funcImpl = self.implementFunction(typeName, "init", paramTypes)
		
		if "finalize" in classObj.functions:
			destructorImpl = self.implementFunction(typeName, "finalize", [])
		
		finalTypeName = self.adjustDataType(typeName, False)
		
		if self.inUnmanaged:
			return paramsString
			#return finalTypeName + "(" + paramsString + ")"
		else:
			if self.useGC:
				# Classes are automatically managed by the GC
				return self.buildNewObject(finalTypeName, funcImpl, paramsString)
			#elif self.useReferenceCounting:
			#	return pointerType + "< " + finalTypeName + " >(new " + finalTypeName + "(" + paramsString + "))"
			#else:
			#	return "(new " + finalTypeName + "(" + paramsString + "))"
	
	def pushClass(self, classObj):
		self.currentClass.addClass(classObj)
		self.currentClass = classObj
		
	def popClass(self):
		self.currentClass = self.currentClass.parent
	
	def getLastParsedNode(self):
		if not self.lastParsedNode:
			return None
		
		return self.lastParsedNode[-1]
	
	def getExprDataType(self, node):
		dataType = self.getExprDataTypeClean(node)
		dataType = self.addMissingTemplateValues(dataType)
		
		# Replace typedefs
		dataType = self.prepareTypeName(dataType)
		
		return dataType#self.currentClassImpl.translateTemplateName(dataType)
	
	def getCallDataType(self, node):
		caller, callerType, funcName = self.getFunctionCallInfo(node)
		params = getElementByTagName(node, "parameters")
		paramsString, paramTypes = self.handleParameters(params)
		
		#if funcName == "distance":
		#	debugStop()
		#print(caller, callerType, funcName, "<<<<<<<<<<")
		if self.compiler.mainClass.hasExternFunction(funcName):
			#print("EXTERN USAGE: " + funcName)
			return self.compiler.mainClass.externFunctions[funcName]
		else:
			callerClassImpl = self.getClassImplementationByTypeName(callerType)
			funcImpl = self.implementFunction(callerType, funcName, paramTypes)
			
			#raise CompilerException("Function '" + funcName + "' has not been defined  [Error code 4]")
			
			#debug("Return types: " + str(funcImpl.returnTypes))
			#debug(self.compiler.funcImplCache)
			#debug("Return type of '%s' is '%s' (callerType: '%s')" % (funcImpl.getName(), funcImpl.getReturnType(), callerType))
			
			return funcImpl.getReturnType()
	
	def addMissingTemplateValues(self, typeName):
		pos = typeName.find("<")
		
		if pos == -1:
			if typeName in self.compiler.mainClass.classes:
				classObj = self.getClass(typeName)
				if classObj.templateNames:
					typeName += "<"
					for dataType in classObj.templateDefaultValues:
						dataType = self.currentClassImpl.translateTemplateName(dataType)
						typeName += self.addMissingTemplateValues(dataType) + ", "
					typeName = typeName[:-2] + ">"
		else:
			pass
			#templateValues = typeName[pos+1:-1].split(",")
			#for templateValue in templateValues:
			#	templateValue = templateValue.strip()
			#	print(templateValue)
		return typeName
	
	def getExprDataTypeClean(self, node):
		if isTextNode(node):
			if node.nodeValue.isdigit():
				num = int(node.nodeValue)
				if num > INT32_MAX or num < INT32_MIN:
					return "BigInt"
				else:
					return "Int"
			elif node.nodeValue.startswith("0x"):
				return "Int"
			elif node.nodeValue.replace(".", "").isdigit():
				return "Float"
			elif node.nodeValue.startswith("bp_string_"):
				if self.stringClassDefined: #or self.currentFunction.isIterator:
					if node.nodeValue in self.stringsAsBytes:
						return "Byte"
					else:
						# All modules that import UTF8String have it defined
						return "UTF8String"
				else:
					# Modules who are compiled before that have to live with CStrings
					return "~MemPointer<ConstChar>"
			elif node.nodeValue == "true" or node.nodeValue == "false":
				return "Bool"
			elif node.nodeValue == "my":
				return self.currentClassImpl.getName()
			elif node.nodeValue == "null":
				return "MemPointer<void>"
			elif node.nodeValue in {"_bp_slice_start", "_bp_slice_end"}:
				return "Size"
			else:
				nodeName = node.nodeValue
				
				if nodeName in replacedNodeValues:
					nodeName = replacedNodeValues[nodeName]
				
				if node.nodeValue in self.tupleTypes:
					return self.tupleTypes[node.nodeValue]
				
				return self.getVariableTypeAnywhere(nodeName)
		else:
			# Binary operators
			if node.tagName == "new":
				typeNode = getElementByTagName(node, "type").childNodes[0]
				
				if isTextNode(typeNode):
					typeName = typeNode.nodeValue
				else:
					# Template parameters
					typeName = self.parseExpr(typeNode, True)
					
				# Check defines
				typeName = self.prepareTypeName(typeName)
					
				return typeName
					#return typeNode.childNodes[0].childNodes[0].nodeValue
			elif node.tagName == "call":
				if self.inFunction:
					# Recursive functions: Try to guess
					if self.currentFunction and getElementByTagName(node, "function").childNodes[0].nodeValue == self.currentFunction.getName():
						if self.currentFunctionImpl.returnTypes:
							return self.currentFunctionImpl.getReturnType()
						else:
							raise CompilerException("Unknown data type for recursive call: " + self.currentFunction.getName())
				
				return self.getCallDataType(node)
			elif node.tagName == "assign":
				op1 = node.childNodes[0].childNodes[0]
				
				if tagName(op1) == "declare-type":
					return self.parseExpr(op1.childNodes[1].firstChild)
				
				op2 = node.childNodes[1].childNodes[0]
				# TODO: Check for declare-type in op1
				return self.getExprDataType(op2)
			elif node.tagName == "access":
				caller = node.childNodes[0].childNodes[0]
				
				if caller.nodeType == Node.TEXT_NODE:
					#if caller.nodeValue == "loop":
					#	return "Size"
					
					if caller.nodeValue in self.compiler.mainClass.namespaces:
						#callerType = "bp_Namespace"
						#callerClassName = "bp_Namespace"
						varName = caller.nodeValue + "_" + node.childNodes[1].childNodes[0].nodeValue
						
						try:
							# Variables
							return self.getVariableTypeAnywhere(varName)
						except:
							# Functions
							virtualCall = self.makeXMLCall(varName)
							return self.getCallDataType(virtualCall)
				
				callerType = self.getExprDataType(caller)
				
				#while callerType in self.compiler.defines:
				#	callerType = self.compiler.defines[callerType]
				
				callerClassName = extractClassName(callerType)
				memberName = node.childNodes[1].childNodes[0].nodeValue
				memberName = self.fixMemberName(memberName)
				
				callerClass = self.getClass(callerClassName)
				
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
				
				#if memberName in callerClass.publicMembers:
				#	memberName = "_" + memberName
				#print(callerClassImpl.members)
				
				if memberName in callerClassImpl.members:
					#debug("Member '" + memberName + "' does exist")
					memberType = callerClassImpl.members[memberName].type
					#print(memberName)
					#print(memberType)
					#print(callerType)
					#print(callerClassName)
					#print(templateParams)
					#print("-----")
					return self.currentClassImpl.translateTemplateName(memberType)
				else:
					pass
					#debug("Member '" + memberName + "' doesn't exist")
					
					# data access from a pointer
					#print(callerClassName, memberName)
					if callerClassName == "MemPointer" and memberName == "data":
						return callerType[callerType.find('<')+1:-1]
					
					virtualGetCall = self.makeXMLObjectCall(node.childNodes[0].childNodes[0].toxml(), "get" + capitalize(memberName)) 
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
			elif node.tagName == "parameters":
				return "Tuple<%s>" % ', '.join([self.getExprDataType(x.firstChild) for x in node.childNodes])
			elif node.tagName == "slice":
				#           slice.value       .range        .from/to
				sliceFrom = node.childNodes[1].childNodes[0].childNodes[0].firstChild.toxml()
				sliceTo =   node.childNodes[1].childNodes[0].childNodes[1].firstChild.toxml()
				memberFunc = "operatorSlice"
				
				xmlCode = "<call><function><access><value>%s</value><value>%s</value></access></function><parameters><parameter>%s</parameter><parameter>%s</parameter></parameters></call>" % (node.childNodes[0].childNodes[0].toxml(), memberFunc, sliceFrom, sliceTo)
				return self.getCallDataType(self.cachedParseString(xmlCode).documentElement)
			elif node.tagName == "not":
				return "Bool"
				#return self.getExprDataType(node.childNodes[0].childNodes[0])
			elif node.tagName == "unmanaged":
				self.inUnmanaged += 1
				expr = self.getExprDataTypeClean(node.childNodes[0].childNodes[0])
				self.inUnmanaged -= 1
				return "~" + expr
			elif node.tagName == "negative":
				return self.getExprDataTypeClean(node.childNodes[0].childNodes[0])
			elif node.tagName == "exists-in":
				return "Bool"
			elif len(node.childNodes) == 2: # Any binary operation
				op1 = node.childNodes[0].childNodes[0]
				op2 = node.childNodes[1].childNodes[0]
				#op1Type = self.getExprDataType(op1)
				#op2Type = self.getExprDataType(op2)
				
				# Recursive functions: Try to guess
				if self.inFunction and self.currentFunction:
					# Is the second operator the recursive call?
					if tagName(op2) == "call" and getElementByTagName(op2, "function").childNodes[0].nodeValue == self.currentFunction.getName():
						op1Type = self.getExprDataType(op1)
						self.currentFunctionImpl.returnTypes.append(op1Type)
						return getHeavierOperator(op1Type, self.currentFunctionImpl.getReturnType())
						#if self.currentFunctionImpl.returnTypes:
						#	return self.currentFunctionImpl.getReturnType()
						#else:
						#	return op1Type
					# Is the first operator the recursive call?
					elif tagName(op1) == "call" and getElementByTagName(op1, "function").childNodes[0].nodeValue == self.currentFunction.getName():
						op2Type = self.getExprDataType(op2)
						self.currentFunctionImpl.returnTypes.append(op2Type)
						return getHeavierOperator(op2Type, self.currentFunctionImpl.getReturnType())
						#if self.currentFunctionImpl.returnTypes:
						#	return self.currentFunctionImpl.getReturnType()
						#else:
						#	return self.getExprDataType(op2)
				
				op1Type = self.getExprDataType(op1)
				op2Type = self.getExprDataType(op2)
				
				#if op1Type == "UTF8String" and op2Type in nonPointerClasses:
				#	return "UTF8String"
				
				# Subtraction should lead to a signed version
				if node.tagName == "subtract" and op1Type in nonPointerClasses and op2Type in nonPointerClasses:
					return self.getSignedVersion(op1Type)
				
				return self.getCombinationResult(node.tagName, op1Type, op2Type)
			
		raise CompilerException("Unknown data type for: " + node.toxml())
	
	def makeXMLCall(self, memberFunc, params = "<parameters/>"):
		xmlCode = "<call><function>%s</value></access></function>%s</call>" % (memberFunc, params)
		return self.cachedParseString(xmlCode).documentElement
	
	def makeXMLObjectCall(self, caller, memberFunc, params = "<parameters/>"):
		xmlCode = "<call><function><access><value>%s</value><value>%s</value></access></function>%s</call>" % (caller, memberFunc, params)
		return self.cachedParseString(xmlCode).documentElement
		
	def makeXMLAssign(self, op1, op2):
		xmlCode = "<assign><value>%s</value><value>%s</value></assign>" % (op1, op2)
		return self.cachedParseString(xmlCode).documentElement
	
	def getSignedVersion(self, typeName):
		if typeName in {"Float", "Float32", "Float64"}:
			return "Float"
		elif typeName in {"BigInt"}:
			return "BigInt"
		else:
			return "Int"
	
	#def cachedCallType(self, xmlCode):
	#	if xmlCode in self.compiler.virtualCallDataType:
	#		print("USING CALL TYPE CACHE")
	#		return self.compiler.virtualCallDataType[xmlCode]
	#	else:
	#		virtualCall = parseString(xmlCode).documentElement
	#		typeName = self.getCallDataType(virtualCall)
	#		self.compiler.virtualCallDataType[xmlCode] = typeName
	#		return typeName
	
	def cachedParseString(self, xmlCode):
		if xmlCode in self.compiler.parseStringCache:
			return self.compiler.parseStringCache[xmlCode]
		else:
			tmpDoc = parseString(xmlCode)
			self.compiler.parseStringCache[xmlCode] = tmpDoc
			return tmpDoc
	
	def getFunctionCallInfo(self, node):
		funcNameNode = getFuncNameNode(node)
		
		caller = ""
		callerType = ""
		if isTextNode(funcNameNode): #and funcNameNode.tagName == "access":
			funcName = funcNameNode.nodeValue
		else:
			#print("XML: " + funcNameNode.childNodes[0].childNodes[0].toxml())
			callerNode = funcNameNode.childNodes[0].childNodes[0]
			
			if callerNode.nodeValue in self.compiler.mainClass.namespaces:
				funcName = callerNode.nodeValue + "_" + funcNameNode.childNodes[1].childNodes[0].nodeValue
			else:
				callerType = self.getExprDataType(callerNode)
				caller = self.parseExpr(callerNode)
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
			elif operation == "less" or operation == "greater" or operation == "less-or-equal" or operation == "greater-or-equal" or operation == "equal" or operation == "not-equal" or operation == "almost-equal" or operation == "and" or operation == "or":
				return "Bool"
			else:
				return getHeavierOperator(operatorType1, operatorType2)
		else:
			operatorType1 = removeUnmanaged(operatorType1)
			operatorType2 = removeUnmanaged(operatorType2)
			
			if operatorType1.startswith("MemPointer"):
				if operation == "index":
					return operatorType1[len("MemPointer<"):-1]
				if operatorType2.startswith("MemPointer"):
					if operation == "subtract":
						return "Size"
				if operation == "add" or operation == "subtract":
					return operatorType1
				return self.getCombinationResult(operation, "Size", operatorType2)
			if operatorType2.startswith("MemPointer"):
				return self.getCombinationResult(operation, operatorType1, "Size")
			
			# TODO: Remove temporary fix
			if operation == "index":
				#if operatorType1.startswith("Array<"):
				#	return operatorType1[len("Array<"):-1]
				impl = self.implementFunction(operatorType1, "[]", [operatorType2])
				return impl.getReturnType()
			
			custom = self.implementFunction(operatorType1, correctOperators(operation), [operatorType2])
			if custom:
				return custom.getReturnType()
			
			raise CompilerException("Could not find an operator for the operation: " + operation + " " + operatorType1 + " " + operatorType2)
	
	def getVariableScopeAnywhere(self, name):
		scope = self.getVariableScope(name)
		if scope:
			return scope
		
		raise CompilerException("Unknown variable: %s" % name)
	
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
		
		if name in self.compiler.mainClass.externVariables:
			return self.compiler.mainClass.externVariables[name]
		
		#print(self.getTopLevelScope().variables)
		if name in self.compiler.mainClass.classes:
			raise CompilerException("You forgot to create an instance of the class '" + name + "' by using brackets")
		
		if name in self.compiler.mainClass.functions:
			raise CompilerException("A function call can only return a value if you use parentheses: '" + name + "()'")
		
		raise CompilerException("Unknown variable: " + name)
	
	def variableExistsAnywhere(self, name):
		if name in self.compiler.mainClassImpl.members:
			return 3
		
		if self.variableExists(name):
			return 1
		
		if name in self.currentClassImpl.members:
			return 2
		
		#print(name + " doesn't exist")
		return 0
	
	def classExists(self, className):
		if className == "":
			return True
		elif className in self.compiler.mainClass.classes:
			return True
		else:
			return False
	
	def isMemberAccessFromOutside(self, op1, op2):
		op1Type = self.getExprDataType(op1)
		op1ClassName = extractClassName(op1Type)
		#print(("get" + op2.nodeValue.capitalize()) + " -> " + str(self.compiler.mainClass.classes[op1Type].functions.keys()))
		
		if not op1ClassName in self.compiler.mainClass.classes:
			return False, False
		
		#if op2.nodeValue == "vertices":
		#	print("-" * 80)
		#	print(op1Type)
		#	print(op1ClassName)
		#	print("OP1:")
		#	print(op1.toprettyxml())
		#	print("OP2:")
		#	print(op2.toprettyxml())
		
		classObj = self.getClass(op1ClassName)
		funcs = classObj.functions
		prop = capitalize(op2.nodeValue)
		
		isPublicMember = classObj.hasPublicMember(op2.nodeValue)
		#print(classObj.name)
		#print(classObj.publicMembers)
		#print(prop)
		
		if isPublicMember:
			return False, True
		
		accessingGetter = ("get" + prop) in funcs
		accessingSetter = ("set" + prop) in funcs
		
		if isTextNode(op2) and (accessingGetter or accessingSetter or (op2.nodeValue in self.getClassImplementationByTypeName(op1Type).members)):
			#print(self.currentFunction.getName() + " -> " + "get" + capitalize(op2.nodeValue))
			#print(self.currentFunction.getName() == "get" + capitalize(op2.nodeValue))
			
			primaryObject = op1
			#while primaryObject.nodeType != Node.TEXT_NODE:
			#	primaryObject = primaryObject.firstChild
			
			if not (isTextNode(op1) and (primaryObject.nodeValue == "my")):
				# Make a virtual call
				#print("so true")
				return True, False
		
		#print("so false")
		return False, False
	
	def registerVariable(self, var):
		#var.name = self.getNamespacePrefix() + var.name
		#debug("Registered variable '" + var.name + "' of type '" + var.type + "'")
		self.getCurrentScope().variables[var.name] = var
		
		# Enable GMP when BigInt is used
		if var.type == "BigInt":
			self.compiler.gmpEnabled = True
		
		if self.getCurrentScope() == self.getTopLevelScope():# and not self.currentFunctionImpl:
			self.compiler.mainClassImpl.members[var.name] = var
		
		#self.currentClassImpl.addMember(var)
		
	def registerVariableFuncScope(self, var):
		#debug("Registered variable '" + var.name + "' of type '" + var.type + "' in function scope")
		self.currentFunctionImpl.scope.variables[var.name] = var
		self.currentFunctionImpl.declareVariableAtStart(var)
	
	def handleUnmanaged(self, node):
		self.inUnmanaged += 1
		expr = self.parseExpr(node.childNodes[0])
		self.inUnmanaged -= 1
		return "~" + expr
	
	def handleParallel(self, node):
		codeNode = getElementByTagName(node, "code")
		
		joinAll = getMetaData(node, "wait-for-all-threads") != "false" #isMetaDataTrueByTag(node, "wait-for-all-threads")
		
		self.parallelBlockStack.append(list())
		self.inParallel += 1
		#self.pushScope()
		code = self.parseChilds(codeNode, "\t" * self.currentTabLevel, self.lineLimiter)
		#self.popScope()
		self.inParallel -= 1
		
		block = self.parallelBlockStack.pop()
		
		if joinAll:
			code += self.waitCustomThreadsCode(block)
		
		return code
	
	def handleShared(self, node):
		codeNode = getElementByTagName(node, "code")
		
		self.inShared += 1
		code = self.parseChilds(codeNode, "\t" * self.currentTabLevel, self.lineLimiter)
		self.inShared -= 1
		
		return code
		
	def handleIn(self, node):
		exprNode = getElementByTagName(node, "expression")
		codeNode = getElementByTagName(node, "code")
		
		expr = self.parseExpr(exprNode.firstChild)
		exprType = self.getExprDataType(exprNode.firstChild)
		
		if exprType in nonPointerClasses:
			raise CompilerException("The class used for an 'in' block needs 'enter' and 'exit' methods which '%s' lacks" % exprType)
		
		classObj = self.getClass(extractClassName(exprType))
		if not (classObj.hasFunction("enter") and classObj.hasFunction("exit")):
			raise CompilerException("The class used for an 'in' block needs 'enter' and 'exit' methods which '%s' lacks" % exprType)
		
		self.implementFunction(exprType, "enter", [])
		self.implementFunction(exprType, "exit", [])
		
		#self.currentTabLevel += 1
		code = self.parseChilds(codeNode, "\t" * self.currentTabLevel, self.lineLimiter)
		#self.currentTabLevel -= 1
		
		# TODO: Check for enter/exit methods
		
		return self.buildInBlock(exprNode, expr, exprType, code, "\t" * self.currentTabLevel)
	
	def handleOn(self, node):
		exprNode = getElementByTagName(node, "expression").firstChild
		codeNode = getElementByTagName(node, "code")
		
		# TODO: C++ independent
		if exprNode.nodeType != Node.TEXT_NODE:
			value = self.parseExpr(exprNode)
			exprType = self.getExprDataType(exprNode)
			
			self.onVariable = "_bp_on_var_%d" % self.compiler.onVarCounter
			self.compiler.onVarCounter += 1
			
			var = self.createVariable(self.onVariable, exprType, value, False, not exprType in nonPointerClasses, False)
			self.registerVariable(var)
			
			code = "%s %s = %s;\n" % (self.adjustDataType(exprType), self.onVariable, value)
		else:
			self.onVariable = exprNode.nodeValue
			code = "// on '%s'\n" % self.onVariable
		
		code += self.parseChilds(codeNode, "\t" * self.currentTabLevel, self.lineLimiter)
		self.onVariable = ""
		
		return code
	
	def handleNamespace(self, node):
		# TODO: Fully implement namespaces
		name = getElementByTagName(node, "name").firstChild.nodeValue
		
		#print("Namespace %s" % name)
		
		self.pushNamespace(name)
		
		codeNode = getElementByTagName(node, "code")
		code = self.parseChilds(codeNode, "\t" * self.currentTabLevel, self.lineLimiter)
		
		self.popNamespace()
		
		return code
	
	def pushNamespace(self, name):
		self.namespaceStack.append(name)
		
		if not name in self.currentClass.namespaces:
			#debug("Adding new namespace to '%s': '%s'" % (self.currentClass.name, name))
			self.currentClass.namespaces[name] = self.createNamespace(name)
		else:
			pass#print("Namespace '%s' already exists!" % name)
		
	def popNamespace(self):
		self.namespaceStack.pop()
	
	def handleReturn(self, node):
		if node.childNodes:
			# THIS STEP MUST BE EXECUTED BEFORE expr = ... IS CALLED!
			# Recursive functions first need their data type value
			# THEN parseExpr -> implementFunction can be called
			retType = self.getExprDataType(node.childNodes[0])
			
			if self.currentFunctionImpl:
				self.currentFunctionImpl.returnTypes.append(retType)
			
			# Multiple return values
			if node.firstChild.nodeType != Node.TEXT_NODE and node.firstChild.tagName == "parameters":
				#typesAndValues = map(lambda x: (self.getExprDataType(x.firstChild), self.parseExpr(x.firstChild)), node.firstChild.childNodes)
				paramTypes = [self.getExprDataType(x.firstChild) for x in node.firstChild.childNodes]
				values = [self.parseExpr(x.firstChild) for x in node.firstChild.childNodes]
				
				typeId = "_".join(paramTypes)
				
				structName = "BPTuple_%s_" % (typeId)
				
				paramNames, structCode = self.buildStruct(structName, paramTypes, True)
				
				self.tuples[typeId] = structCode
				self.compiler.tuples[typeId] = True
				
				return self.returnSyntax % (self.newObjectSyntax % (structName, ', '.join(values)))
			else:
				# STEP 2
				expr = self.parseExpr(node.firstChild, False)
				
				if retType == "void":
					raise CompilerException("'%s' doesn't return a value" % nodeToBPC(node.childNodes[0]))
					
				#debug("Returning '%s' with type '%s' on current func '%s' with implementation '%s'" % (expr, retType, self.currentFunction.getName(), self.currentFunctionImpl.getName()))
				if self.currentFunction and self.currentFunction.hasDataFlow:
					#print("[DATAFLOW] Returning '%s' with type '%s' on current func '%s' with implementation '%s'" % (expr, retType, self.currentFunction.getName(), self.currentFunctionImpl.getName()))
					return self.buildFunctionDataFlowOnReturn(node, expr, self.currentFunctionImpl)
				
				return self.returnSyntax % expr
		else:
			retType = "void"
			return "return"
		
	def handleYield(self, node):
		if node.childNodes:
			yieldType = self.getExprDataType(node.childNodes[0])
			self.currentFunctionImpl.yieldType = yieldType
			
			# STEP 2
			yieldValue = self.parseExpr(node.childNodes[0], False)
			
			if yieldType == "void":
				raise CompilerException("'%s' doesn't return a value" % nodeToBPC(node.childNodes[0]))
				
			#debug("Returning '%s' with type '%s' on current func '%s' with implementation '%s'" % (expr, retType, self.currentFunction.getName(), self.currentFunctionImpl.getName()))
			return self.yieldSyntax % yieldValue
		else:
			raise CompilerException("The 'yield' keyword needs an expression which is processed in each loop iteration")
			#retType = "void"
			#return "return"
	
	def handleParameters(self, pNode):
		pList = []
		pTypes = []
		
		# For slicing:
		#<parameter>						= node
		#	<slice>							= node.firstChild
		#		<value>a</value>			= node.firstChild.firstChild
		#		<value>						= node.firstChild.childNodes[1]
		#			<range>					= node.firstChild.childNodes[1].firstChild
		#				<from>2</from>
		#				<to>3</to>
		#			</range>
		#		</value>
		#	</slice>
		#</parameter>
		
		# Faster lookups
		parseExpr = self.parseExpr
		prepareTypeName = self.prepareTypeName
		getExprDataType = self.getExprDataType
		pTypesAppend = pTypes.append
		pListAppend = pList.append
		
		for node in pNode.childNodes:
			paramType = getExprDataType(node.childNodes[0])
			
			# Typedefs
			paramType = prepareTypeName(paramType)
			
			#paramType = self.translateTemplateParam(paramType)
			pListAppend(parseExpr(node.childNodes[0]))
			pTypesAppend(paramType)
		
		return ", ".join(pList), pTypes
	
	def getClass(self, className):
		if className == "":
			return self.compiler.mainClass
		elif className in self.compiler.specializedClasses:
			return self.compiler.specializedClasses[className]
		elif className in self.compiler.mainClass.classes:
			return self.compiler.mainClass.classes[className]
		else:
			raise CompilerException("Class '%s' has not been defined  [Error code 3]" % (className))
		
	def getClassImplementationByTypeName(self, typeName, initTypes = []):
		className = extractClassName(typeName)
		templateValues = extractTemplateValues(typeName)
		return self.getClass(className).requestImplementation(initTypes, splitParams(templateValues))
		
	def getParameterList(self, pNode):
		if pNode is None:
			return [], [], [], []
		
		pList = []
		pTypes = []
		pDefault = []
		pDefaultTypes = []
		
		# Faster lookups
		pListAppend = pList.append
		pTypesAppend = pTypes.append
		pDefaultAppend = pDefault.append
		pDefaultTypesAppend = pDefaultTypes.append
		textNodeType = Node.TEXT_NODE
		translateTemplateName = self.currentClassImpl.translateTemplateName
		addMissingTemplateValues = self.addMissingTemplateValues
		prepareTypeName = self.prepareTypeName
		implementFunction = self.implementFunction
		addDefaultParameters = self.addDefaultParameters
		parseExpr = self.parseExpr
		
		for node in pNode.childNodes:
			name = ""
			type = ""
			defaultValue = ""
			defaultValueType = ""
			
			exprNode = node.childNodes[0]
			
			if exprNode.nodeType == textNodeType:
				name = exprNode.nodeValue
			elif exprNode.tagName == "name":
				name = exprNode.childNodes[0].nodeValue
				defaultValue = self.parseExpr(node.childNodes[1].childNodes[0])
			elif exprNode.tagName == "access":
				name = "__" + exprNode.childNodes[1].childNodes[0].nodeValue
			elif exprNode.tagName == "assign":
				if tagName(exprNode.childNodes[0].childNodes[0]) == "declare-type":
					name2 = self.parseExpr(exprNode.childNodes[0].childNodes[0].firstChild.firstChild)
					name, type = self.getTypeDeclInfo(exprNode.childNodes[0].childNodes[0])
					#print(name, name2, name == name2)
				else:
					name = self.parseExpr(exprNode.childNodes[0].childNodes[0])
				
				if name.startswith(self.memberAccessSyntax):
					member = name[len(self.memberAccessSyntax):]
					#self.currentClassImpl.addMember(self.createVariable(member, usedAs, "", False, not usedAs in nonPointerClasses, False))
					name = "__" + member
				
				defaultValue = self.parseExpr(exprNode.childNodes[1].childNodes[0])
				defaultValueType = self.getExprDataType(exprNode)
				
				#if declTypeFlag:
				#	exprNode = exprNode.childNodes[0].childNodes[0]
				
				# TODO: declare-type
				#type = defaultValueType
			elif exprNode.tagName == "declare-type":
				name, type = self.getTypeDeclInfo(exprNode)
				
				# Typedefs
				#type = prepareTypeName(type)
				
				#if typeNode.childNodes and isElemNode(typeNode) and typeNode.tagName == "unmanaged":
				#	type = "~" + type
			else:
				raise CompilerException("Invalid parameter %s" % (exprNode.toxml()))
			
			if name in replacedNodeValues:
				name = replacedNodeValues[name]
			
			pListAppend(name)
			
			type = translateTemplateName(type)
			type = addMissingTemplateValues(type)
			type = prepareTypeName(type)
			
			# Use default value type if not set
			#if not type and defaultValueType:
			#	type = defaultValueType
			
			# Implement it
			if not type in nonPointerClasses:
				try:
					#classImpl = self.getClassImplementationByTypeName(type)
					#classImpl.requestFuncImplementation("init", [])
					
					# Default parameters for init
					paramTypes, paramsString = addDefaultParameters(type, "init", [], "")
					funcImpl = implementFunction(type, "init", paramTypes)
				except:
					pass
			
			pTypesAppend(type)
			pDefaultAppend(defaultValue)
			pDefaultTypesAppend(defaultValueType)
		
		return pList, pTypes, pDefault, pDefaultTypes
	
	def getTypeDeclInfo(self, exprNode):
		op1 = exprNode.childNodes[0].childNodes[0]
		if isElemNode(op1) and op1.tagName == "access":
			accessingObject = self.parseExpr(op1.childNodes[0].childNodes[0])
			accessingMember = self.parseExpr(op1.childNodes[1].childNodes[0])
			if accessingObject == self.myself:
				name = "__" + accessingMember
			else:
				raise CompilerException("'%s.%s' may not be used as a function parameter" % (accessingObject, accessingMember))
		else:
			name = self.parseExpr(op1)
		
		typeNode = exprNode.childNodes[1].childNodes[0]
		type = self.parseExpr(typeNode, True)
		
		return name, type
	
	def parseChilds(self, parent, prefix = "", postfix = ""):
		lines = []
		parseExpr = self.parseExpr
		
		for node in parent.childNodes:
			line = parseExpr(node)
			
			self.lastParsedNode.pop()
			
			if self.additionalCodePerLine:
				line = "%s%s%s%s" % ((postfix + prefix).join(self.additionalCodePerLine), postfix, prefix, line)
				self.additionalCodePerLine = []
				
			if line:
				lines.append(prefix)
				lines.append(line)
				lines.append(postfix)
		
		# Save scope for the IDE
		#if parent.tagName == "code":
		#self.saveScopesForNode(parent)
		
		return ''.join(lines)
	
	def parseExpr(self, node, keepUnmanagedSign = True):
		# Set last node for debugging purposes
		self.lastParsedNode.append(node)
		
		if not keepUnmanagedSign:
			expr = self.parseExpr(node, True)
			# Remove unmanaged sign
			if len(expr) and expr[0] == "~":
				return expr[1:]
			return expr
		
		# Return text nodes directly (if it is not a string)
		if isTextNode(node):
			if node.nodeValue.startswith("bp_string_"):
				return self.id + "_" + node.nodeValue
			else:
				if node.nodeValue == "my":
					if self.useGC:
						return self.myself
					# TODO: Make sure the algorithm to find out whether 'self' is being used solely works 100%
					#opNode = node.parentNode.parentNode
					#numChildNodes = len(opNode.childNodes)
					#if numChildNodes > 1:
					#	return self.myself
					#else:
						# TODO: Unmanaged object initiations need to return 'this'
					#	return "shared_from_this()"
				#elif node.nodeValue == "null":
				#	return "NULL"
				# BigInt support
				elif node.nodeValue.isdigit():
					num = int(node.nodeValue)
					if num > INT32_MAX or num < INT32_MIN:
						return "(BigInt)(\"" + str(num) + "\")"
					else:
						return str(num)
				elif "." in node.nodeValue:
					return self.buildFloat(node.nodeValue)
				elif node.nodeValue == "true":
					return self.buildTrue()
				elif node.nodeValue == "false":
					return self.buildFalse()
				elif node.nodeValue == "null":
					return self.buildNull()
				#elif node.nodeValue == "_bp_slice_end":
				#	declTypeNode = node.parentNode.parentNode
				#	sliceNode = declTypeNode.parentNode.parentNode
				#	sliceOn	
				elif node.nodeValue in replacedNodeValues:
					nodeName = node.nodeValue
					nodeName = replacedNodeValues[node.nodeValue]
					return nodeName
				else:
					return node.nodeValue
		
		tagName = node.tagName
		
		# Check which kind of tag it is
		if tagName in self.directMapping:
			func = self.directMapping[tagName]
			
			if func:
				return func(node)
			else:
				return ""
		elif tagName == "value":
			return self.parseExpr(node.childNodes[0])
		elif tagName == "if-block" or tagName == "try-block":
			return self.parseChilds(node, "", "")
		# exists-in
		elif tagName == "exists-in":
			op1 = node.childNodes[0].firstChild
			op2 = node.childNodes[1].firstChild
			
			memberFunc = "contains"
			virtualCall = self.cachedParseString("<call><function><access><value>%s</value><value>%s</value></access></function><parameters><parameter>%s</parameter></parameters></call>" % (op2.toxml(), memberFunc, op1.toxml())).documentElement
			
			return self.handleCall(virtualCall)
		elif tagName == "parameters":
			return self.parseChilds(node, "", ", ")[:-2]
		elif tagName == "parameter":
			if getElementByTagName(node, "default-value"):
				return self.parseExpr(node.childNodes[0].childNodes[0])
			return self.parseExpr(node.childNodes[0])
		# Assign-add for Strings
		elif tagName == "assign-add":
			# So damn hardcoded...
			op1 = node.childNodes[0].firstChild
			op2 = node.childNodes[1].firstChild
			dataType = self.getExprDataType(op1)
			
			# TODO: Check whether the class has a += operator and if not, use this:
			if dataType == "UTF8String":
				lValue = self.parseExpr(op1)
				#rValue = self.parseExpr(op2)
				#return "%s = %s->operatorAdd__UTF8String(%s)" % (lValue, lValue, rValue)
				memberFunc = "+"
				virtualAddCall = self.cachedParseString("<call><operator><access><value>%s</value><value>%s</value></access></operator><parameters><parameter>%s</parameter></parameters></call>" % (op1.toxml(), memberFunc, op2.toxml())).documentElement
				
				return "%s = %s" % (lValue, self.handleCall(virtualAddCall))
		elif tagName in enableOperatorOverloading:
			caller = self.parseExpr(node.childNodes[0].childNodes[0])
			callerType = self.getExprDataType(node.childNodes[0].childNodes[0])
			callerClassName = extractClassName(callerType)
			#valueType = self.getExprDataType(node.childNodes[1].childNodes[0])
			
			if callerClassName == "void":
				funcName = node.childNodes[0].childNodes[0].childNodes[0].childNodes[0].nodeValue
				raise CompilerException("Function '%s' has no return value" % funcName)
			
			if callerClassName in nonPointerClasses:
				pass#return "(%s+%s)" % (caller, op2)
			elif callerClassName == "MemPointer": #and isUnmanaged(callerType):
				pass#return "(%s + %s)" % (caller, op2)
			else:#if correctOperators(tagName) in self.getClassImplementationByTypeName(callerType).funcImplementations:
				memberFunc = correctOperators(tagName)
				if (not callerType in nonPointerClasses) and self.getClass(callerClassName).hasFunction(memberFunc):
					virtualIndexCall = self.cachedParseString("<call><operator><access><value>%s</value><value>%s</value></access></operator><parameters><parameter>%s</parameter></parameters></call>" % (node.childNodes[0].childNodes[0].toxml(), memberFunc, node.childNodes[1].childNodes[0].toxml())).documentElement
					
					call = self.handleCall(virtualIndexCall)
					return call
				 
		#elif tagName == "not":
		#	return "!" + self.parseChilds(node)
		elif tagName == "index":
			caller = self.parseExpr(node.childNodes[0].childNodes[0])
			callerType = self.getExprDataType(node.childNodes[0].childNodes[0])
			index = self.parseExpr(node.childNodes[1].childNodes[0])
			callerClassName = extractClassName(callerType)
			
			if callerClassName == "MemPointer": #and isUnmanaged(callerType):
				return "%s[%s]" % (caller, index)
			
			memberFunc = "[]"
			virtualIndexCall = self.cachedParseString("<call><operator><access><value>%s</value><value>%s</value></access></operator><parameters><parameter>%s</parameter></parameters></call>" % (node.childNodes[0].childNodes[0].toxml(), memberFunc, node.childNodes[1].childNodes[0].toxml())).documentElement
			
			return self.handleCall(virtualIndexCall)
		elif tagName == "test":
			if self.isMainFile and node.parentNode.parentNode.tagName == "module":
				return self.parseChilds(node.firstChild, "\t" * self.currentTabLevel, self.lineLimiter)
			return ""
		elif tagName == "not":
			return self.buildNegation(self.parseExpr(node.firstChild))
		elif tagName == "throw":
			return self.throwSyntax % self.parseExpr(node.firstChild)
		elif tagName == "include":
			fileName = node.childNodes[0].nodeValue
			incFile = (self.dir + fileName)[len(self.compiler.modDir):]
			ifndef = normalizeModPath(incFile).replace(".", "_")
			self.includes.append((incFile, ifndef)) #+= "#include \"" + node.childNodes[0].nodeValue + "\"\n"
			self.compiler.includes.append((incFile, ifndef))
			return ""
		elif node.tagName == "declare-type":
			if node.parentNode.tagName == "code":
				self.handleTypeDeclaration(node)
				return ""
			
			name = self.handleTypeDeclaration(node, insertTypeName = True)
			#print(name)
			return name
		elif node.tagName == "slice":
			#           slice.value       .range        .from/to
			sliceFrom = node.childNodes[1].childNodes[0].childNodes[0].firstChild.toxml()
			sliceTo =   node.childNodes[1].childNodes[0].childNodes[1].firstChild.toxml()
			
			memberFunc = "operatorSlice"
			
			if sliceFrom == "_bp_slice_start":
				sliceFrom = "0"
			
			if sliceTo == "_bp_slice_end":
				virtualSliceCall = self.cachedParseString("<call><function><access><value>%s</value><value>%s</value></access></function><parameters><parameter>%s</parameter></parameters></call>" % (node.childNodes[0].childNodes[0].toxml(), memberFunc, sliceFrom)).documentElement
			else:
				# Call with 2 parameters
				virtualSliceCall = self.cachedParseString("<call><function><access><value>%s</value><value>%s</value></access></function><parameters><parameter>%s</parameter><parameter>%s</parameter></parameters></call>" % (node.childNodes[0].childNodes[0].toxml(), memberFunc, sliceFrom, sliceTo)).documentElement
			
			return self.handleCall(virtualSliceCall)
		elif node.tagName == "compiler-flags":
			return self.parseChilds(node, "", "")
		elif tagName == "break":
			return "break"
		elif tagName == "noop":
			return self.buildNOOP()
		
		# Check parameterized blocks
		if tagName in self.paramBlocks:
			paramBlock = self.paramBlocks[node.tagName]
			keywordName = paramBlock[0]
			paramTagName = paramBlock[1]
			codeTagName = paramBlock[2]
			
			#if isElemNode(getElementByTagName(node, paramTagName)):
			#	print(getElementByTagName(node, paramTagName).childNodes[0].toprettyxml())
			
			condition = self.parseExpr(getElementByTagName(node, paramTagName).childNodes[0])
			
			self.pushScope()
			code = self.parseChilds(getElementByTagName(node, codeTagName), "\t" * self.currentTabLevel, self.lineLimiter)
			self.popScope()
			
			return self.buildParamBlock(keywordName, condition, code, "\t" * self.currentTabLevel)
		
		# Check operators
		if tagName in self.compiler.operators:
			op = self.compiler.operators[tagName]
			
			if op.type == Operator.BINARY:
				if op.text == "\\":
					return self.parseBinaryOperator(node, " / ", True)
				return self.parseBinaryOperator(node, " %s " % op.text, True)
			elif op.type == Operator.UNARY:
				return "%s(%s)" % (op.text, self.parseExpr(node.childNodes[0]))
		
		return ""
	
	def handleAccess(self, node):
		op1 = node.childNodes[0].childNodes[0]
		op2 = node.childNodes[1].childNodes[0]
		
		if op1.nodeType == Node.TEXT_NODE:
			if op1.nodeValue in self.compiler.mainClass.namespaces:
				return op1.nodeValue + "_" + self.parseExpr(op2)
				
			#if op1.nodeValue == "loop":
			#	if op2.nodeType != Node.TEXT_NODE or op2.nodeValue != "counter":
			#		raise CompilerException("You probably meant 'loop.counter'")
			#	
			#	self.currentLoopUsesCounter += 1
			#	return "_bp_loop_counter_%d" % (self.compiler.forVarCounter)
		
		callerType = self.getExprDataType(op1)
		callerClassName = extractClassName(callerType)
		
		if callerClassName in self.compiler.mainClass.classes:
			if callerClassName == "MemPointer" and isTextNode(op2):
				if op2.nodeValue == "data":
					return "(*(%s))" % (self.parseExpr(op1))
			# TODO: Optimize
			# GET access
			isMemberAccess, publicMemberAccess = self.isMemberAccessFromOutside(op1, op2)
			if isMemberAccess:
				#print("Replacing ACCESS with CALL: %s.%s" % (op1.toxml(), "get" + op2.nodeValue.capitalize()))
				#if isTextNode(op1) and op1.nodeValue == "my":
				#	op1xml = "this"
				#else:
				op1xml = op1.toxml()
				
				getFunc = self.cachedParseString("<call><function><access><value>%s</value><value>%s</value></access></function><parameters/></call>" % (op1xml, "get" + capitalize(op2.nodeValue))).documentElement
				#print(getFunc.toprettyxml())
				return self.handleCall(getFunc)
			elif publicMemberAccess:
				# Public member access
				return self.parseBinaryOperator(node, self.ptrMemberAccessChar + "_")
		
		return self.parseBinaryOperator(node, self.ptrMemberAccessChar)
	
	def isDerivedClass(self, typeA, typeB):
		try:
			typeAClassImpl = self.getClassImplementationByTypeName(typeA)
			typeAClass = typeAClassImpl.classObj
			
			typeBClassImpl = self.getClassImplementationByTypeName(typeB)
		except:
			# Classes are not defined yet
			return False
		
		#print(typeAClass.extends)
		#print(">>>", typeAClass.name, typeBClassImpl.getName(), "->", typeBClassImpl in typeAClass.extends)
		
		if typeBClassImpl in typeAClass.extends:
			return True
		else:
			return False
	
	def prepareTypeName(self, typeName):
		#print("PREPARE: " + typeName)
		while typeName in self.compiler.defines:
			typeName = self.compiler.defines[typeName]
		
		pos = typeName.find("<")
		if pos != -1:
			templateParts = []
			for param in splitParams(typeName[pos + 1:-1]):
				templateParts.append(self.prepareTypeName(param))
			
			typeName = typeName[:pos]
			templatePart = "<" + ", ".join(templateParts) + ">"
		else:
			templatePart = ""
		
		if typeName in self.compiler.specializedClasses:
			typeName = self.compiler.specializedClasses[typeName].name
		
		#print("PREPARED: " + typeName + templatePart)
		return typeName + templatePart
	
	def scanAhead(self, parent):
		for node in parent.childNodes:
			if isElemNode(node):
				if node.tagName == "class":
					self.scanClass(node)
				elif node.tagName == "function" or node.tagName == "operator" or node.tagName == "iterator-type":
					self.scanFunction(node)
				elif node.tagName == "getter":
					self.inGetter += 1
					result = self.scanFunction(node)
					self.inGetter -= 1
				elif node.tagName == "setter":
					self.inSetter += 1
					result = self.scanFunction(node)
					self.inSetter -= 1
				elif node.tagName == "cast-definition":
					self.inCastDefinition += 1
					result = self.scanFunction(node)
					self.inCastDefinition -= 1
				elif node.tagName == "public-member":
					self.scanPublicMember(node)
				elif node.tagName == "namespace":
					self.scanNamespace(node)
				elif node.tagName == "extern":
					self.inExtern += 1
					self.scanAhead(node)
					self.inExtern -= 1
				elif node.tagName == "operators":
					self.inOperators += 1
					self.scanAhead(node)
					self.inOperators -= 1
				elif node.tagName == "iterators":
					self.inIterators += 1
					self.scanAhead(node)
					self.inIterators -= 1
				elif node.tagName == "casts":
					self.inCasts += 1
					self.scanAhead(node)
					self.inCasts -= 1
				elif node.tagName == "define":
					self.inDefine += 1
					self.scanAhead(node)
					self.inDefine -= 1
				elif node.tagName == "public":
					self.scanAhead(node)
				#elif node.tagName == "default-get":
				#	self.scanDefaultGet(node)
				#elif node.tagName == "default-set":
				#	self.scanDefaultSet(node)
				elif node.tagName == "get" or node.tagName == "set":
					self.scanAhead(node)
				elif node.tagName == "template":
					self.inTemplate += 1
					self.scanTemplate(node)
					self.inTemplate -= 1
				elif node.tagName == "extends":
					self.inExtends += 1
					self.scanExtends(node)
					self.inExtends -= 1
				elif node.tagName == "extern-function":
					self.scanExternFunction(node)
				elif node.tagName == "extern-variable":
					self.scanExternVariable(node)
				elif node.tagName == "const":
					self.scanAhead(node)
				elif node.tagName == "assign" and self.inDefine > 0:
					self.scanDefine(node)
	
	def implementFunction(self, typeName, funcName, paramTypes):
		#if funcName == "init":
		#	print("%s.%s(%s)" % (typeName, funcName, ", ".join(paramTypes)))
			#classImpl = self.getClassImplementationByTypeName(typeName)
			#classImpl.initCallTypes = paramTypes
		funcName = correctOperators(funcName)
		
		# For casts
		#while funcName in self.compiler.defines:
		#	funcName = self.compiler.defines[funcName]
		
		key = typeName + "." + funcName + "(" + ", ".join(paramTypes) + ")"
		
		if key in self.compiler.funcImplCache:
			return self.compiler.funcImplCache[key]
		
		className = extractClassName(typeName)
		if className in nonPointerClasses:
			raise CompilerException("'%s' has not been defined (maybe another function returns the wrong value?)" % (key))
		
		#print(funcName, "|", className, "|", key)
		if not funcName in self.getClass(className).functions:
			classImpl = self.getClassImplementationByTypeName(typeName)
			tmpFunc, baseClassImpl = findFunctionInBaseClasses(classImpl, funcName)
			
			if not tmpFunc:
				if not self.compiler.background:
					print(className + " contains the following functions:")
					print(" * " + "\n * ".join(self.getClass(className).functions.keys()))
					
				# TODO: Check for an iterator used in the wrong place and show another exception
				raise CompilerException("The '%s' function of class '%s' has not been defined" % (funcName, className))
		
		func = self.getClassImplementationByTypeName(typeName).getMatchingFunction(funcName, paramTypes)
		definedInFile = func.cppFile
		
		# Default parameters
		#paramTypesLen = len(paramTypes)
		#paramDefaultValueTypes = func.getParamDefaultValueTypes()
		#paramDefaultValueTypesLen = len(paramDefaultValueTypes)
		#if paramTypesLen < paramDefaultValueTypesLen:
		#	paramTypes += paramDefaultValueTypes[paramTypesLen:paramDefaultValueTypesLen]
		
		# Push
		oldFunc = definedInFile.currentFunction
		
		# Implement
		definedInFile.currentFunction = func
		if func.isIterator:
			definedInFile.stringClassDefined = True
		funcImpl = definedInFile.implementLocalFunction(typeName, funcName, paramTypes)
		
		# Pop
		definedInFile.currentFunction = oldFunc
		
		if className == "":
			prototype = funcImpl.getPrototype()
			self.prototypesHeader += prototype
			self.compiler.prototypes.append(prototype)
		
		#if func and funcImpl and funcImpl.getReturnType() != "void":
		self.compiler.funcImplCache[key] = funcImpl
		
		return funcImpl
	
	def implementLocalFunction(self, typeName, funcName, paramTypes):
		className = extractClassName(typeName)
		
		# Save values
		oldGetter = self.inGetter
		oldSetter = self.inSetter
		oldOperator = self.inOperator
		oldCastDefinition = self.inCastDefinition
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
		elif node.tagName == "cast-definition":
			self.inCastDefinition += 1
		
		if self.inCastDefinition:
			# For casts
			funcName = self.prepareTypeName(funcName)
		
		# Implement it
		funcImpl, codeExists = self.currentClassImpl.requestFuncImplementation(funcName, paramTypes)
		self.currentFunctionImpl = funcImpl
		
		if not codeExists:
			funcNode = funcImpl.func.node
			codeNode = getElementByTagName(funcNode, "code")
			
			#debug("Before:")
			#self.debugScopes()
			#debugPush()
			
			self.saveScopes()
			self.scopes = self.scopes[:1]
			
			self.pushScope()
			
			if typeName: #and not self.variableExistsAnywhere("my"):
				# TODO: removeUnmanaged(typeName) ? yes/no?
				self.registerVariable(self.createVariable("my", typeName, "", False, True, False))
			parameters, funcStartCode = self.getParameterDefinitions(getElementByTagName(funcNode, "parameters"), paramTypes, funcImpl.func.getParamDefaultValueTypes())
			
			#  * self.currentTabLevel
			oldTabLevel = self.currentTabLevel
			if typeName:
				self.currentTabLevel = 2
			else:
				self.currentTabLevel = 1
			
			# Set scope
			funcImpl.setScope(self.getCurrentScope())
			
			# Here we parse the actual code node
			funcImplCode = self.parseChilds(codeNode, "\t" * self.currentTabLevel, self.lineLimiter)
			
			# Variables used in deeper scopes need to be initialized at the beginning
			varsAtStart = []
			for var in funcImpl.variablesAtStart:
				varsAtStart.append("\t" * self.currentTabLevel)
				varsAtStart.append(var.getPrototype())
				varsAtStart.append(";\n")
			varsAtStartCode = ''.join(varsAtStart)
			#print(varsAtStartCode)
			
			# Set code
			funcImpl.setCode(funcStartCode + varsAtStartCode + funcImplCode)
			
			self.currentTabLevel = oldTabLevel - 1
			
			self.restoreScopes()
			
			#debugPop()
			#debug("After:")
			#self.debugScopes()
		
		# Load previous values
		self.inFunction -= 1
		self.currentFunction = oldFunction
		self.currentFunctionImpl = oldFunctionImpl
		self.inGetter = oldGetter
		self.inSetter = oldSetter
		self.inOperator = oldOperator
		self.inCastDefinition = oldCastDefinition
		self.currentClass = oldClass
		self.currentClassImpl = oldImpl
		
		return funcImpl
	
	def addDefaultParameters(self, typeName, funcName, paramTypes, paramsString):
		func = self.getClassImplementationByTypeName(typeName).getMatchingFunction(funcName, paramTypes)
		#if not func:
		#	raise CompilerException("Couldn't")
		
		paramTypesLen = len(paramTypes)
		paramDefaultValues = func.getParamDefaultValues()
		paramDefaultValueTypes = func.getParamDefaultValueTypes()
		paramDefaultValuesLen = len(paramDefaultValues)
		if paramTypesLen < paramDefaultValuesLen:
			if paramsString:
				paramsString += ", "
			paramTypes += paramDefaultValueTypes[paramTypesLen:paramDefaultValuesLen]
			paramsString += ", ".join(paramDefaultValues[paramTypesLen:paramDefaultValuesLen])
		
		return paramTypes, paramsString
	
	def handleTarget(self, node):
		name = getElementByTagName(node, "name").childNodes[0].nodeValue
		if name == self.compiler.getTargetName() or matchesCurrentPlatform(name):
			return "\n" + self.parseChilds(getElementByTagName(node, "code"), "\t" * self.currentTabLevel, self.lineLimiter)
	
	def handleImport(self, node):
		importedModulePath = node.childNodes[0].nodeValue.strip()
		importedModule = getModulePath(importedModulePath, extractDir(self.file), self.compiler.getProjectDir(), ".bp")
		return self.buildModuleImport(importedModule)
	
	def handleElse(self, node):
		self.pushScope()
		code = self.parseChilds(getElementByTagName(node, "code"), "\t" * self.currentTabLevel, self.lineLimiter)
		self.popScope()
		
		return self.elseSyntax % (code, "\t" * self.currentTabLevel)
	
	def handleString(self, node):
		stringId = node.getAttribute("id")
		id = self.id + "_" + stringId
		value = decodeCDATA(node.childNodes[0].nodeValue)
		
		asByte = node.getAttribute("as-byte")
		
		if asByte == "true":
			dataType = "Byte"
			line = self.buildStringAsByte(id, value)
			self.stringsAsBytes[stringId] = True
			#print(self.stringsAsBytes)
		else:
			dataType = self.compiler.stringDataType
			line = self.buildString(id, value)
		
		# TODO: classExists(self.compiler.stringDataType)
		#if 1:#self.stringClassDefined or value == "\\n":
		#	dataType = self.compiler.stringDataType
		#	line = self.buildString(id, value)
		#else:
		#	dataType = "CString"
		#	line = self.buildUndefinedString(id, value)
		
		var = self.createVariable(id, dataType, value, False, False, True)
		#self.currentClassImpl.addMember(var)
		self.getTopLevelScope().variables[id] = var
		self.compiler.stringCounter += 1
		
		return line
	
	def handleTemplateCall(self, node):
		op1 = self.parseExpr(node.childNodes[0].childNodes[0])
		op2 = self.parseExpr(node.childNodes[1].childNodes[0])
		
		# Template translation
		op1 = self.currentClassImpl.translateTemplateName(op1)
		op2 = self.currentClassImpl.translateTemplateName(op2)
		
		op2 = self.prepareTypeName(op2)
		
		# Check whether the class really exists
		if (not op2 in nonPointerClasses) and (not op2 == "MemPointer"):
			self.getClassImplementationByTypeName(op2)
		
		return self.buildTemplateCall(op1, op2)
		
	def handleConst(self, node):
		self.inConst += 1
		code = self.parseChilds(node, "\t" * self.currentTabLevel, self.lineLimiter)
		self.inConst -= 1
		
		return code
	
	def isInvalidType(self, typeNode):
		return (not isTextNode(typeNode)) and (not typeNode.tagName in {"template-call", "unmanaged"})
	
	def handleTypeDeclaration(self, node, insertTypeName = True):
		self.inTypeDeclaration += 1
		
		typeNode = node.childNodes[1]
		if self.isInvalidType(typeNode.firstChild):
			raise CompilerException("Invalid type definition in '%s'" % nodeToBPC(node))
		
		typeName = self.parseExpr(typeNode, True)
		
		# Typedefs
		typeName = self.prepareTypeName(typeName)
		
		typeName = self.currentClassImpl.translateTemplateName(typeName)
		varName = self.parseExpr(node.childNodes[0])
		self.inTypeDeclaration -= 1
		
		# Implement it
		#if not typeName in nonPointerClasses:
		#	try:
		#		self.getClassImplementationByTypeName(typeName)
		#	except:
		#		pass
		
		if varName.startswith(self.memberAccessSyntax):
			memberName = varName[len(self.memberAccessSyntax):]
			memberName = self.fixMemberName(memberName)
			
			self.currentClassImpl.addMember(self.createVariable(memberName, typeName, "", False, not extractClassName(typeName) in nonPointerClasses, False))
			return self.buildMemberTypeDeclInConstructor(varName) # ""
		
		variableExists = self.variableExistsAnywhere(varName)
		if variableExists and (self.getVariableScope(varName) == self.getTopLevelScope()):
			#["local", "global"][self.getVariableScopeAnywhere(varName) == self.getTopLevelScope()]
			for item in self.scopes:
				print(item.variables)
				print("===")
			raise CompilerException("'" + varName + "' has already been defined as a %s variable of the type '" % (["local", "class", "global"][variableExists - 1]) + self.getVariableTypeAnywhere(varName) + "'")
		else:
			#debug("Declaring '%s' as '%s'" % (varName, typeName))
			var = self.createVariable(varName, typeName, "", self.inConst, not typeName in nonPointerClasses, False)
			self.registerVariable(var)
			
			if insertTypeName:
				return self.buildTypeDeclaration(typeName, varName)
			else:
				return self.buildTypeDeclarationNameOnly(varName)
	
	def getFunction(self, name):
		return self.compiler.mainClass.functions[name]
	
	def handleFlowTo(self, node):
		op1 = node.childNodes[0].childNodes[0]
		op2 = node.childNodes[1].childNodes[0]
		
		code = []
		
		# If the left operator is a data flow expression take its right operator
		if op1.nodeType != Node.TEXT_NODE and op1.tagName == "flow-to":
			op1Expr = self.parseExpr(op1.childNodes[1].firstChild)
			code.append(self.handleFlowTo(op1))
		else:
			op1Expr = self.parseExpr(op1)
		
		op2Expr = self.parseExpr(op2)
		
		funcList = self.getFunction(op1Expr)
		for func in funcList:
			func.setDataFlow(True)
			funcName = func.getName()
			
			#listeners = func.getName() + "_listeners"
			self.compiler.funcDataFlowRequests.append((func, op2Expr))
			
			code.append(self.buildLine("%s__flow_to__%s()" % (funcName, op2Expr)))
		
		#op1Type = self.getExprDataType(op1)
		return ''.join(code)
	
	def handleForEach(self, node):
		iterExprNode = getElementByTagName(node, "iterator").childNodes[0]
		collExprNode = getElementByTagName(node, "collection").childNodes[0]
		
		iterName = "Default"
		if isElemNode(collExprNode) and collExprNode.tagName == "access":
			op2 = collExprNode.childNodes[1].firstChild
			if isTextNode(op2):
				iterName = capitalize(op2.nodeValue)
				collExprNode = collExprNode.childNodes[0].firstChild
		
		iterExpr = self.parseExpr(iterExprNode)
		collExpr = self.parseExpr(collExprNode)
		
		collExprType = self.getExprDataType(collExprNode)
		
		iteratorImpl = self.implementFunction(collExprType, "iterator" + iterName, [])
		iteratorType = iteratorImpl.getYieldType()
		iteratorValue = iteratorImpl.getYieldValue()
		
		if not iteratorType:
			raise CompilerException("Iterator for '%s' doesn't pass any objects to the foreach loop using the yield keyword" % collExpr)
		
		self.pushScope()
		
		# Register iterator variable
		var = self.createVariable(iterExpr, iteratorType, iteratorValue, False, False, False)
		typeInit = ""
		if not self.variableExistsAnywhere(iterExpr):
			self.getCurrentScope().variables[iterExpr] = var
			typeInit = self.adjustDataType(var.type) + " "
			
		# Register counter variable (if available)
		counterNode = getElementByTagName(node, "counter")
		if counterNode:
			counterVarName = self.parseExpr(counterNode.firstChild)
			cVar = self.createVariable(counterVarName, "Size", "", False, False, False)
			
			if not self.variableExistsAnywhere(counterVarName):
				self.getCurrentScope().variables[counterVarName] = cVar
				counterTypeInit = self.adjustDataType(cVar.type) + " "
		else:
			counterVarName = ""
			counterTypeInit = ""
		
		code = self.parseChilds(getElementByTagName(node, "code"), "\t" * self.currentTabLevel, self.lineLimiter)
		
		# Save scope
		#self.debugScopes()
		self.saveScopesForNode(node)
		
		self.popScope()
		
		"""
		# Insert code from iterator
		
		while condition
			x = yieldExpr;
			$code
		"""
		
		# TODO: Generic
		tabs = "\t" * self.currentTabLevel
		iterImplCode = iteratorImpl.getCode()
		
		# DO THIS AFTER THE LOOP BODY HAS BEEN COMPILED
		self.compiler.forVarCounter += 1
		
		return self.buildForEachLoop(var, typeInit, iterExpr, collExpr, collExprType, iterImplCode, code, tabs, counterVarName, counterTypeInit)
	
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
		var = self.createVariable(iterExpr, getHeavierOperator(fromType, toType), fromExpr, False, False, False)
		typeInit = ""
		if not self.variableExistsAnywhere(iterExpr):
			self.getCurrentScope().variables[iterExpr] = var
			typeInit = self.adjustDataType(var.type) + " "
		code = self.parseChilds(getElementByTagName(node, "code"), "\t" * self.currentTabLevel, self.lineLimiter)
		self.popScope()
		
		varDefs = ""
		if not self.variableExistsAnywhere(toExpr):
			toVar = self.createVariable("bp_for_end_%s" % (self.compiler.forVarCounter), toType, "", False, not toType in nonPointerClasses, False)
			#self.getTopLevelScope().variables[toVar.name] = toVar
			self.varsHeader += self.buildVarDeclaration(toVar.type, toVar.name) + self.lineLimiter
			varDefs = "%s = %s;\n" % (toVar.name, toExpr)
			varDefs += "\t" * self.currentTabLevel
			toExpr = toVar.name
			self.compiler.forVarCounter += 1
		
		return self.buildForLoop(varDefs, typeInit, iterExpr, fromExpr, operator, toExpr, code, "\t" * self.currentTabLevel)
	
	def buildVarDeclaration(self, typeName, name):
		return self.buildSingleParameter(typeName, name)
	
	def addDivisionByZeroCheck(self, op):
		if isNumeric(op):
			if op != "0" and op != "0.0":
				return
			else:
				self.additionalCodePerLine.append(self.buildDivByZeroThrow(op))
				return
		
		self.additionalCodePerLine.append(self.buildDivByZeroCheck(op))
	
	def waitCustomThreadsCode(self, block):
		joinCodes = []
		tabs = "\t" * self.currentTabLevel
		for threadID in block:
			joinCodes.append(self.buildThreadJoin(threadID, tabs))
		return ''.join(joinCodes)
	
	def handleTry(self, node):
		codeNode = getElementByTagName(node, "code")
		
		self.pushScope()
		code = self.parseChilds(codeNode, "\t" * self.currentTabLevel, self.lineLimiter)
		self.popScope()
		
		return self.trySyntax % code
		
	def handleCatch(self, node):
		varNode = getElementByTagName(node, "variable")
		codeNode = getElementByTagName(node, "code")
		
		self.pushScope()
		
		var = self.parseExpr(varNode)
		
		# Declare-type on exceptions
		if not var and varNode.firstChild and varNode.firstChild.nodeType != Node.TEXT_NODE and varNode.firstChild.tagName == "declare-type":
			varName = varNode.firstChild.childNodes[0].childNodes[0].nodeValue
			typeName = varNode.firstChild.childNodes[1].childNodes[0].nodeValue
			
			#print("Registering")
			#print(varName)
			#print(typeName)
			varObject = self.createVariable(varName, typeName, "", self.inConst, not typeName in nonPointerClasses, False)
			self.registerVariable(varObject)
			
			var = self.buildCatchVar(varName, self.adjustDataType(typeName))
		
		if not var:
			var = self.buildEmptyCatchVar()
		
		# Code needs to be compiled AFTER THE EXCEPTION VARIABLE HAS BEEN REGISTERED
		
		code = self.parseChilds(codeNode, "\t" * self.currentTabLevel, self.lineLimiter)
		self.popScope()
		
		return self.catchSyntax % (var, code)
	
	def handleCall(self, node):
		if self.onVariable:
			funcNameNode = getFuncNameNode(node)
			params = getElementByTagName(node, "parameters")
			virtualCall = self.makeXMLObjectCall(self.onVariable, funcNameNode.toxml(), params.toxml())
			
			# Set parent node to make mutable behaviour for immutable types possible (some crazy cheating)
			virtualCall.parentNode = node.parentNode
			
			saved = self.onVariable
			self.onVariable = ""
			code = self.handleCall(virtualCall)
			self.onVariable = saved
			
			return code
		
		caller, callerType, funcName = self.getFunctionCallInfo(node)
		
		# For casts
		funcName = self.prepareTypeName(funcName)
		
		params = getElementByTagName(node, "parameters")
		paramsString, paramTypes = self.handleParameters(params)
		
		#debug(("--> [CALL] " + caller + "." + funcName + "(" + paramsString + ")").ljust(70) + " [my : " + callerType + "]")
		
		callerClassName = extractClassName(callerType)
		#if callerClassName == "void":
		#	raise CompilerException("Function '%s' has no return value" % getElementByTagName(node, "function"))
		callerClass = self.getClass(callerClassName)
		
		# MemPointer.free
		if funcName == "free" and callerClassName == "MemPointer":
			return self.buildDeleteMemPointer(caller)
		
		if not self.compiler.mainClass.hasExternFunction(funcName): #not funcName.startswith("bp_"):
			# Check extended classes
			callerClassImpl = self.getClassImplementationByTypeName(callerType)
			funcInBase, baseClassImpl = findFunctionInBaseClasses(callerClassImpl, funcName)
			
			if not funcName in callerClass.functions:
				if not funcInBase:
					if funcName[0].islower():
						raise CompilerException("Function '%s.%s' has not been defined [Error code 1]" % (callerType, funcName))
					else:
						raise CompilerException("Class '%s' has not been defined  [Error code 2]" % (funcName))
				
				func = funcInBase
			else:
				func = callerClass.functions[funcName]
				
				# Are we overwriting the implementation of the base class?
				if funcInBase:
					#print([x.getName() for x in func], [x.getName() for x in funcInBase])
					for baseFunc in funcInBase:
						baseFunc.setOverwritten(True)
			
			# Optimized string concatenation
			# print "Aあいうえお|" + "Bあいうえお|" + "C|あいうえお"
			if self.compiler.optimizeStringConcatenation:
				if funcName == "operatorAdd" and callerType == "UTF8String" and paramTypes[0] in {"UTF8String", "Int"}:
					# Check if above our node is an add node
					op = getElementByTagName(node, "operator")
					secondAddNode = op.firstChild.firstChild.firstChild
					
					if op and op.firstChild.tagName == "access" and tagName(secondAddNode) == "add":
						#print("PREPARING FOR REPLACEMENT")
						
						string1 = secondAddNode.childNodes[0].firstChild#.cloneNode(True)
						string2 = secondAddNode.childNodes[1].firstChild
						
						if string1 and string2:
							#print("OP:")
							#print(op.toprettyxml())
							#print("String 1: " + string1.toxml())
							#print("String 2: " + string2.toxml())
							#print(paramTypes)
							#print(paramsString)
							
							# Add one more parameter to the operator
							paramTypes = [self.getExprDataType(string2)] + paramTypes
							paramsString = "%s, %s" % (self.parseExpr(string2), paramsString)
							
							#print(paramTypes)
							#print(paramsString)
							#print(secondAddNode.toprettyxml())
							
							#secondAddNode.parentNode.replaceChild(string1, secondAddNode)
							
							#print("After:")
							#print(secondAddNode.toprettyxml())
							
							caller = self.parseExpr(string1)
							# Remove add node
							
						#print(("--> [CALL] " + caller + "." + funcName + "(" + paramsString + ")").ljust(70) + " [my : " + callerType + "]")
			
			# Default parameters
			paramTypes, paramsString = self.addDefaultParameters(callerType, funcName, paramTypes, paramsString)
			previousParamTypes = list(paramTypes)
			
			for i in range(len(paramTypes)):
				if paramTypes[i] == "void":
					raise CompilerException("'%s' does not return a value" % nodeToBPC(params.childNodes[i]))
			
			funcImpl = self.implementFunction(callerType, funcName, paramTypes)
			fullName = funcImpl.getName()
			
			# Casts
			for i in range(len(previousParamTypes)):
				pFrom = previousParamTypes[i]
				pTo = paramTypes[i]
				
				if pFrom != pTo and (not canBeCastedTo(pFrom, pTo)) and (not self.isDerivedClass(pFrom, pTo)):
					params = paramsString.split(",")
					# TODO: self.buildCall(caller, fullName, paramsString)
					#debug("Type cast from '%s' to '%s'" % (pFrom, pTo))
					params = params[:i] + [self.buildCall("(" + params[i] + ")", "to" + pTo, "")] + params[i + 1:]
					paramsString = ", ".join(params)
				elif pFrom == "Int" and pTo == "Size":
					compilerWarning("Cast from signed Integer to unsigned Size in '%s'" % nodeToBPC(node))
			
			# Check whether the given parameters match the default parameter types
			#defaultValueTypes = funcImpl.func.getParamDefaultValueTypes()
			#for i in range(len(defaultValueTypes)):
			#	if i >= paramTypesLen:
			#		break
			#	
			#	if defaultValueTypes[i] and paramTypes[i] != defaultValueTypes[i]:
			#		raise CompilerException("Call parameter types don't match the parameter default types of '%s'" % (funcName))
			
			# Parallel
			if self.inParallel >= 0 and node.parentNode and node.parentNode.parentNode and node.parentNode.parentNode.tagName == "parallel":
				threadID = self.compiler.customThreadsCount
				threadFuncID = fullName
				self.buildThreadFunc(threadFuncID, paramTypes)
				self.parallelBlockStack[-1].append(threadID)
				self.compiler.customThreadsCount += 1
				tabs = "\t" * self.currentTabLevel
				return self.buildThreadCreation(threadID, threadFuncID, paramTypes, paramsString, tabs)
			
			# Immutable used with mutable coding style
			if ((not isinstance(node.parentNode, Document)) and node.parentNode.tagName == "code") and funcImpl.getReturnType() == callerType:
				pos = caller.find(self.ptrMemberAccessChar)
				if pos == -1:
					implicitAssignment = caller + " = "
				else:
					implicitAssignment = caller[:pos] + " = "
			else:
				implicitAssignment = ""
				
			if (callerClass in nonPointerClasses) or isUnmanaged(callerType):
				return implicitAssignment + self.buildNonPointerCall(caller, fullName, paramsString)
			else:
				return implicitAssignment + self.buildCall(caller, fullName, paramsString)
		else:
			# Temporary hack
			if funcName == "glVertexAttribPointer":
				funcName = "bp_" + funcName
			
			return self.externCallSyntax % (funcName, paramsString)
	
	def pushScope(self):
		self.currentTabLevel += 1
		ScopeController.pushScope(self)
		
	def popScope(self):
		self.currentTabLevel -= 1
		ScopeController.popScope(self)
	
	def debugScopes(self):
		counter = 0
		for scope in self.scopes:
			print("[Scope " + str(counter) + "]")
			for name, variable in scope.variables.items():
				print(" => " + variable.name.ljust(40) + " : " + variable.type)
			counter += 1
	
	def implementCasts(self):
		# Implement casts BEFORE class functions are written
		for classObj in self.localClasses:
			if not classObj.isExtern:
				for classImplId, classImpl in classObj.implementations.items():
					for funcList in classObj.functions.values():
						if funcList:
							func = funcList[0]
							if func.isCast:
								#print("===> " + classImpl.getName() + "." + func.getName())
								self.implementFunction(classImpl.getName(), func.getName(), [])
	
	def writeFunctions(self):
		for func in self.localFunctions:
			for funcImpl in func.implementations.values():
				self.functionsHeader += "%s\n" % (funcImpl.getFullCode())
	
	def getRootNode(self):
		return self.root
		
	def getCodeNode(self):
		return self.codeNode
		
	def getHeaderNode(self):
		return self.headerNode
		
	def getDependenciesNode(self):
		return self.dependencies
	
	def getFilePath(self):
		return self.file
	
	def getFileName(self):
		return self.file[len(self.dir):]
	
	def getDirectory(self):
		return self.dir
	
	def getCode(self):
		return NotImplementedError()
