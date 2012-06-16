def bp_strlen(cString):
	return len(cString)
	
def bp_strlenUtf8(cString):
	return len(cString)#.decode("utf-8")
	
def bp_strlenUtf8Xchars(cString, limit):
	raise NotImplementedError()
	
def bp_insertInt():
	raise NotImplementedError()
	
# TODO: Implement this
def bp_utf8Slice(toString, fromString, fromIndex, toIndex):
	toString.data = fromString
	toString.length = 0
	toString.lengthInBytes = 0