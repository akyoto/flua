from bp.Tools.IDE.Startup import *
from bp.Tools.IDE.Menu import *
import bp.Compiler.Input.bpc.BPCUtils as bpcUtils

class MenuActions(FileMenuActions, EditMenuActions, ModuleMenuActions, HelpMenuActions):
	
	def ask(self, question, title = "Message"):
		return QtGui.QMessageBox.question(self,
				title,
				question,
				QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
				QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes
	
	def askText(self, labelText, info = "", title = "Message"):
		self.textInput, existed = self.getUIFromCache("text-input")
		
		if not existed:
			self.textInput.setStyleSheet(self.config.dialogStyleSheet)
		
		self.textInput.textWidget.setText("")
		self.textInput.labelWidget.setText(labelText)
		
		if info:
			self.textInput.infoWidget.setText(info)
			self.textInput.infoWidget.adjustSize()
			self.textInput.adjustSize()
			self.textInput.infoWidget.show()
		else:
			self.textInput.infoWidget.hide()
		
		self.textInput.setWindowTitle(title)
		dialogCode = self.textInput.exec()
		
		if dialogCode == QtGui.QDialog.Accepted:
			return self.textInput.textWidget.text()
		else:
			return False
		
	def toggleFullScreen(self):
		self.geometryState = self.saveState()
		if self.isFullScreen():
			self.showNormal()
		else:
			self.showFullScreen()
		
	def switchSyntax(self, index):
		bpcUtils.currentSyntax = index
		
		ceList = []
		self.forEachCodeEditDo(lambda ce: ceList.append(ce))
		
		for ce in ceList:
			ce.reload()
			#ce.updater.run()
			#ce.updater.finished.emit()
			#ce.compilerFinished()
			#ce.highlighter.rehighlight()
			
			#self.postProcessorThread.codeEdit = ce
			#self.postProcessorThread.run()
			#self.postProcessorFinished()
			
			#ce.rehighlightFunctionUsage()
	
	def closeEvent(self, event):
		self.scribble.saveScribble()
		event.accept()
		return
		
		# TODO: Check files opened
		reply = QtGui.QMessageBox.question(self,
				"Message",
				"Are you sure you want to quit?",
				QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
				QtGui.QMessageBox.No)
		
		if reply == QtGui.QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()
			
	def notImplemented(self):
		self.notify("Not implemented yet.")
