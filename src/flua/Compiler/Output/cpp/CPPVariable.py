from flua.Compiler.Output import *
from flua.Compiler.Output.cpp.DataTypes import *

class CPPVariable(BaseVariable):
	
	def __init__(self, name, type, value, isConst, isPointer, isPublic):
		super().__init__(name, type, value, isConst, isPointer, isPublic)
		
	def getPrototype(self):
		return "%s %s" % (adjustDataTypeCPP(self.type, True), self.name)
