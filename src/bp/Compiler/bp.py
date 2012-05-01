####################################################################
# Header
####################################################################
# Blitzprog Compiler
# 
# Website: blitzprog.org
# Started: 19.07.2008 (Sat, Jul 19 2008)

####################################################################
# License
####################################################################
# (C) 2008  Eduard Urbach
# 
# This file is part of Blitzprog.
# 
# Blitzprog is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Blitzprog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Blitzprog.  If not, see <http://www.gnu.org/licenses/>.

####################################################################
# Imports
####################################################################
from bp.Compiler.Input import *
from bp.Compiler.Generic import *
from bp.Compiler.Output import *
from bp.Compiler.Config import *

####################################################################
# Main
####################################################################
def bpMain(compileFile, outputDir = None):
	compileFile = fixPath(os.path.abspath(compileFile))
	outputDir = fixPath(os.path.abspath(outputDir) + "/")
	
	print("Main file: " + compileFile)
	print("Output dir: " + outputDir)
	print("Starting:")
	totalStart = time.time()
	
	# Compile
	start = time.time()
	
	bpcCompilerInstance = BPCCompiler(getModuleDir())
	bpcCompilerInstance.compile(compileFile)
	
	compileTime = time.time() - start
	
	# Post-processing
	start = time.time()
	
	bpp = BPPostProcessor(bpc)
	bpp.processExistingInputFile(bpc.getCompiledFiles()[0])
	bpcCompilerInstance.writeToFS(outputDir + "xml/")
	
	postProcessTime = time.time() - start
	
	# Parallelizer
	start = time.time()
	
	#automaticallyParallelize(dTreeByNode)
	#automaticallyParallelize(dTreeByFunctionName)
	
	autoParallelizerTime = time.time() - start
	
	# Generate
	start = time.time()
	
	cpp = CPPOutputCompiler(bpc)
	inpFile = bpc.getCompiledFiles()[0]
	cpp.compile(inpFile.file, inpFile.getRoot())
	cpp.writeToFS(outputDir)
	
	generateTime = time.time() - start
	
	# Build
	start = time.time()
	
	if buildAndExecute:
		exe = cpp.build()
	
	buildTime = time.time() - start
	totalTime = time.time() - totalStart
	
	print("")
	print("CompileTime:      " + str(int(compileTime * 1000)).rjust(8) + " ms")
	print("PostProcessTime:  " + str(int(postProcessTime * 1000)).rjust(8) + " ms")
	print("ParallelizerTime: " + str(int(autoParallelizerTime * 1000)).rjust(8) + " ms")
	print("GenerateTime:     " + str(int(generateTime * 1000)).rjust(8) + " ms")
	print("BuildTime:        " + str(int(buildTime * 1000)).rjust(8) + " ms")
	print("-----------------------------")
	print("TotalTime:        " + str(int(totalTime * 1000)).rjust(8) + " ms")
	
	# OPs
	#for opLevel in bpc.parser.operatorLevels:
	#	for op in opLevel.operators:
	#		print(op.name)
	
	# Debug data dependencies
	#debugPP("")
	#for bpPostFile in bp.compiledFiles.values():
	#	if bpPostFile.inpFile.file.endswith("/main.bpc"):
	#		debugPP("Dependencies of " + bpPostFile.inpFile.file + ":")
	print("")
	filterByName = "aosdkfoai"
	for tree in dTreeByFunctionName.values():
		if len(tree.dependencies) > 0 and len(tree.parents) == 0 and tree.name.find(".") == -1 and (not filterByName or tree.name in filterByName):
			tree.printNodes()
			print("")
	
	# GraphViz
	if buildGraphViz:
		useRoot = True
		allGraphs = "digraph Dependencies {\n"
		for tree in dTreeByFunctionName.values():
			if tree.name and tree.dependencies:
				treeLabel = tree.name
				treeID = "node" +str(id(tree.instruction))
				if useRoot:
					allGraphs += "root -> " + treeID + ";\n"
				#allGraphs += treeID + "[shape=box3d];\n"
				
				funcGraph = "subgraph %s {\n" % (treeID)
				funcGraph += tree.getGraphVizCode()
				funcGraph += "label = \"%s\";\n" % (treeLabel)
				funcGraph += "}\n"
				
				allGraphs += funcGraph
		
		if useRoot:
			allGraphs += "root [shape=circle];\n"
			allGraphs += "}"
		print(allGraphs)
	
	# Exec
	print("\nOutput:")
	if buildAndExecute:
		cpp.execute(exe)

# Main
if __name__ == '__main__':
	try:
		bpMain("Test/Input/main.bpc", "Test/Output/")
	except:
		printTraceback()
