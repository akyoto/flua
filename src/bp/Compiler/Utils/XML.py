####################################################################
# Header
####################################################################
# String functions

####################################################################
# License
####################################################################
# This file is part of Blitzprog.

# Blitzprog is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Blitzprog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Blitzprog.  If not, see <http://www.gnu.org/licenses/>.

####################################################################
# Imports
####################################################################
from xml.dom.minidom import *
import codecs

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
	
def findNodes(node, nodeName):
	callList = []
	
	if tagName(node) == nodeName:# or tagName(node) == "new":
		callList.append(node)
	
	for child in node.childNodes:
		callList += findNodes(child, nodeName)
	
	return callList
	
def findCalls(node):
	return findNodes(node, "call")
	
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
		doc = "# " + " ".join(docs)
		
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
	return node.nodeType != Node.TEXT_NODE

def getElementByTagName(node, name):
	for child in node.childNodes:
		if child.nodeType != Node.TEXT_NODE and child.tagName == name:
			return child

def getFuncNameNode(node):
	if getElementByTagName(node, "function"):
		return getElementByTagName(node, "function").childNodes[0]
	else:
		return getElementByTagName(node, "operator").childNodes[0]

def tagName(node):
	if node is None:
		return ""
	elif node.nodeType == Node.TEXT_NODE:
		return ""#node.nodeValue
	else:
		return node.tagName

def loadXMLFile(fileName):
	with codecs.open(fileName, "r", "utf-8") as inStream:
		xmlCode = inStream.read()
	
	# TODO: Remove all BOMs
	if len(xmlCode) and xmlCode[0] == '\ufeff': #codecs.BOM_UTF8:
		xmlCode = xmlCode[1:]
	
	xmlCode = xmlCode.replace("\r", "")
	
	# Remove whitespaces
	# TODO: Ignore bp_strings!
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
