from bp.Compiler.Output.BaseOutputFile import *

class PythonOutputFile(BaseOutputFile):
	
	def __init__(self, compiler, file, root):
		self.currentTabLevel = 0
		
		BaseOutputFile.__init__(self, compiler, file, root)
	
	def getCode(self):
		return ""
