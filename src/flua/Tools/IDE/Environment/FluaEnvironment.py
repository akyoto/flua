from flua.Tools.IDE.Environment.BaseEnvironment import *
from flua.Compiler.Config import *

class FluaEnvironment(BaseEnvironment):
	
	def __init__(self, rootDir):
		self.rootDir = rootDir
		self.fileExtensions = {".flua"}
