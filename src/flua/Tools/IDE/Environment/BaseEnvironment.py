from flua.Compiler.Output.BaseNamespace import *

class BaseEnvironment:
	
	def __init__(self, action):
		self.name = "Base"
		self.rootDir = ""
		self.mainNamespace = BaseNamespace("", None)
		self.fileExtensions = {}
		self.standardFileExtension = ""
		self.autoCompleteKeywords = {}
		self.highlightKeywords = {}
		self.singleLineCommentIndicators = {}
		self.preprocessorIndicators = {}
		self.internalDataTypes = {}
		self.internalFunctions = {}
		self.specialKeywords = {}
		self.selfReferences = {}
		self.defines = {}
		self.action = action
		
		self.operators = {
			'=',
			# Comparison
			'==', '!=', '<', '<=', '>', '>=',
			# Arithmetic
			'\+', '-', '\*', '/', '//', '\%', '\*\*', '\^',
			# In-place
			'\+=', '-=', '\*=', '/=', '\%=',
			# Bitwise
			'\^', '\|', '\&', '\~', '>>', '<<',
			# Data Flow
			'<-', '->', '<--', '-->',
			# Type declaration
			':',
			# Tilde
			'~',
		}
		
		self.braces = {
			'(', ')', '[', ']', '{', '}',
		}
