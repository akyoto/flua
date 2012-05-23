class BaseVariable:
	
	def __init__(self, name, type, value, isConst, isPointer, isPublic):
		self.name = name
		self.type = type
		self.value = value
		self.isConst = isConst
		self.isPointer = isPointer
		self.isPublic = isPublic
		self.classImpl = None
		
	def getPrototype(self):
		raise NotImplementedError()
