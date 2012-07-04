from flua.Tools.IDE.Startup import *
from flua.Compiler import *

class UtilMenuActions:
	
	def createDefaultImplementation(self):
		if self.codeEdit:
			self.codeEdit.createDefaultImplementation()
			
	def jumpToDefinition(self):
		self.notImplemented()
		return
		
		if self.codeEdit:
			self.codeEdit.getTextAtCursor()
			
	def duplicateLine(self):
		self.notImplemented()
		return
		
		if self.codeEdit:
			self.codeEdit.getTextAtCursor()
