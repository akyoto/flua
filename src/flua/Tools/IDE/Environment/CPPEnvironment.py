from flua.Tools.IDE.Environment.BaseEnvironment import *

class CPPEnvironment(BaseEnvironment):
	
	def __init__(self, rootDir):
		self.rootDir = rootDir
		self.fileExtensions = {".cpp", ".cxx", ".c", ".hpp", ".h"}
