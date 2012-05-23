####################################################################
# Header
####################################################################
# File:		Namespace class
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
# Classes
####################################################################
class BaseNamespace:
	
	def __init__(self, name):
		self.name = name
		self.namespaces = {}
		self.classes = {}
		self.functions = {}
		self.externFunctions = {}
		self.implementations = {}
	
	def getPrefix(self):
		return self.name + "_"
	
	def hasClassByName(self, name):
		return name in self.classes
