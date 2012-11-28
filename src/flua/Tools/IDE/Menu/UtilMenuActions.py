from flua.Tools.IDE.Startup import *
from flua.Compiler import *

class UtilMenuActions:
	
	def enterCommand(self):
		self.searchEdit.hide()
		self.replaceEdit.hide()
		
		self.cmdEdit.focusNormal()
		self.cmdEdit.show()
	
	def createDefaultImplementation(self):
		if self.codeEdit:
			obj = self.codeEdit.getTextAtCursor()
			
			if obj:
				if obj[0].islower():
					self.codeEdit.makeFunction(obj)
				else:
					self.codeEdit.makeClass(obj)
			
	def jumpToDefinition(self):
		if self.codeEdit:
			obj = self.codeEdit.getTextAtCursor()
			
			if obj:
				self.jumpTo(obj)
	
	def jumpTo(self, obj):
		if not (self.codeEdit and self.codeEdit.outputCompilerData):
			return
		
		if obj[0].islower():
			allFuncs = self.codeEdit.outputCompilerData.mainNamespace.functions
			
			if obj in allFuncs:
				fileList = [x.filePath for x in allFuncs[obj]]
				typesList = [x.paramTypesByDefinition for x in allFuncs[obj]]
				
				# TODO: Make the user select a definition
				if len(typesList) >= 1:
					self.openFile(fileList[0])
					if self.codeEdit:
						self.codeEdit.jumpToFunction(allFuncs[obj][0].node)
		else:
			allClasses = self.codeEdit.outputCompilerData.mainNamespace.classes
			
			if obj in allClasses:
				classObj = allClasses[obj]
				
				self.openFile(classObj.filePath)
				if self.codeEdit:
					self.codeEdit.jumpToClass(obj)
	
	def duplicateLine(self):
		if self.codeEdit:
			tc = self.codeEdit.textCursor()
			
			tc.beginEditBlock()
			tc.select(QtGui.QTextCursor.BlockUnderCursor)
			text = tc.selectedText()
			if tc.block().position() == 0:
				text = "\n" + text
			tc.clearSelection()
			tc.insertText(text)
			tc.endEditBlock()
			
	def toggleComment(self):
		self.codeEdit.toggleCommentsSelection()
		
	def findPossibleParallelizationPoints(self):
		self.notImplemented()
		return
