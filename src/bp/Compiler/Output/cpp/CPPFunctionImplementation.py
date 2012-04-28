from bp.Compiler.Utils import *
from bp.Compiler.Output.cpp.datatypes import *

class CPPFunctionImplementation:
	
	def __init__(self, classImpl, func, paramTypes):
		self.classImpl = classImpl
		self.func = func
		self.paramTypes = paramTypes
		
		for i in range(len(self.func.paramTypesByDefinition)):
			byDef = self.func.paramTypesByDefinition[i]
			if byDef:
				self.paramTypes[i] = self.classImpl.translateTemplateName(byDef)
		
		self.name = self.func.getName() + self.buildPostfix()
		self.code = ""
		self.returnTypes = []
		self.func.implementations[self.name] = self
		
	def getReturnType(self):
		heaviest = None
		
		for type in self.returnTypes:
			if type in dataTypeWeights:
				heaviest = getHeavierOperator(heaviest, type)
			else:
				return type
		
		if heaviest:
			return heaviest
		else:
			return "void"
		
	def buildPostfix(self):
		return buildPostfix(self.paramTypes)
	
	def setCode(self, newCode):
		self.code = newCode
		
	def getName(self):
		# main -> _bp_custom_main
		if self.name == "main":
			return "_bp_custom_main"
		return self.name
	
	def getFuncName(self):
		return self.func.getName()
		
	def getParamString(self):
		stri = ""
		paramNames = self.func.getParamNames()
		for i in range(len(paramNames)):
			stri += "%s %s, " % (adjustDataType(self.paramTypes[i]), paramNames[i])
		return stri[:-2]
		
	def getParamTypeString(self):
		stri = ""
		paramNames = self.func.getParamNames()
		#print(paramNames)
		#print(self.paramTypes)
		for i in range(len(paramNames)):
			stri += "%s, " % (adjustDataType(self.paramTypes[i]))
		return stri[:-2]
		
	def getReferenceString(self):
		# TODO: Remove hardcoded stuff
		if self.getFuncName() == "operatorIndex":
			return "&"
		return ""
		
	def getPrototype(self):
		return "inline %s %s(%s);\n" % (adjustDataType(self.getReturnType()) + self.getReferenceString(), self.getName(), self.getParamTypeString())
		
	def getFullCode(self):
		# TODO: Add parameters
		if self.func.isCast:
			castType = ""
			if self.func.castToUnmanaged:
				castType = adjustDataType("~" + self.name)
			else:
				castType = adjustDataType(self.name)
			return "// Cast: %s\n\tinline operator %s(%s) {\n%s\t}\n" % (self.func.name, castType, self.getParamString(), self.code)
		
		# TODO: Remove hardcoded stuff (here: Operator = for ~MemPointer<ConstChar> is directly used by C++ and therefore needs no name change)
		if self.getFuncName() == "operatorAssign" and self.classImpl.getName() == "UTF8String" and self.paramTypes[0] == "~MemPointer<ConstChar>":
			funcName = "operator="
		else:
			funcName = self.getName()
		
		return "// %s\n\tinline %s %s(%s) {\n%s\t}\n" % (funcName, adjustDataType(self.getReturnType()) + self.getReferenceString(), funcName, self.getParamString(), self.code)
	
	def getConstructorCode(self):
		# TODO: Add parameters
		return "// %s\n\tinline %s(%s) {\n%s\t}\n" % (self.getFuncName(), "BP" + self.func.classObj.name, self.getParamString(), self.code)