from bp.Compiler.Utils import *

def findFunctionInBaseClasses(callerClass, funcName):
	for classObj in callerClass.extends:
		debug("Checking base class '%s' for function '%s'" % (classObj.name, funcName))
		if funcName in classObj.functions:
			debug("Found function '%s' in base class '%s'" % (funcName, classObj.name))
			return classObj.functions[funcName]
		
		if classObj.extends:
			func = findFunctionInBaseClasses(classObj, funcName)
			if func:
				return func
	return None

class BaseClassImplementation:
	
	def __init__(self, classObj, templateValues):
		self.classObj = classObj
		self.templateValues = templateValues
		self.members = {}
		self.funcImplementations = {}
		
		debug("'%s' added class implementation %s" % (self.classObj.name, templateValues))
		
	def getName(self):
		return ""
		
	def getTemplateValuesString(self, adjusted = False, clean = False):
		return ""
		
	def translateTemplateName(self, dataType):
		templateNames = self.classObj.templateNames
		for i in range(len(templateNames)):
			if dataType == templateNames[i]:
				if i < len(self.templateValues):
					return self.templateValues[i]
				else:
					return self.classObj.templateDefaultValues[i]
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
				candidates = findFunctionInBaseClasses(self.classObj, funcName)
				if not candidates:
					if self.classObj.name:
						raise CompilerException("Function '%s.%s' has not been defined" % (self.classObj.name, funcName))
					else:
						raise CompilerException("Function '%s' has not been defined" % (funcName))
			impl = self.createFunctionImplementation(self.getMatchingFunction(funcName, paramTypes), paramTypes)
			self.addFuncImplementation(impl)
			return impl, codeExists
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
		
	def getMatchingFunction(self, funcName, paramTypes):
		#print("Function '%s' has been called with types %s (%s to choose from)" % (funcName, paramTypes, len(self.classObj.functions[funcName])))
		if not funcName in self.classObj.functions:
			candidates = findFunctionInBaseClasses(self.classObj, funcName)
		else:
			candidates = self.classObj.functions[funcName]
		#print(candidates[0].paramTypesByDefinition)
		winner = None
		winnerScore = 0
		for func in candidates:
			score = func.getMatchingScore(paramTypes, self)
			#debug("Candidate: %s with score '%s'" % (func.paramTypesByDefinition, score))
			if score > winnerScore:
				winner = func
				winnerScore = score
		
		if winner is None:
			print("Candidates were:")
			for func in candidates:
				print(" * " + func.getName() + " " + str(func.paramTypesByDefinition).replace("''", "*").replace("'", ""))
			raise CompilerException("No matching function found for the call '%s.%s' with the parameter types '%s'" % (self.getName(), funcName, paramTypes))
		
		return winner
