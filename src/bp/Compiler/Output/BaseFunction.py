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
from bp.Compiler.Output.DataTypes import *

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
		self.classObj = None
		self.implementations = {}
		self.paramNames = []
		self.paramTypesByDefinition = []
		self.paramDefaultValues = []
		self.paramDefaultValueTypes = []
		
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
					score += 2
					continue
				else:
					return 0
			
			typeA = calledTypes[i]
			typeB = self.paramTypesByDefinition[i]
			typeB = classImpl.translateTemplateName(typeB)
			
			if typeA in nonPointerClasses:
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
			
			if typeA == typeB:
				score += 5
			elif typeA == "BigInt" and (typeB == "MemPointer<Byte>" or typeB == "~MemPointer<Byte>"):
				score += 4
			elif typeB == "":
				score += 3
			elif classImplA and classImplA.classObj.hasCast(typeB):
				score += 2
			elif canBeCastedTo(typeA, typeB):
				score += 1
			else:
				return 0
			
		return score
		
	def getInitList(self):
		stri = ""
		for param in self.paramNames:
			stri += "%s(%s), " % (param, param)
		return stri[:-2]
