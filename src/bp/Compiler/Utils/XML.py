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

####################################################################
# Functions
####################################################################

# Check whether node has some usable content
def nodeIsValid(node):
	return (node is not None) and (node.nodeType != Node.TEXT_NODE or node.nodeValue != "")

def isTextNode(node):
	if node is None:
		return False
	return node.nodeType == Node.TEXT_NODE

def tagName(node):
	if node is None:
		return ""
	elif(isTextNode(node)):
		return node.nodeValue
	else:
		return node.tagName