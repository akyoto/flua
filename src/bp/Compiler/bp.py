####################################################################
# Header
####################################################################
# Blitzprog Compiler
# 
# Website: www.blitzprog.com
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
from Input import *
from Generic import *
from Output import *

####################################################################
# Main
####################################################################
if __name__ == '__main__':
	try:
		print("Starting:")
		totalStart = time.clock()
		
		# Compile
		start = time.clock()
		
		bpc = BPCCompiler("../../")
		bpc.compile("Test/Input/main.bpc")
		
		compileTime = time.clock() - start
		
		# Post-processing
		start = time.clock()
		
		bp = BPPostProcessor(bpc)
		bp.process(bpc.getCompiledFiles()[0])
		
		postProcessTime = time.clock() - start
		
		# Generate
		start = time.clock()
		
		cpp = CPPOutputCompiler(bpc)
		cpp.compile(bpc.getCompiledFiles()[0])
		cpp.writeToFS("Test/Output/")
		
		generateTime = time.clock() - start
		
		# Build
		start = time.clock()
		
		exe = cpp.build()
		
		buildTime = time.clock() - start
		totalTime = time.clock() - totalStart
		
		print("")
		print("CompileTime:      " + str(compileTime * 1000).rjust(8) + " ms")
		print("PostProcessTime:  " + str(postProcessTime * 1000).rjust(8) + " ms")
		print("GenerateTime:     " + str(generateTime * 1000).rjust(8) + " ms")
		print("BuildTime:        " + str(buildTime * 1000).rjust(8) + " ms")
		print("-----------------------------")
		print("TotalTime:        " + str(totalTime * 1000).rjust(8) + " ms")
		
		# Exec
		print("\nOutput:")
		cpp.execute(exe)
	except:
		printTraceback()