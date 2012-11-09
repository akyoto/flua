from flua.Tools.IDE.Environment.BaseEnvironment import *
from flua.Compiler.Config import *

class GLSLEnvironment(BaseEnvironment):
	
	def __init__(self, rootDir, action):
		BaseEnvironment.__init__(self, action)
		
		self.name = "GLSL"
		self.rootDir = rootDir
		self.fileExtensions = {".glsl"}
		self.standardFileExtension = ".glsl"
		self.singleLineCommentIndicators = {"//"}
		#self.selfReferences = {"my", "self", "this"}
		
		self.autoCompleteKeywords = {
			'varying', 'uniform', 'attribute', 
		}
		
		self.highlightKeywords = self.autoCompleteKeywords
		
		self.internalDataTypes = {
			# C
			'char', 'bool', 'void', 'int', 'float', 'double', 'short', 'unsigned',
			
			# GLSL
			'vec2', 'vec3', 'vec4',
			'bvec2', 'bvec3', 'bvec4',
			'ivec2', 'ivec3', 'ivec4',
			'mat2', 'mat3', 'mat4',
			'sampler1D', 'sampler2D', 'sampler3D', 'samplerCube',
			'sampler1DShadow', 'sampler2DShadow',
		}
		
		self.internalFunctions = {
			'texture2D'
		}
