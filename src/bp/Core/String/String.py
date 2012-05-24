def bp_strlen(cString):
	return len(cString)
	
def bp_strlen_utf8(cString):
	return len(cString)#.decode("utf-8")
	
def bp_strlen_utf8_xchars(cString, limit):
	raise NotImplementedError()
	
def bp_insertInt():
	raise NotImplementedError()
	
# TODO: Implement this
def bp_utf8_slice(toString, fromString, fromIndex, toIndex):
	toString.data = fromString
	toString.length = 0
	toString.lengthInBytes = 0