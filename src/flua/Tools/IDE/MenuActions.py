from flua.Tools.IDE.Startup import *
from flua.Tools.IDE.Menu import *
import flua.Compiler.Input.bpc.BPCUtils as bpcUtils

class MenuActions(
		FileMenuActions,
		EditMenuActions,
		ModuleMenuActions,
		RepositoryMenuActions,
		UtilMenuActions,
		HelpMenuActions
	):
	
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
		
	def viewSource(self):
		if not self.codeEdit:
			return
		
		filePath = self.getFilePath()
		
		# TODO: Remove hardcoded stuff...
		sourceFile = extractDir(filePath) + "C++/" + stripAll(filePath) + ".hpp"
		
		if os.path.exists(sourceFile):
			self.openFile(sourceFile)
			return
		
	def switchSyntax(self, index):
		bpcUtils.currentSyntax = index
		
		ceList = []
		self.forEachCodeEditDo(lambda ce: ceList.append(ce))
		
		for ce in ceList:
			if not ce.isTextFile and os.path.isfile(ce.getFilePath()):
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
		# Save scribble text
		self.scribble.saveScribble()
		
		self.dockVisibility = dict()
		for x in self.docks:
			self.dockVisibility[x] = x.isVisible()
		
		# Replace clipboard references with an actual copy
		# so that we can access the copied text after the
		# application has quit.
		clipboard = QtGui.QApplication.clipboard()
		event = QtCore.QEvent(QtCore.QEvent.Clipboard)
		QtGui.QApplication.sendEvent(clipboard, event)
		
		# Go ahead quitting the app
		event.accept()
		
		## TODO: Check files opened
		#reply = QtGui.QMessageBox.question(self,
		#		"Message",
		#		"Are you sure you want to quit?",
		#		QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
		#		QtGui.QMessageBox.No)
		#
		#if reply == QtGui.QMessageBox.Yes:
		#	event.accept()
		#else:
		#	event.ignore()
		
	def notImplemented(self):
		self.notify("Not implemented yet.")
