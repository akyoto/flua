from flua.Tools.IDE.Environment.BaseEnvironment import *
from flua.Compiler.Config import *

class FluaEnvironment(BaseEnvironment):
	
	def __init__(self, rootDir, action):
		BaseEnvironment.__init__(self, action)
		
		self.name = "Flua"
		self.rootDir = rootDir
		self.fileExtensions = {".flua"}
		self.standardFileExtension = ".flua"
		self.singleLineCommentIndicators = {"#"}
		self.selfReferences = {"my", "self", "this"}
		
		self.autoCompleteKeywords = {
			'and', 'assert', 'atomic',
			'begin', 'break',
			'class', 'continue', 'const', 'case', 'catch', 'compilerflags', 'counting',
			'define',
			'elif', 'else', 'ensure', 'extern', 'extends',
			'for', 'false',
			'get',
			'if', 'in', 'include', 'import', 'iterator', 'interface', 'implements',
			'not', 'namespace', 'null',
			'or', 'operator', 'on',
			'pattern', 'private', 'parallel', 'public', 'pfor',
			'return', 'require',
			'set', 'shared', 'switch',
			'to', 'try', 'template', 'target', 'throw', 'true', 'test',
			'until',
			'while',
			'yield',
		}
		
		self.highlightKeywords = set(list(self.autoCompleteKeywords) + [
			# Ruby syntax
			'elsif', 'end',
			
			# C++ syntax
			'new',
			
			# Python syntax
			'def',
		])
