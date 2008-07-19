#!/usr/bin/python

####################################################################
# Header
####################################################################
# Blitzprog Compiler
# 
# Version: 0.0.0.1
# Website: www.blitzprog.de
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
from Utils import *
import time

####################################################################
# Global
####################################################################
funcs = list()
lines = list()

####################################################################
# Functions
####################################################################
def throwError(stri, lineNum, charPos = -1):
    global lines
    sys.stderr.write("Error\n")
    
    # Print line and character position
    if charPos is not -1:
        sys.stderr.write("  line " + str(lineNum) + ", char " + str(charPos + 1) + "\n")
    else:
        sys.stderr.write("  line " + str(lineNum) + "\n")
    
    # Print the line itself
    sys.stderr.write("    " + lines[lineNum].lstrip() + "\n")
    
    # Show the character
    if charPos is not -1:
        sys.stderr.write("    " + "^".rjust(charPos + 1) + "\n")
    
    # Print error message
    sys.stderr.write(stri + "\n")
    sys.stderr.flush()
    
    # TODO: Throw custom error
    sys.exit()

####################################################################
# Main
####################################################################
try:
    start = time.clock()
    out = open("../Container/Array/Array.txt", "w")
    
    linesOrig = open("../Container/Array/Array.bp", "r").readlines()
    
    for line in linesOrig:
        line = line.rstrip()
        if line == "":
            continue
        if line[0] == "#":
            continue
        lines.append(line)
        
    # Just to make sure line[index + 1] works
    lines.append("#")
    
    inClass = 0
    inMethod = 0
    
    # For every line
    for index, line in enumerate(lines):
        #print line
        
        tabs = ""
        
        # Get tabs
        # TODO: Better algorithm
        while line[0] == '\t':
            tabs += '\t'
            line = line[1:]
        
        # Top-level
        if len(tabs) == 0:
            
            # Currently top-level - so we are not in the class body
            inClass = 0
            
            # Class or function - simply a word on the top level
            if isValidVarName(line):
                
                # Get next line
                nextLine = lines[index + 1].lstrip()
                
                # Check next line - it must be a class member declaration or the init method
                if startswith(nextLine, "init") or nextLine.startswith("class"):
                    
                    # Class found
                    print "CLASS: " + line
                    inClass = 1                         # Number of tabs
                    inMethod = inClass + 1              # Number of tabs
                    
                else:
                    
                    # Function found
                    print "FUNC: " + line
        else:
            # Methods
            if len(tabs) == inClass:
                
                # Simply one word in the class body => procedure
                if isValidVarName(line):
                    print "  METH|PROC: " + line
                else:
                    # Get position of first non-var-char
                    # TODO: Optimize algo
                    firstNonVarChar = 0
                    while isVarChar(line[firstNonVarChar]):
                        firstNonVarChar += 1
                    
                    # First non-var-char
                    char = line[firstNonVarChar]
                    
                    # Method declaration with params
                    if char == ' ':
                        meth = line[:firstNonVarChar]
                        params = line[firstNonVarChar+1:]
                        print "  METH: " + meth
                        print "    PARAMS: " + params
                        
                    # Class variable declaration
                    elif char == '.':
                        if line[:firstNonVarChar] != "class":
                            print "Only 'class' member variables can be assigned in the class definition"
                        
                        # TODO: Extract assignment information
                        # ...
                        
                        print "  CLASS|MEMBER: " + line
                        
                    # Unknown character
                    else:
                        throwError("Unknown character: Expected class variable initialisation or init method", index, firstNonVarChar)
    
    out.close()
    
    elapsedTime = time.clock() - start
    
    # Print elapsed time + processed lines
    print ""
    print str(elapsedTime * 1000) + " ms"
    print "Lines: " + str(index + 1)
except SystemExit:
    pass
except:
    printTraceback()
