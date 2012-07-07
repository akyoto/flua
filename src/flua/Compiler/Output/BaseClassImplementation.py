####################################################################
# Header
####################################################################
# File:		Base class implementation
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

####################################################################
# Functions
####################################################################
def findFunctionInBaseClasses(callerClassImpl, funcName):
	if isinstance(callerClassImpl, BaseClassImplementation):
		callerClass = callerClassImpl.classObj
	else:
		callerClass = callerClassImpl
	
	for classImpl in callerClass.extends:
		classObj = classImpl.classObj
		#debug("Checking base class „%s“ for function „%s“" % (classObj.name, funcName))
		if funcName in classObj.functions:
			#debug("Found function „%s“ in base class „%s“" % (funcName, classObj.name))
			return classObj.functions[funcName], classImpl
		
		if classObj.extends:
			func, impl = findFunctionInBaseClasses(classObj, funcName)
			
			if func:
				return func, impl
	
	return None, None

####################################################################
# Classes
####################################################################
class BaseClassImplementation:
	
	def __init__(self, classObj, templateValues):
		self.classObj = classObj
		self.templateValues = templateValues
		self.members = {}
		self.funcImplementations = {}
		self.hasConstructorImpl = False
		
		#debug("„%s“ added class implementation %s" % (self.classObj.name, templateValues))
		
	def hasConstructorImplementation(self):
		return self.hasConstructorImpl
		
	def getName(self):
		return ""
		
	def getTemplateValuesString(self, adjusted = False, clean = False):
		return ""
		
	def translateTemplateName(self, dataType):
		templateNames = self.classObj.templateNames
		
		#print(templateNames)
		#print(self.templateValues)
		templateValuesLen = len(self.templateValues)
		
		for i in range(len(templateNames)):
			#print(dataType, templateNames[i], i, templateValuesLen, self.classObj.templateDefaultValues)
			if dataType == templateNames[i]:
				if i < templateValuesLen:
					return self.templateValues[i]
				else:
					return self.classObj.templateDefaultValues[i]
		return dataType
		
	def getFullName(self):
		if self.templateValues:
			return "%s<%s>" % (self.classObj.name, ", ".join(self.templateValues))
		else:
			return self.classObj.name
		
	def addMember(self, var):
		#debug("„%s“ added member „%s“" % (self.getFullName(), var.name))
		
		# Type correction - public declaration always has precedence.
		if var.name in self.classObj.publicMembers:
			var.type = self.translateTemplateName(self.classObj.publicMembers[var.name])
		
		if var.name.startswith("_"):
			raise CompilerException("Member names starting with an underscore are not allowed")
		
		var.classImpl = self
		self.members[var.name] = var
		
	def requestFuncImplementation(self, funcName, paramTypes):
		codeExists = 1
		key = funcName + buildPostfix(paramTypes)
		
		if not key in self.funcImplementations:
			codeExists = 0
			#debug(self.classObj.functions)
			if not funcName in self.classObj.functions:
				candidates, baseClassImpl = findFunctionInBaseClasses(self, funcName)
				
				if not candidates:
					if self.classObj.name:
						print("\n * ".join(["Class „%s“ has the following functions:" % self.classObj.name] + list(self.classObj.functions.keys())))
						print("\n * ".join(["Class „%s“ implemented the following functions:" % self.classObj.name] + list(self.funcImplementations.keys())))
						raise CompilerException("Function „%s.%s“ has not been defined [Error code 5]" % (self.classObj.name, funcName))
					else:
						raise CompilerException("Function „%s“ has not been defined [Error code 5]" % (funcName))
			
			func = self.getMatchingFunction(funcName, paramTypes)
			
			if func.classObj == self.classObj:
				classImpl = self
			else:
				# We implemented it in the inherited class
				classImpl = baseClassImpl
			
			impl = classImpl.createFunctionImplementation(func, paramTypes)
			classImpl.addFuncImplementation(impl)
			
			# Constructors
			if funcName == "init":
				self.hasConstructorImpl = True
			
			return impl, codeExists
		
		# Return existing one
		return self.funcImplementations[key], codeExists
		
	def getFuncImplementation(self, funcName, paramTypes):
		return self.funcImplementations[funcName + buildPostfix(paramTypes)]
		
#	def getTemplateValuesString(self):
#		return ", ".join(self.templateValues)
#	
#	def getTemplateValuesStringEnclosed(self):
#		return "<" + ", ".join(self.templateValues) + ">"
		
	def addFuncImplementation(self, impl):
		#debug("„%s“ added function implementation %s" % (self.classObj.name + self.getTemplateValuesString(), impl.name))
		self.funcImplementations[impl.name] = impl
		
	def getCandidates(self, funcName):
		if not funcName in self.classObj.functions:
			return findFunctionInBaseClasses(self.classObj, funcName)
		else:
			return self.classObj.functions[funcName]
		
	def getMatchingFunction(self, funcName, paramTypes):
		#print("Function „%s“ has been called with types %s (%s to choose from)" % (funcName, paramTypes, len(self.classObj.functions[funcName])))
		if not funcName in self.classObj.functions:
			candidates, baseClassImpl = findFunctionInBaseClasses(self, funcName)
		else:
			candidates = self.classObj.functions[funcName]
		
		if candidates is None:
			if funcName in self.classObj.functions:
				funcCount = len(self.classObj.functions[funcName])
			else:
				funcCount = 0
			
			raise CompilerException("No matching function found: „%s“ has been called with these types: %s (%s possibilities to choose from)" % (funcName, paramTypes, funcCount))
		
		#print(candidates[0].paramTypesByDefinition)
		winner = None
		winnerScore = 0
		for func in candidates:
			score = func.getMatchingScore(paramTypes, self)
			#debug("Candidate: %s (types by definition) with score „%s“" % (func.paramTypesByDefinition, score))
			if score > winnerScore:
				winner = func
				winnerScore = score
		
		if winner is None:
			# Laziness to the maximum!
			#if not candidates[0].cppFile.compiler.background:
			#	print("Candidates were:")
			#	for func in candidates:
			#		print(" * " + func.getName() + " " + str(func.paramTypesByDefinition).replace("''", "*").replace("'", ""))
			
			if self.getName():
				calledFunc = "%s.%s" % (self.getName(), funcName)
			else:
				calledFunc = funcName
			
			if paramTypes:
				paramsInfo = "with the parameter types %s" % paramTypes
			else:
				paramsInfo = "without any parameters"
			raise CompilerException("No matching function found for the call „%s“ %s" % (calledFunc, paramsInfo))
		
		return winner
