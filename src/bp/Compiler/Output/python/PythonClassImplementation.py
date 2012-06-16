from bp.Compiler.Output import *
from bp.Compiler.Output.python.PythonFunctionImplementation import *

class PythonClassImplementation(BaseClassImplementation):
	
	def __init__(self, classObj, templateValues):
		super().__init__(classObj, templateValues)
		
	def createFunctionImplementation(self, func, paramTypes):
		return PythonFunctionImplementation(self, func, paramTypes)
		
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
					stri += adjustDataTypePY(param) + "__"
				
				if clean:
					return ("_" + stri[:-2] + "_").replace(" ", "")
				else:
					return "_" + stri[:-2] + "_"
			else:
				return ""
		else:
			if self.templateValues:
				if clean:
					return "_" + "__".join(self.templateValues) + "_"
				else:
					return "_" + "__".join(self.templateValues) + "_"
			else:
				return ""

