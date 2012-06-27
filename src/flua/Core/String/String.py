def flua_strlen(cString):
	return len(cString)
	
def flua_strlenUtf8(cString):
	return len(cString)#.decode("utf-8")
	
def flua_strlenUtf8Xchars(cString, limit):
	raise NotImplementedError()
	
def flua_insertInt():
	raise NotImplementedError()
	
# TODO: Implement this
def flua_utf8Slice(toString, fromString, fromIndex, toIndex):
	toString.data = fromString
	toString.length = 0
	toString.lengthInBytes = 0