from bp.Compiler.Utils import *

class BaseOutputCompiler(Benchmarkable):
	
	# Abstract
	def build(self, compilerFlags, fhOut, fhErr):
		raise NotImplementedError("build")
	
	def getTargetName(self):
		raise NotImplementedError("Target name not specified")
	
	def getExePath(self):
		raise NotImplementedError()
	
	def writeToFS(self):
		raise NotImplementedError()
	
	def compile(self, inpFile):
		raise NotImplementedError()
		
	def getCompiledFiles(self):
		return self.compiledFiles
	
	# Other stuff
	def initExprParser(self):
		self.parser = getBPCExpressionParser()
	
	def getProjectDir(self):
		return self.projectDir
		
	def getCompiledFilesList(self):
		return self.compiledFilesList
		
	# Optimization
	def enableOptimization(self):
		self.optimize = True
		self.updateOptimizationFlags()
		
	def disableOptimization(self):
		self.optimize = False
		self.updateOptimizationFlags()
		
	def updateOptimizationFlags(self):
		# TODO: Module dependant setting
		self.checkDivisionByZero = True
		self.optimizeStringConcatenation = self.optimize
	
	# Building and executing
	def execute(self, exe, fhOut = sys.stdout.write, fhErr = sys.stderr.write):
		cmd = [exe]
		
		try:
			startProcess(cmd, fhOut, fhErr)
		except OSError:
			print("Can't execute '%s'" % exe)
	
	def getFileExecList(self):
		files = ""
		for cppFile in self.getCompiledFilesList():
			files += "\texec_" + cppFile.id + "();\n"
		return files
