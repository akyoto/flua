####################################################################
# Header
####################################################################
# Scope class

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

####################################################################
# Classes
####################################################################
class Scope:
	
	def __init__(self):
		self.variables = dict()

class ScopeController:
	
	def __init__(self):
		self.scopes = []
		self.scopeBackups = []
		self.nodeIdToScope = dict()
		self.pushScope()
	
	def getCurrentScope(self):
		return self.currentScope
	
	def getTopLevelScope(self):
		return self.scopes[0]
	
	def pushScope(self):
		self.currentScope = Scope()
		self.scopes.append(self.currentScope)
		
	def popScope(self):
		self.scopes.pop()
		self.currentScope = self.scopes[-1]
		
	def saveScopesForNode(self, node):
		#print("Saving node %s" % node.toxml())
		try:
			nodeId = node.lineNumber
			self.nodeIdToScope[nodeId] = list(self.scopes)
		except AttributeError:
			return
		
	def restoreScopesForNode(self, node):
		#if node in self.nodeToScope:
		self.restoreScopesForNodeId(node.lineNumber)
		
	def restoreScopesForNodeId(self, nodeId):
		self.scopes = self.nodeIdToScope[nodeId]
		self.currentScope = self.scopes[-1]
		
	def debugNodeToScope(self):
		for nodeId, scopes in self.nodeIdToScope.items():
			print("[Node: %s]" % nodeId)
			for scope in scopes:
				print("->SCOPE:")
				for var in scope.variables.values():
					print("  ->" + var.name + " : " + var.type)
		
	def saveScopes(self):
		self.scopeBackups.append(list(self.scopes))
	
	def restoreScopes(self, scopes = []):
		if not scopes:
			if len(self.scopeBackups) > 0:
				self.scopes = self.scopeBackups.pop()
		else:
			self.scopes = scopes
		
		self.currentScope = self.scopes[-1]
		
	#===========================================================================
	# def updateScopes(self):
	#	scopeBackup = self.scopes
	#	if len(self.scopeBackups) > 0:
	#		self.scopes = self.scopeBackups.pop()
	#	self.scopeBackups.append(scopeBackup)
	#===========================================================================
		
	#===========================================================================
	# def pushPrivateScopeList(self, newScopeList):
	#	oldScopeList = self.scopes
	#	self.scopeListBackups.append(oldScopeList)
	#	self.scopes = newScopeList
	#	self.pushScope()
	# 
	# def popPrivateScopeList(self):
	#	self.scopes = self.scopeListBackups.pop()
	#	self.currentScope = self.scopes[-1]
	#===========================================================================
		
	def getVariable(self, name):
		i = len(self.scopes) - 1
		while i >= 0:
			if name in self.scopes[i].variables:
				return self.scopes[i].variables[name]
			i -= 1
		
		return None
	
	def getVariableScope(self, name):
		i = len(self.scopes) - 1
		while i >= 0:
			if name in self.scopes[i].variables:
				return self.scopes[i]
			i -= 1
		
		return None
		
	def variableExists(self, name):
		i = len(self.scopes) - 1
		while i >= 0:
			if name in self.scopes[i].variables:
				return 1
			i -= 1
		
		return 0
