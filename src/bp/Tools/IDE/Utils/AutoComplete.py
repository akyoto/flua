####################################################################
# Header
####################################################################
# File:		AutoComplete utilities
# Author:   Eduard Urbach

####################################################################
# License
####################################################################
# (C) 2012  Eduard Urbach
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
# Functions
####################################################################
def buildShortcutDict(functionList):
	shortCuts = dict()
	for funcName in functionList:
		chars = funcName[0]
		previousIsUpper = False
		for char in funcName:
			if char.isupper() or char.isdigit():
				if not previousIsUpper:
					chars += char.lower()
					previousIsUpper = True
			elif previousIsUpper:
				previousIsUpper = False
				
		if chars:
			shortCuts[chars] = funcName
	return shortCuts
