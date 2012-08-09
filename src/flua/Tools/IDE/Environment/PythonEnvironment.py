from flua.Tools.IDE.Environment.BaseEnvironment import *

class PythonEnvironment(BaseEnvironment):
	
	def __init__(self, rootDir, action):
		BaseEnvironment.__init__(self, action)
		
		self.name = "Python 3"
		self.rootDir = rootDir
		self.fileExtensions = {".py"}
		self.standardFileExtension = ".py"
