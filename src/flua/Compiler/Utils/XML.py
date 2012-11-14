####################################################################
# Header
####################################################################
# String functions

####################################################################
# License
####################################################################
# This file is part of Flua.

# Flua is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Flua is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Flua.  If not, see <http://www.gnu.org/licenses/>.

####################################################################
# Imports
####################################################################
from xml.dom.minidom import *
import codecs
from flua.Compiler.Utils.Debug import *

####################################################################
# Global
####################################################################

binaryOperatorTagToSymbol = dict()

####################################################################
# Functions
####################################################################

def getMetaData(node, metaTag):
	metaNode = getElementByTagName(node, "meta")
	if not metaNode:
		return ""
	
	metaTagNode = getElementByTagName(metaNode, metaTag)
	if not metaTagNode:
		return ""
	
	return metaTagNode.firstChild.nodeValue

def createMetaDictFromNode(metaNode):
	meta = dict()
	for child in metaNode.childNodes:
		meta[child.tagName] = child.firstChild.nodeValue
	return meta
	
def getMetaDataBool(node, metaTag):
	return False
	
def isMetaDataTrue(stri):
	if not stri:
		return False
	
	stri = stri.lower()
	return stri == "true" or stri == "yes"
	
def isMetaDataTrueByTag(node, metaTag):
	return isMetaDataTrue(getMetaData(node, metaTag))
	
def isNot2ndAccessNode(node):
	return (node.parentNode.parentNode.tagName != "access" or node == node.parentNode.parentNode.firstChild.firstChild)
	
def findNodes(node, nodeName):
	callList = []
	
	if node.nodeType == Node.ELEMENT_NODE and node.tagName == nodeName: # or tagName(node) == "new":
		callList.append(node)
	
	# TODO: Improve performance, make an iterative algorithm out of this:
	for child in node.childNodes:
		callList += findNodes(child, nodeName)
	
	return callList
	
def findCalls(node):
	# Ignore text nodes
	if node.nodeType != Node.ELEMENT_NODE:
		return []
	
	# This will disable recursive block checking so that only the current line is being displayed
	if node.tagName == "code":
		return []
	
	callList = []
	
	if node.tagName in {"call", "new"}: # or tagName(node) == "new":
		callList.append(node)
	
	# TODO: Improve performance, make an iterative algorithm out of this:
	for child in node.childNodes:
		if child.nodeType == Node.ELEMENT_NODE:
			callList += findCalls(child)
	
	return callList
	
def findCallsReversed(node):
	calls = findCalls(node)
	calls.reverse()
	return calls
	
def getNodeComments(node):
	docs = []
	while tagName(node.previousSibling) == "comment":
		node = node.previousSibling
		docs.insert(0, decodeCDATA(node.firstChild.nodeValue).strip())
		
	if docs:
		doc = "# " + " ".join(docs).replace("#", "➘")
		
		#if doc[-1] != ".":
		#	doc += "."
		
		return doc + "\n"
	else:
		return ""
	
# Check whether node has some usable content
def nodeIsValid(node):
	return (node is not None) and (node.nodeType != Node.TEXT_NODE or node.nodeValue != "")

def encodeCDATA(data):
	if not data:
		return "\\E"
	return data.replace("\t", "\\T").replace(" ", "\\S")
	
def decodeCDATA(data):
	if data != "\\E":
		return data.replace("\\T", "\t").replace("\\S", " ")
	return ""
	
def isTextNode(node):
	if node is None:
		return False
	return node.nodeType == Node.TEXT_NODE

def isElemNode(node):
	if node is None:
		return False
	return node.nodeType == Node.ELEMENT_NODE

def getElementByTagName(node, name):
	for child in node.childNodes:
		if child.nodeType == Node.ELEMENT_NODE and child.tagName == name:
			return child

def getFuncNameNode(node):
	if getElementByTagName(node, "function"):
		return getElementByTagName(node, "function").childNodes[0]
	else:
		#if getElementByTagName(node, "operator"):
		return getElementByTagName(node, "operator").childNodes[0]
		#else:
		#	raise CompilerException("Invalid function call")

def tagName(node):
	if node is None:
		return ""
	elif node.nodeType == Node.TEXT_NODE:
		return ""#node.nodeValue
	else:
		return node.tagName

def getLeftMostOperatorNode(node):
	if (not node.childNodes):
		return node
	
	while node.firstChild:
		node = node.firstChild
		
	return node

def loadXMLFile(fileName):
	with codecs.open(fileName, "r", "utf-8") as inStream:
		xmlCode = inStream.read()
	
	# TODO: Remove all BOMs
	if len(xmlCode) and xmlCode[0] == '\ufeff': #codecs.BOM_UTF8:
		xmlCode = xmlCode[1:]
	
	xmlCode = xmlCode.replace("\r", "")
	
	# Remove whitespaces
	# TODO: Ignore flua_strings!
	headerEnd = xmlCode.find("</header>")
	pos = xmlCode.find("\t", headerEnd)
	while pos != -1:
		xmlCode = xmlCode.replace("\t", "")
		pos = xmlCode.find("\t", headerEnd)
		
	pos = xmlCode.find("\n", headerEnd)
	while pos != -1:
		xmlCode = xmlCode.replace("\n", "")
		pos = xmlCode.find("\n", headerEnd)
	
	return xmlCode
