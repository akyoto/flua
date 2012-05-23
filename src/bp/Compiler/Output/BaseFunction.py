from bp.Compiler.Utils import *
from bp.Compiler.Output.DataTypes import *

class BaseFunction:
	
	def __init__(self, cppFile, node):
		self.node = node
		self.cppFile = cppFile
		self.isCast = (node.tagName == "cast-definition")
		self.castToUnmanaged = False
		self.forceImplementation = False
		
		if self.isCast:
			typeNode = getElementByTagName(node, "to")
			self.name = cppFile.parseExpr(typeNode.childNodes[0])
			
			# Replace typedefs
			while self.name in cppFile.compiler.defines:
				self.name = cppFile.compiler.defines[self.name]
			
			# TODO: Remove quick fix
			#if isElemNode(typeNode.childNodes[0]) and typeNode.childNodes[0].tagName == "unmanaged":
			#	self.castToUnmanaged = True
		else:
			self.name = correctOperators(getElementByTagName(node, "name").childNodes[0].nodeValue)
		
		self.classObj = None
		self.implementations = {}
		self.paramNames = []
		self.paramTypesByDefinition = []
		self.paramDefaultValues = []
		self.paramDefaultValueTypes = []
		
	def setForceImplementation(self, state):
		self.forceImplementation = state
		
	def isOperator(self):
		return self.node.tagName == "operator"
		
	def getName(self):
		if self.node.parentNode.tagName == "set":
			return "set" + capitalize(self.name)
		elif self.node.parentNode.tagName == "get":
			return "get" + capitalize(self.name)
		
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
			
#				print(typeA)
#				print(typeB)
#				print(self.paramTypesByDefinition[i])
#				print(classImpl.translateTemplateName("Tradius"))
#				print(classImpl.templateValues)
#				print("---------------->")
			
			if typeA == typeB:
				score += 4
			elif typeA == "BigInt" and (typeB == "MemPointer<Byte>" or typeB == "~MemPointer<Byte>"):
				score += 3
			elif typeB == "":
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
