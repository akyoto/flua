####################################################################
# Header
####################################################################
# File:		Base function class
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
from flua.Compiler.Output.DataTypes import *

####################################################################
# Classes
####################################################################
class BaseFunction:
	
	def __init__(self, cppFile, node):
		self.node = node
		self.cppFile = cppFile
		self.isCast = (node.tagName == "cast-definition")
		self.isIterator = (node.tagName == "iterator-type")
		self.castToUnmanaged = False
		self.forceImplementation = False
		
		#print(node.tagName)
		
		if self.isCast:
			typeNode = getElementByTagName(node, "to")
			self.name = cppFile.parseExpr(typeNode.childNodes[0])
			
			# Replace typedefs
			#while self.name in cppFile.compiler.defines:
			#	self.name = cppFile.compiler.defines[self.name]
			self.name = cppFile.prepareTypeName(self.name)
			
			# TODO: Remove quick fix
			#if isElemNode(typeNode.childNodes[0]) and typeNode.childNodes[0].tagName == "unmanaged":
			#	self.castToUnmanaged = True
		else:
			self.name = correctOperators(getElementByTagName(node, "name").childNodes[0].nodeValue)
		
		self.name = cppFile.getNamespacePrefix() + self.name
		
		self.hasDataFlow = False
		self.overwritten = False
		self.classObj = None
		self.implementations = {}
		self.paramNames = []
		self.paramTypesByDefinition = []
		self.paramDefaultValues = []
		self.paramDefaultValueTypes = []
		
	def setOverwritten(self, flag):
		self.overwritten = flag
		self.classObj.setOverwrittenFunctions(True)
		
	def setDataFlow(self, state):
		self.hasDataFlow = True
		# TODO: Update available implementations
		
	def setForceImplementation(self, state):
		self.forceImplementation = state
		
	def isOperator(self):
		return self.node.tagName == "operator"
		
	def isSetter(self):
		return self.node.parentNode.tagName == "set"
		
	def isGetter(self):
		return self.node.parentNode.tagName == "get"
		
	def getName(self):
		if self.isSetter():
			return "set" + capitalize(self.name)
		elif self.isGetter():
			return "get" + capitalize(self.name)
		elif self.isIterator:
			return "iterator" + capitalize(self.name)
		
		return self.name
		
	def getParamNames(self):
		return self.paramNames
		
	def getParamNamesString(self):
		return ", ".join(self.paramNames)
	
	def getParamDefaultValues(self):
		return self.paramDefaultValues
		
	def getParamDefaultValueTypes(self):
		return self.paramDefaultValueTypes
	
	def getMatchingScore(self, calledTypes, classImpl):
		numCalledTypes = len(calledTypes)
		numTypesByDef = len(self.paramTypesByDefinition)
		score = 0
		
		#print(calledTypes)
		#print(self.paramTypesByDefinition)
		#print("<--------------")
		
		if numCalledTypes > numTypesByDef:
			return 0
		
		#if numCalledTypes < numTypesByDef:
			# Check for default values
		#	print("Default value check")
		#	for i in range(numCalledTypes, numTypesByDef):
		#		print("Using default value %s" % self.paramDefaultValues[i])
		#		calledTypes.append()
		#	return 0
		
		score = 1
		for i in range(numTypesByDef):
			# Default values
			if i >= numCalledTypes:
				if self.paramDefaultValues[i]:
					# Choose a number higher than 0 but lower than 1 to
					# to make the function viable but not prioritize over
					# more fitting functions.
					score += 0.01
					continue
				else:
					return 0
			
			typeA = calledTypes[i]
			typeB = self.paramTypesByDefinition[i]
			
			# TODO: Is this one the correct classImpl for typeA?
			typeA = classImpl.translateTemplateName(typeA)
			
			typeB = classImpl.translateTemplateName(typeB)
			
			if typeA in nonPointerClasses or typeA.startswith("Function("):
				classImplA = None
			else:
				classImplA = self.cppFile.getClassImplementationByTypeName(typeA)
			
			#print("---------------->")
			#print("Called as:  " + typeA)
			#print("Defined as: " + typeB)
			#print(self.paramTypesByDefinition[i])
			#print(classImpl.templateValues)
			#print(classImplA.classObj.hasCast(typeB))
			#print("<----------------")
			
			# Type A is the type the call has been requested with.
			# Type B is the type that has been defined in the function by definition.
			
			# Exact match
			if typeA == typeB:
				score += 7
			# BigInt -> String
			elif typeA == "BigInt" and (typeB == "MemPointer<Byte>" or typeB == "~MemPointer<Byte>"):
				score += 6
			# Inheritance: Derived class -> Base class
			elif self.cppFile.isDerivedClass(typeA, typeB):
				score += 5
			# A implemented a cast to B
			elif classImplA and classImplA.classObj.hasCast(typeB):
				score += 4
			# "I don't care about the type of A"
			elif typeB == "":
				score += 3
			# A can be naturally casted to B
			elif canBeCastedTo(typeA, typeB):
				score += 2
			# A is null
			elif typeA == "MemPointer<void>" and not typeB in nonPointerClasses:
				score += 1
			# Does not match
			else:
				return 0
			
		return score
		
	def getInitList(self):
		stri = ""
		for param in self.paramNames:
			stri += "%s(%s), " % (param, param)
		return stri[:-2]
