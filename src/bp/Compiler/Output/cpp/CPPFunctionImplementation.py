from Utils import *
from Output.cpp.datatypes import *

class CPPFunctionImplementation:
	
	def __init__(self, classImpl, func, paramTypes):
		self.classImpl = classImpl
		self.func = func
		self.paramTypes = paramTypes
		self.name = self.func.name + self.buildPostfix()
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
		return self.name
	
	def getFuncName(self):
		return self.func.name
		
	def getParamString(self):
		stri = ""
		paramNames = self.func.getParamNames()
		for i in range(len(paramNames)):
			stri += "%s %s, " % (adjustDataType(self.paramTypes[i]), paramNames[i])
		return stri[:-2]
		
	def getParamTypeString(self):
		stri = ""
		paramNames = self.func.getParamNames()
		print(paramNames)
		print(self.paramTypes)
		for i in range(len(paramNames)):
			stri += "%s, " % (adjustDataType(self.paramTypes[i]))
		return stri[:-2]
		
	def getReferenceString(self):
		# TODO: Remove hardcoded stuff
		if self.getFuncName() == "operatorIndex":
			return "&"
		return ""
		
	def getPrototype(self):
		return "inline %s %s(%s);\n" % (adjustDataType(self.getReturnType()) + self.getReferenceString(), self.name, self.getParamTypeString())
		
	def getFullCode(self):
		# TODO: Add parameters
		return "// %s\n\tinline %s %s(%s) {\n%s\t}\n" % (self.func.name, adjustDataType(self.getReturnType()) + self.getReferenceString(), self.name, self.getParamString(), self.code)
	
	def getConstructorCode(self):
		# TODO: Add parameters
		return "// %s\n\tinline %s(%s) {\n%s\t}\n" % (self.func.name, "BP" + self.func.classObj.name, self.getParamString(), self.code)