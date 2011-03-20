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
import os

####################################################################
# Functions
####################################################################

def isVarChar(char):
	return char.isalnum() or char == '_'

def startsWith(stri = str, prefix = str):
	stri = stri.lower()
	prefix = prefix.lower()
	return stri.startswith(prefix) and (len(prefix) == len(stri) or stri[len(prefix)].isspace())

def stripExt(stri):
	pos = stri.rfind(".")
	if pos != -1:
		return stri[:pos]
	return stri

def stripAll(path):
	return stripExt(os.path.basename(path))

def getNextWhitespacePos(stri, fromIndex):
	striLen = len(stri)
	while fromIndex < striLen and not stri[fromIndex].isspace():
		fromIndex += 1
	if fromIndex == striLen:
		return -1
	return fromIndex

def getNextNonWhitespacePos(stri, fromIndex):
	striLen = len(stri)
	while fromIndex < striLen and stri[fromIndex].isspace():
		fromIndex += 1
	if fromIndex == striLen:
		return -1
	return fromIndex