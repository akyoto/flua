from bp.Compiler.Output import *
from bp.Compiler.Output.python.PythonDataTypes import *

class PythonVariable(BaseVariable):
	
	def __init__(self, name, type, value, isConst, isPointer, isPublic):
		super().__init__(name, type, value, isConst, isPointer, isPublic)
		
	def getPrototype(self):
		return self.name#adjustDataTypePY(self.type, True) + " " + self.name
