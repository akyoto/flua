# Functions
def bp_copyMem(source, dest, num):
	for i in range(num):
		dest[i] = source[i]

def bp_compareMem(source, dest, num):
	for i in range(num):
		if source[i] != dest[i]:
			return False
	
	return True

def bp_setMem(dest, value, num):
	for i in range(num):
		dest[i] = value

# MemPointer emulator - 'emulator' sounds slow, eh? It probably is.
# I should probably make a faster implementation.
class BPMemPointer:
	
	def __init__(self, fromStringOrSize, startPos = 0):
		if isinstance(fromStringOrSize, int):
			self.data = [0] * fromStringOrSize
		else:
			self.data = fromStringOrSize
		
		self.pos = startPos
		
	def __add__(self, offset):
		return BPMemPointer(self.data, self.pos + offset)
		
	def __getitem__(self, index):
		return self.data[self.pos + index]
	
	def __setitem__(self, index, value):
		self.data[self.pos + index] = value
				
	def __len__(self):
		return len(self.data) - self.pos
		
	def __str__(self):
		if self.pos == 0:
			return bytes(self.data).decode("utf-8")
		else:
			return bytes(self.data[self.pos:]).decode("utf-8")