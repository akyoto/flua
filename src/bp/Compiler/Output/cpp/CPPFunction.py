from Utils import *
from Output.cpp.datatypes import *

class CPPFunction:
	
	def __init__(self, cppFile, node):
		self.node = node
		self.cppFile = cppFile
		self.isCast = (node.tagName == "cast-definition")
		self.castToUnmanaged = False
		
		if self.isCast:
			typeNode = getElementByTagName(node, "to")
			self.name = cppFile.parseExpr(typeNode.childNodes[0])
			# TODO: Remove quick fix
			if isElemNode(typeNode.childNodes[0]) and typeNode.childNodes[0].tagName == "unmanaged":
				self.castToUnmanaged = True
		else:
			self.name = correctOperators(getElementByTagName(node, "name").childNodes[0].nodeValue)
		
		self.classObj = None
		self.implementations = {}
		self.paramNames = []
		self.paramTypesByDefinition = []
		
	def isOperator(self):
		return self.node.tagName == "operator"
		
	def getName(self):
		return self.name
		
	def getParamNames(self):
		return self.paramNames
		
	def getParamNamesString(self):
		return ", ".join(self.paramNames)
	
	def getMatchingScore(self, calledTypes, classImpl):
		numCalledTypes = len(calledTypes)
		numTypesByDef = len(self.paramTypesByDefinition)
		score = 0
		
		#print(calledTypes)
		#print(self.paramTypesByDefinition)
		#print("<--------------")
		
		if numCalledTypes > numTypesByDef:
			return 0
		elif numCalledTypes < numTypesByDef:
			# TODO: Check for default values
			return 0
		else:
			score = 1
			for i in range(numTypesByDef):
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