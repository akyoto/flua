from flua.Compiler.Utils import *
from flua.Compiler.Output import *
from flua.Compiler.Output.cpp.DataTypes import *

class CPPFunctionImplementation(BaseFunctionImplementation):
	
	def __init__(self, classImpl, func, paramTypes):
		super().__init__(classImpl, func, paramTypes)
		
	def getParamString(self):
		stri = ""
		paramNames = self.func.getParamNames()
		paramTypesLen = len(self.paramTypes)
		#invisibleParamTypesLen = len(self.invisibleParamTypes)
		
		for i in range(len(paramNames)):
			#if self.hasInvisibleParamTypes and i < invisibleParamTypesLen and self.invisibleParamTypes[i]:
			#	stri += "%s %s, " % ("__flua_T%d" % i, paramNames[i])
			#else:
			if i < paramTypesLen:
				paramType = self.paramTypes[i]
			else:
				# Default values
				paramType = self.func.paramDefaultValueTypes[i]
			
			paramType = self.classImpl.translateTemplateName(paramType)
			stri += "%s %s, " % (adjustDataTypeCPP(paramType), paramNames[i])
		
		return stri[:-2]
		
	def getParamTypeString(self):
		stri = ""
		paramNames = self.func.getParamNames()
		paramTypesLen = len(self.paramTypes)
		#print(paramNames)
		#print(self.paramTypes)
		for i in range(len(paramNames)):
			if i < paramTypesLen:
				paramType = self.paramTypes[i]
			else:
				# Default values
				paramType = self.func.paramDefaultValueTypes[i]
			stri += "%s, " % (adjustDataTypeCPP(paramType))
		return stri[:-2]
		
	def getReferenceString(self):
		# TODO: Remove hardcoded stuff
		#if self.getFuncName() == "operatorIndex":
		#	return "&"
		return ""
		
	def getPrototype(self):
		return "inline %s %s(%s);\n" % (adjustDataTypeCPP(self.getReturnType()) + self.getReferenceString(), self.getName(), self.getParamTypeString())
		
	def getFullCode(self, noPostfix = False, includeNamespace = False):
		if self.func.overwritten:
			inlineVirtual = "virtual"
		else:
			inlineVirtual = "inline"
		
		# TODO: Add parameters
		if self.func.isCast:
			castType = ""
			if self.func.castToUnmanaged:
				castType = adjustDataTypeCPP("~" + self.name)
			else:
				castType = adjustDataTypeCPP(self.name)
			
			funcIntern = "// BP Cast: %s\n\t%s %s to%s(%s) {\n%s\t}\n" % (self.func.name, inlineVirtual, castType, normalizeName(self.func.name), self.getParamString(), self.code)
			funcCppComfort = "// C++ Cast: %s\n\t%s operator %s(%s) {\n%s\t}\n" % (self.func.name, inlineVirtual, castType, self.getParamString(), self.code)
			
			return funcIntern + "\n\t" + funcCppComfort
		
		classImplName = self.classImpl.getName()
		
		# TODO: Remove hardcoded stuff (here: Operator = for ~MemPointer<ConstChar> is directly used by C++ and therefore needs no name change)
		if self.getFuncName() == "operatorAssign" and classImplName == "UTF8String" and self.paramTypes[0] == "~MemPointer<ConstChar>":
			funcName = "operator="
		else:
			if noPostfix:
				funcName = self.func.getName()
			else:
				funcName = self.getName()
		
		if classImplName:
			tabs = "\t"
			
			if includeNamespace:
				funcName = "%s::%s" % (adjustDataTypeCPP(classImplName, adjustOuterAsWell = False), funcName)
		else:
			tabs = ""
			
			if includeNamespace:
				funcName = "::" + funcName
		
		#if self.hasInvisibleParamTypes:
		#	templateList = []
		#	for i in range(len(self.invisibleParamTypes)):
		#		if self.invisibleParamTypes[i]:
		#			templateList.append("typename __flua_T%d" % i)
		#	templates = "template <%s>\n%s" % (", ".join(templateList), tabs)
		#else:
		#	templates = ""
		
		return "// %s\n%s%s %s %s(%s) {\n%s%s}\n" % (
			funcName,
			tabs,
			#templates,
			inlineVirtual,
			adjustDataTypeCPP(self.getReturnType()) + self.getReferenceString(),
			funcName,
			self.getParamString(),
			self.code,
			tabs
		)
	
	# Constructor
	def getConstructorCode(self):
		# TODO: Add parameters
		return "// %s\n\tinline %s(%s) {\n%s\t}\n" % (self.getFuncName(), "BP" + self.func.classObj.name, self.getParamString(), self.code)
	
	# Destructor
	def getDestructorCode(self):
		if self.classImpl.classObj.hasOverwrittenFunctions:
			inlineVirtual = "virtual"
		else:
			inlineVirtual = "inline"
		
		return "// %s\n\t%s ~%s(%s) {\n%s\t}\n" % (self.getFuncName(), inlineVirtual, "BP" + self.func.classObj.name, self.getParamString(), self.code)
