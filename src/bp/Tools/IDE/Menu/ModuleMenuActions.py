from bp.Tools.IDE.Startup import *
from bp.Compiler import *

class ModuleMenuActions:
	
	def onRunModule(self):
		self.runModule([])
	
	def runModuleTests(self):
		self.notImplemented()
	
	def runProfiler(self):
		self.notImplemented()
	
	def runDebug(self):
		self.runModule([
			"-ggdb",
		])
	
	def runModuleOptimized(self):
		self.runModule([
			"-O3",
			"-march=native",
			"-mtune=native",
		])
	
	def runModule(self, compilerFlags = []):
		if self.codeEdit is None or self.currentWorkspace.count() == 0 or self.codeEdit.isTextFile:
			return
		
		if self.running > 0 or self.compiling > 0:
			return
		
		# Console
		#self.console.log.setPlainText("")
		self.console.compiler.setPlainText("")
		self.console.output.setPlainText("")
		
		self.console.activate("Compiler")
		self.console.watch(self.console.compiler)
		
		self.console.setMinimumHeight(220)
		self.consoleDock.show()
		
		# Set compiling flag
		self.compiling += 1
		
		debugMode = ("-ggdb" in compilerFlags)
		optimizeMode = ("-O3" in compilerFlags)
		
		# Make sure the XML is up 2 date
		if self.codeEdit.updateQueue:
			# We first need to end parsing!
			# Disable the stupid threads!
			self.codeEdit.threaded = False
			self.codeEdit.onUpdateTimeout()
			self.codeEdit.threaded = True
		
		# General
		if self.codeEdit.bubble:
			self.codeEdit.bubble.hide()
		
		self.codeEdit.save(msgStatusBar = False)
		
		if self.codeEdit:
			self.codeEdit.msgView.clear()
		
		# Target dependant
		outputTarget = self.targetSwitcher.currentText()
		
		#print(self.processor.getCompiledFilesList())
		try:
			if not self.backgroundCompileIsUpToDate:
				self.createOutputCompiler(outputTarget)
				
				#exePath = cpp.getExePath().replace("/", "\\")
				#if exePath and os.path.isfile(exePath):
				#	print("Removing %s" % exePath)
				#	os.remove(exePath)
				
				bpPostPFile = self.getCurrentPostProcessorFile()
				
				# Generate
				self.startBenchmark("%s Generator" % outputTarget)
				self.outputCompiler.compile(bpPostPFile)
				self.outputCompiler.writeToFS()
				self.endBenchmark()
			else:
				# Information is up to date, just write it to the disk
				self.startBenchmark("%s Generator (write files to disk)" % outputTarget)
				self.outputCompiler.writeToFS()
				self.endBenchmark()
			
			# Build
			self.startBenchmark("%s Build" % outputTarget)
			exitCode = self.outputCompiler.build(compilerFlags, fhOut = self.console.compiler.write, fhErr = self.console.compiler.writeError)
			
			if exitCode != 0:
				#print("%s compiler error (see other console window, exit code %d)" % (outputTarget, exitCode))
				return
			
			print("-" * 80)
			self.endBenchmark()
			
			exe = self.outputCompiler.getExePath()
			
			if debugMode:
				print("Using debug mode.")
			elif optimizeMode:
				print("Using optimizations.")
			else:
				print("No optimizations active.")
			
			if exe:
				# Windows DLLs
				if outputTarget.startswith("C++") and os.name == "nt":
					print("Using DLLs in path: %s" % getDLLDir())
				
				print("Executing: %s" % exe)
				print("-" * 80)
				
				exeDir = extractDir(exe)
				os.chdir(exeDir)
				
				self.console.activate("Output")
				self.console.output.setFocus()
				
				self.runThread.startWith(exe, debugMode)
			else:
				print("Couldn't find executable file.\nBuild for this target is probably not implemented yet.")
		except OutputCompilerException as e:
			self.displayOutputCompilerException(e)
		except:
			printTraceback()
		finally:
			if self.compiling > 0:
				self.compiling -= 1
			
			self.console.watch(self.console.log)
		
		#cpp.compile(self.file, self.codeEdit.root)
		
	def displayOutputCompilerException(self, e):
		if not self.codeEdit:
			return
		
		#lineNumber = e.getLineNumber()
		node = e.getLastParsedNode()
		
		if 0:#self.developerFlag:
			#print(e.getMsg())
			
			if node:
				print("Last parsed node:\n" + node.toxml())
				
			self.consoleDock.show()
		else:
			errorMessage = e.getMsg()
			self.codeEdit.msgView.addLineBasedMessage(e.getFilePath(), e.getLineNumber(), errorMessage)
			
			if not self.developerFlag:
				self.consoleDock.hide()
			#self.codeEdit.msgView.updateView()
		
	def showModuleProperties(self):
		if self.codeEdit is None or not self.currentWorkspace.count():
			return
		
		self.moduleProperties, existed = self.getUIFromCache("module-properties")
		if not existed:
			self.moduleProperties.optimizeFor.currentIndexChanged.connect(self.setOptimizationOptions)
			self.moduleProperties.setStyleSheet(self.config.dialogStyleSheet)
		
		filePath = self.getFilePath()
		modulePath = self.localToGlobalImport(stripAll(filePath))
		if modulePath:
			parts = self.splitModulePath(modulePath)
			self.moduleProperties.modName.setText(".".join(parts))
			self.moduleProperties.companyName.setText(parts[0])
			if len(parts) > 1:
				self.moduleProperties.projectName.setText(parts[1])
			else:
				self.moduleProperties.projectName.setText("")
		else:
			self.moduleProperties.modName.setText("Your module is stored outside of the global repository. Please change this.")
			self.moduleProperties.companyName.setText("No company associated. Please create a directory in the global repository.")
			self.moduleProperties.projectName.setText("")
		
		if os.path.isfile(filePath):
			created = os.path.getctime(filePath)
			modified = os.path.getmtime(filePath)
			
			self.moduleProperties.dateCreated.setText(time.ctime(created))
			self.moduleProperties.dateModified.setText(time.ctime(modified))
		else:
			self.moduleProperties.dateCreated.setText("-")
			self.moduleProperties.dateModified.setText("-")
		
		self.setOptimizationOptions(self.moduleProperties.optimizeFor.currentIndex())
		self.moduleProperties.exec()
	
	def setOptimizationOptions(self, index):
		# 0: Speed
		if index == 0:
			self.moduleProperties.useBigInt.setChecked(False)
			self.moduleProperties.useRequirements.setChecked(False)
			self.moduleProperties.useArrayRequirements.setChecked(False)
			self.moduleProperties.useDivisionByZeroCheck.setChecked(False)
		# 1: Correctness
		elif index == 1:
			self.moduleProperties.useBigInt.setChecked(True)
			self.moduleProperties.useRequirements.setChecked(True)
			self.moduleProperties.useArrayRequirements.setChecked(True)
			self.moduleProperties.useDivisionByZeroCheck.setChecked(True)
		# 2: Custom
		else:
			pass
