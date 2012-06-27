####################################################################
# Header
####################################################################
# File:		Handlers for the base class
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
from flua.Compiler.Output import *
from flua.Compiler.Input.bpc.BPCUtils import *

####################################################################
# Classes
####################################################################
class BaseOutputFileHandler:
	
	def handleAssign(self, node):
		self.inAssignment += 1
		
		# 'on' block
		if self.onVariable:
			op1 = node.firstChild.firstChild
			op2 = node.childNodes[1].firstChild
			
			# OP1 = OP2
			# a.x = 5
			
			# a.x -> op1
			# a   -> innerOp1
			
			innerOp1 = getLeftMostOperatorNode(op1)
			#innerOp2 = innerOp1.parentNode.parentNode.childNodes[1].firstChild
			
			# Prefix the on variable
			op1XML = ">%s<" % op1.toxml()
			
			# Not really safe
			innerOp1XML = innerOp1.toxml()
			
			replaced = ">%s<" % innerOp1XML
			virtualAccess = "><access><value>%s</value><value>%s</value></access><" % (self.onVariable, innerOp1XML)
			op1ModifiedXML = op1XML.replace(replaced, virtualAccess)[1:-1]
			
			#print(replaced, " -> ", virtualAccess)
			#print(op1XML)
			#print(op1ModifiedXML)
			
			virtualAssign = self.makeXMLAssign(op1ModifiedXML, op2.toxml())
			
			# Set parent node (hacks!)
			virtualAssign.parentNode = node.parentNode
			
			saved = self.onVariable
			self.onVariable = ""
			
			try:
				# For improved debug messages
				#self.lastParsedNode.append(node)
				
				code = self.handleAssign(virtualAssign)
				
				#self.lastParsedNode.pop()
			except CompilerException:
				raise
			except:
				raise CompilerException("'%s' could not be set as a property of '%s'" % (nodeToBPC(node), saved))
			
			self.onVariable = saved
			
			return code
		
		isSelfMemberAccess = False
		publicMemberAccess = False
		
		# Member access (setter)
		op1 = node.childNodes[0].childNodes[0]
		#debug("OP1: " + op1.toxml())
		#debug(isTextNode(op1))
		
		if not isTextNode(op1):
			if op1.tagName == "access":
				accessOp1 = op1.childNodes[0].childNodes[0]
				accessOp2 = op1.childNodes[1].childNodes[0]
				
				# data access from a pointer
				accessOp1Type = self.getExprDataType(accessOp1)
				if extractClassName(accessOp1Type) == "MemPointer" and accessOp2.nodeValue == "data": #and isUnmanaged(accessOp1Type):
					return self.pointerDerefAssignSyntax % (self.parseExpr(accessOp1), self.parseExpr(node.childNodes[1]))
				
				#debug(accessOp1)
				#debug(".")
				#debug(accessOp2)
				
				isMemberAccess, publicMemberAccess = self.isMemberAccessFromOutside(accessOp1, accessOp2)
				if isMemberAccess and not accessOp1.nodeValue == "my":
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
				
				code.append(self.buildLine("%s _flua_tuple_%d = %s" % (self.adjustDataType(valueType), self.compiler.tupleUnbindCounter, op2Expr)))
				
				for i in range(numAssignments):
					varExpr = op1.childNodes[i].firstChild
					varType = tupleTypes[i]
					
					#valueVar = self.createVariable("_flua_tuple_%d->_%d" % (self.compiler.tupleUnbindCounter, i), varType, varExpr, self.inConst, not varType in nonPointerClasses, False)
					#self.registerVariable(valueVar)
					
					valueVar = "_flua_tuple_%d->_%d" % (self.compiler.tupleUnbindCounter, i)
					
					self.tupleTypes[valueVar] = varType
					
					virtualAssign = self.makeXMLAssign(varExpr.toxml(), valueVar)
					code.append(self.buildLine(self.handleAssign(virtualAssign)))
					
				code.append(self.buildLine("delete _flua_tuple_%d" % self.compiler.tupleUnbindCounter))
					
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
			# TODO: Save it for the IDE
			#self.currentClass.possibleMembers[memberName] = variableType
			
			isSelfMemberAccess = True
		
		if isSelfMemberAccess or publicMemberAccess:
			memberName = self.fixMemberName(memberName)
			var = self.createVariable(memberName, valueType, value, self.inConst, not valueType in nonPointerClasses, False)
			#if not variableName in self.currentClass.members:
			#	self.currentClass.addMember(var)
			
			if (not memberName in self.currentClassImpl.members):
				self.currentClassImpl.addMember(var)
			
			variableExisted = True
		else:
			#debug("Checking whether '%s' exists:" % variableName)
			variableExisted = self.variableExistsAnywhere(variableName)
			#debug(variableExisted)
			
			# If it exists as a member we do not care about it
			if variableExisted == 2:
				variableExisted = False
			
		# Need to register it here? 2 stands for class members
		if ((not variableExisted) or variableExisted == 2) and (not declaredInline):
			var = self.createVariable(variableName, valueType, value, self.inConst, not valueType in nonPointerClasses, False)
			
			# Check if we are in the top function level scope
			if self.currentFunctionImpl and self.getCurrentScope() != self.currentFunctionImpl.scope: #and isTextNode(op1):
				#print(var.getPrototype() + "<<")
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
		
		#print(self.assignSyntax % (variableName, value))
		
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
		#elif publicMemberAccess:
		#	return self.assignSyntax % (variableName, value)
		else:
			#print(self.assignFirstTimeSyntax % (var.getPrototype(), value))
			return self.assignFirstTimeSyntax % (var.getPrototype(), value)
	
	def handleAccess(self, node):
		op1 = node.childNodes[0].childNodes[0]
		op2 = node.childNodes[1].childNodes[0]
		
		if op1.nodeType == Node.TEXT_NODE:
			if op1.nodeValue in self.compiler.mainClass.namespaces:
				return op1.nodeValue + "_" + self.parseExpr(op2)
		
		callerType = self.getExprDataType(op1)
		callerClassName = extractClassName(callerType)
		
		# Class exists?
		if callerClassName in self.compiler.mainClass.classes:
			
			# MemPointer dereferencing is a special case
			if callerClassName == "MemPointer" and isTextNode(op2):
				if op2.nodeValue == "data":
					return "(*(%s))" % (self.parseExpr(op1))
			
			# GET access - are we accessing a member outside the class?
			isMemberAccess, publicMemberAccess = self.isMemberAccessFromOutside(op1, op2)
			
			#debug(op1.toxml())
			#debug(op2.toxml())
			#debug(publicMemberAccess)
			callerClassImpl = self.getClassImplementationByTypeName(callerType)
			
			# If yes, convert it to a getXYZ() call
			if isMemberAccess:
				#print("Replacing ACCESS with CALL: %s.%s" % (op1.toxml(), "get" + op2.nodeValue.capitalize()))
				#if isTextNode(op1) and op1.nodeValue == "my":
				#	op1xml = "this"
				#else:
				op1xml = op1.toxml()
				
				getFunc = self.cachedParseString("<call><function><access><value>%s</value><value>%s</value></access></function><parameters/></call>" % (op1xml, "get" + capitalize(op2.nodeValue))).documentElement
				#print(getFunc.toprettyxml())
				return self.handleCall(getFunc)
			# Or maybe it's just a direct public member access?
			elif publicMemberAccess:
				return self.parseBinaryOperator(node, self.ptrMemberAccessChar + "_")
			elif self.currentClassImpl != callerClassImpl:
				if op2.nodeValue in callerClassImpl.members:
					raise CompilerException("The property '%s' of class '%s' is not public and has no get function" % (nodeToBPC(op2), callerType))
				else:
					raise CompilerException("The property '%s' of class '%s' does not exist" % (nodeToBPC(op2), callerType))
		
		return self.parseBinaryOperator(node, self.ptrMemberAccessChar)
	
	def handleCompilerFlag(self, node):
		return ""
		
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
		
		# We also need to implement 'init' for all types used in the template.
		# This is needed because we need the information about their members before
		# iterators get implemented.
		#pos = typeName.find("<")
		#if pos != -1:
		#	templateTypes = splitParams(typeName[pos+1:-1])
		#	for t in templateTypes:
		#		if t in nonPointerClasses:
		#			continue
				
				#t = self.prepareTypeName(t)
				
		#		print("Trying " + t)
				
				#tClassImpl = self.getClassImplementationByTypeName(t)
				#for tFunc in tClassImpl.classObj.functions["init"]:
				#	print(tFunc.getName())
				#	tPTypes = tFunc.paramTypesByDefinition
				#	for i in range(len(tPTypes)):
				#		if not tPTypes[i]:
				#			tPTypes[i] = tFunc.paramDefaultValueTypes[i]
				#	self.implementFunction(t, tFunc.getName(), self.addDefaultParameters(t, tFunc.getName(), tPTypes, "")[0])
				
				#self.implementations = {}
				#self.paramNames = []
				#self.paramTypesByDefinition = []
				#self.paramDefaultValues = []
				#self.paramDefaultValueTypes = []
				
		#		try:
		#			pTypes, pString = self.addDefaultParameters(t, "init", [], "")
		#			funcImpl = self.implementFunction(t, "init", pTypes)
		#			print("Success.")
		#		except:
		#			raise
				#finally:
				#	continue
		
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
			
	def handleUnmanaged(self, node):
		self.inUnmanaged += 1
		expr = self.parseExpr(node.childNodes[0])
		self.inUnmanaged -= 1
		return "~" + expr
	
	def handleParallel(self, node):
		codeNode = getElementByTagName(node, "code")
		
		# 'begin' or 'parallel' statement?
		if (node.tagName == "parallel"):
			joinAll = True
		else:
			joinAll = False
			
		#getMetaData(node, "wait-for-all-threads") != "false" #isMetaDataTrueByTag(node, "wait-for-all-threads")
		
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
			
			self.onVariable = "_flua_on_var_%d" % self.compiler.onVarCounter
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
		
	def handleTarget(self, node):
		name = getElementByTagName(node, "name").childNodes[0].nodeValue
		if name == self.compiler.getTargetName() or matchesCurrentPlatform(name):
			return "\n" + self.parseChilds(getElementByTagName(node, "code"), "\t" * self.currentTabLevel, self.lineLimiter)
	
	def handleImport(self, node):
		importedModulePath = node.childNodes[0].nodeValue.strip()
		importedModule = getModulePath(importedModulePath, extractDir(self.file), self.compiler.getProjectDir(), ".flua")
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
				op1Type = self.getExprDataType(collExprNode.childNodes[0].firstChild)
				op1Class = self.getClass(extractClassName(op1Type))
				
				if op1Class.hasIterator(op2.nodeValue):
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
		
		# We ignore global variables - THIS...IS...SPAR...ERR...LOCALSCOPE!
		if 1:#not self.variableExistsAnywhere(iterExpr):
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
		
		#print(code)
		#print("--ITER--")
		#print(iterImplCode)
		#print("--END ITER--")
		
		return self.buildForEachLoop(var, typeInit, iterExpr, collExpr, collExprType, iterImplCode, code, tabs, counterVarName, counterTypeInit)
	
	def handleFor(self, node):
		if node.tagName == "parallel-for":
			parallel = True
		else:
			parallel = False
		
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
		
		self.parallelBlockStack.append([])
		code = self.parseChilds(getElementByTagName(node, "code"), "\t" * self.currentTabLevel, self.lineLimiter)
		
		self.popScope()
		
		varDefs = ""
		if not self.variableExistsAnywhere(toExpr):
			toVar = self.createVariable("flua_for_end_%s" % (self.compiler.forVarCounter), toType, "", False, not toType in nonPointerClasses, False)
			#self.getTopLevelScope().variables[toVar.name] = toVar
			self.varsHeader += self.buildVarDeclaration(toVar.type, toVar.name) + self.lineLimiter
			varDefs = "%s = %s;\n" % (toVar.name, toExpr)
			varDefs += "\t" * self.currentTabLevel
			toExpr = toVar.name
			self.compiler.forVarCounter += 1
		
		# Parallel execution
		if parallel:
			threadID = self.compiler.customThreadsCount
			threadFuncID = "flua_pfor_func_%d" % self.compiler.customThreadsCount
			saveInCollection = "flua_pfor_collection_%d" % self.compiler.customThreadsCount
			
			# Create a thread function
			paramTypes = []
			self.buildThreadFunc(threadFuncID, paramTypes)
			
			# Append it to the last list on the stack
			self.parallelBlockStack[-1].append(threadID)
			
			self.compiler.customThreadsCount += 1
			tabs = "\t" * self.currentTabLevel
			
			self.compiler.parallelForFuncs.append(self.buildPForFunc(threadFuncID, code))
			#return self.buildThreadCreation(threadID, threadFuncID, paramTypes, paramsString, tabs)
			
			# Create a dynamical list of threads
			# TODO: C++ independent
			initCode = self.buildLine("std::vector<pthread_t> %s" % (saveInCollection))
			exitCode = ""
			
			# Replace code
			tabs = "\t" * self.currentTabLevel
			code = self.buildThreadCreation(threadID, threadFuncID, paramTypes, "", tabs, saveInCollection)
		else:
			initCode = ""
			exitCode = ""
		
		self.parallelBlockStack.pop()
		
		return initCode + self.buildForLoop(varDefs, typeInit, iterExpr, fromExpr, operator, toExpr, code, "\t" * self.currentTabLevel) + exitCode
		
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
		# 'on' block
		if self.onVariable:
			funcNameNode = getFuncNameNode(node)
			params = getElementByTagName(node, "parameters")
			virtualCall = self.makeXMLObjectCall(self.onVariable, funcNameNode.toxml(), params.toxml())
			
			# Set parent node to make mutable behaviour for immutable types possible (some crazy cheating)
			virtualCall.parentNode = node.parentNode
			
			saved = self.onVariable
			self.onVariable = ""
			
			try:
				# For improved debug messages
				#self.lastParsedNode.append(node)
				
				code = self.handleCall(virtualCall)
				
				#self.lastParsedNode.pop()
			except CompilerException:
				raise
			except:
				raise CompilerException("'%s' could not be called as a method of '%s'" % (nodeToBPC(node), saved))
			self.onVariable = saved
			
			return code
		
		# Retrieve some information about the call
		caller, callerType, funcName = self.getFunctionCallInfo(node)
		
		# For casts
		funcName = self.prepareTypeName(funcName)
		
		# DAU protection
		if self.currentClassImpl != self.compiler.mainClassImpl:
			#print(self.currentClassImpl.members)
			#print(caller)
			if caller in self.currentClassImpl.members:
				# TODO: Replace 'my'
				bpc = nodeToBPC(node)
				raise CompilerException("Did you mean %s.%s instead of %s? %s is a member of %s" % ("my", bpc, bpc, caller, self.currentClassImpl.getFullName()))
		
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
		
		if not self.compiler.mainClass.hasExternFunction(funcName): #not funcName.startswith("flua_"):
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
			
			# Parallel execution
			if self.inParallel >= 0 and node.parentNode and node.parentNode.parentNode and node.parentNode.parentNode.tagName in {"parallel", "begin"}:
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
				funcName = "flua_" + funcName
			
			return self.externCallSyntax % (funcName, paramsString)
