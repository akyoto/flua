from bp.Compiler.Output import *
from bp.Compiler.Output.cpp.datatypes import *

class CPPVariable(BaseVariable):
	
	def __init__(self, name, type, value, isConst, isPointer, isPublic):
		super().__init__(name, type, value, isConst, isPointer, isPublic)
		
	def getPrototype(self):
		return adjustDataTypeCPP(self.type, True) + " " + self.name
