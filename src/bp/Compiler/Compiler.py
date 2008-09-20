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
# ToDo
####################################################################
#
# Parser bug: False child/parent parsing
#

####################################################################
# Classes
####################################################################
class Node:
    TypeUnknown = 0
    TypeClass = 1
    TypeKeyword = 2
    TypeFunction = 3
    
    def __init__(self, line, parent, tabs):
        self.line = line
        if parent:
            self.parent = parent
            parent.childs.append(self)
        self.childs = list()
        self.tabs = tabs
        self.type = Node.TypeUnknown

class Compiler:
    
    def __init__(self):
        self.root = Node("", None, 0)
    
    def parse(self, file):
        start = time.clock()
        lineCount = 0
        currentTabs = 0
        currentNode = self.root
        lineNode = None
        
        fileIn = open(file, "r")
        
        for line in fileIn:
            lineCount += 1
            line = line.rstrip()
            if line:
                line, tabs = self.countAndRemoveTabs(line)  # optimize
                print strTimes("    ", tabs) + line
                if tabs != currentTabs:
                    if tabs > currentTabs:
                        lineNode = Node(line, currentNode, tabs)
                        currentNode = lineNode
                    elif tabs < currentTabs:
                        currentNode = currentNode.parent
                        lineNode = Node(line, currentNode, tabs)
                    currentTabs = tabs
                else:
                    lineNode = Node(line, currentNode, tabs)
        
        self.compile(self.root)
        
        out = open("Test.txt", "w")
        #writeNode(root, out)
        out.close()
        
        elapsedTime = time.clock() - start
        
        print ""
        print "Lines:   " + str(lineCount)
        print "Time:    " + str(elapsedTime * 1000) + " ms"
        
    def compile(self, node):
        for child in node.childs:
            self.compile(child)
        self.process(node)
        
    def process(self, node):
        line = node.line
        
        if len(node.childs) > 0:
            print "*** " + str(len(node.childs)) + " *** " + node.line
            
            if startswith(line, "if"):
                node.type = Node.TypeKeyword
                condition = line[3:]
                print "IF " + condition
            
            for child in node.childs:
                if node.type == Node.TypeFunction:
                    pass
        else:
            pass
        
        firstNonVarChar = self.findFirstNonVarChar(line)
        if firstNonVarChar == -1:
            print "NAME: " + line
        elif firstNonVarChar == 0:
            if line == "...":
                print "EMPTY"
        else:   # if firstNonVarChar > 0:
            char = line[firstNonVarChar]
            if char == ' ':
                print "KEYWORD/FUNCTION"
            elif char == '.':
                print "OOP CALL"
            elif char == '=':
                print "ASSIGNMENT"
            elif char == '+':               # +=
                print "INCREMENT"
            elif char == '-':               # -=
                print "DECREMENT"
            elif char == '*':               # *=
                print "MULTIPLY"
            elif char == '/':               # /=
                print "DIVISION"
            elif char == '^':               # ^=
                print "POW"
            elif char == '[':
                print "ARRAY INDEX"
            else:
                print >>sys.stderr, "UNKNOWN CHAR"
        
    def findFirstNonVarChar(self, line):
        pos = 0
        lineLen = len(line)
        
        while pos < lineLen and isVarChar(line[pos]):
            pos += 1
            
        if pos == lineLen:
            return -1
        else:
            return pos
        
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