#!/usr/bin/python

####################################################################
# Header
####################################################################
# Blitzprog Compiler
# 
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
# Classes
####################################################################
class Node:
    
    def __init__(self, line, parent, tabs):
        self.line = line
        if parent:
            self.parent = parent
            parent.childs.append(self)
        self.childs = list()
        self.tabs = tabs

class Compiler:
    
    def parse(self, file):
        start = time.clock()
        lineCount = 0
        currentTabs = 0
        currentNode = root = Node("", None, 0)
        lineNode = None
        
        fileIn = open(file, "r")
        
        for line in fileIn:
            lineCount += 1
            line = line.rstrip()
            if line:
                line, tabs = self.countAndRemoveTabs(line)  # optimize
                lineNode = Node(line, currentNode, tabs)
                if tabs != currentTabs:
                    if tabs > currentTabs:
                        currentNode = lineNode
                    elif tabs < currentTabs:
                        currentNode = currentNode.parent
                    currentTabs = tabs
        
        self.compile(root)
        
        out = open("Test.txt", "w")
        #writeNode(root, out)
        out.close()
        
        elapsedTime = time.clock() - start
        
        print ""
        print "Lines:   " + str(lineCount)
        print "Time:    " + str(elapsedTime * 1000) + " ms"
        
    def compile(self, node):
        line = node.line
        print line
        for child in node.childs:
            self.compile(child)
        
    def countAndRemoveTabs(self, line):
        counter = 0
        lineLength = len(line)
        while line[counter] == '\t':
            counter += 1
            if counter >= lineLength:
                break
        return (line[counter:], counter)

####################################################################
# Main
####################################################################
if __name__ == "__main__":
    try:
        compiler = Compiler()
        compiler.parse("../Math/Vector3/Vector3.bp")
    except:
        printTraceback()