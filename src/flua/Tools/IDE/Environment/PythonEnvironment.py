from flua.Tools.IDE.Environment.BaseEnvironment import *

class PythonEnvironment(BaseEnvironment):
	
	def __init__(self, rootDir):
		self.rootDir = rootDir
		self.fileExtensions = {".py"}
