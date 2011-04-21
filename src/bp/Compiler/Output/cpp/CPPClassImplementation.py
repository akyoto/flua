from Output.cpp.CPPFunctionImplementation import *

class CPPClassImplementation:
	
	def __init__(self, classObj, templateValues):
		self.classObj = classObj
		self.templateValues = templateValues
		self.members = {}
		self.funcImplementations = {}
		
		debug("'%s' added class implementation %s" % (self.classObj.name, templateValues))
		
	def getName(self):
		name = self.classObj.name
		if self.templateValues:
			name += "<%s>" % (", ".join(self.templateValues))
		return name
		
	def getTemplateValuesString(self, adjusted = False, clean = False):
		stri = ""
		
		if adjusted:
			if self.templateValues:
				for param in self.templateValues:
					stri += adjustDataType(param) + ", "
				
				if clean:
					return ("< " + stri[:-2] + " >").replace(" ", "")
				else:
					return "< " + stri[:-2] + " >"
			else:
				return ""
		else:
			if self.templateValues:
				if clean:
					return "<" + ",".join(self.templateValues) + ">"
				else:
					return "< " + ", ".join(self.templateValues) + " >"
			else:
				return ""
		
	def translateTemplateName(self, dataType):
		templateNames = self.classObj.templateNames
		for i in range(len(templateNames)):
			if dataType == templateNames[i]:
				return self.templateValues[i]
		return dataType
		
	def addMember(self, var):
		debug("'%s' added member '%s'" % (self.classObj.name, var.name))
		var.classImpl = self
		self.members[var.name] = var
		
	def requestFuncImplementation(self, funcName, paramTypes):
		codeExists = 1
		key = funcName + buildPostfix(paramTypes)
		if not key in self.funcImplementations:
			codeExists = 0
			#debug(self.classObj.functions)
			if not funcName in self.classObj.functions:
				if self.classObj.name:
					raise CompilerException("Function '%s.%s' has not been defined" % (self.classObj.name, funcName))
				else:
					raise CompilerException("Function '%s' has not been defined" % (funcName))
			self.addFuncImplementation(CPPFunctionImplementation(self, self.classObj.getMatchingFunction(funcName, paramTypes), paramTypes))
		return self.funcImplementations[key], codeExists
		
	def getFuncImplementation(self, funcName, paramTypes):
		return self.funcImplementations[funcName + buildPostfix(paramTypes)]
		
#	def getTemplateValuesString(self):
#		return ", ".join(self.templateValues)
#	
#	def getTemplateValuesStringEnclosed(self):
#		return "<" + ", ".join(self.templateValues) + ">"
		
	def addFuncImplementation(self, impl):
		debug("'%s' added function implementation %s" % (self.classObj.name + self.getTemplateValuesString(), impl.name))
		self.funcImplementations[impl.name] = impl