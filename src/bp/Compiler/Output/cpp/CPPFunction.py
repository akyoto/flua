from Utils import *
from Output.cpp.datatypes import *

class CPPFunction:
	
	def __init__(self, cppFile, node):
		self.node = node
		self.cppFile = cppFile
		self.name = correctOperators(getElementByTagName(node, "name").childNodes[0].nodeValue)
		self.classObj = None
		self.implementations = {}
		self.paramNames = []
		
	def isOperator(self):
		return self.node.tagName == "operator"
		
	def getName(self):
		return self.name
		
	def getParamNames(self):
		return self.paramNames
		
	def getParamNamesString(self):
		return ", ".join(self.paramNames)
	
	def getInitList(self):
		stri = ""
		for param in self.paramNames:
			stri += "%s(%s), " % (param, param)
		return stri[:-2]