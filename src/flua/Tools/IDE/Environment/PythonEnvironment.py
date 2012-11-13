from flua.Tools.IDE.Environment.BaseEnvironment import *
import keyword

class PythonEnvironment(BaseEnvironment):
	
	def __init__(self, rootDir, action):
		BaseEnvironment.__init__(self, action)
		
		self.name = "Python 3"
		self.rootDir = rootDir
		self.fileExtensions = {".py"}
		self.standardFileExtension = ".py"
		self.singleLineCommentIndicators = {"#"}
		self.selfReferences = {"self"}
		
		self.autoCompleteKeywords = keyword.kwlist
		self.highlightKeywords = self.autoCompleteKeywords
		self.internalFunctions = __builtins__.keys()
