import sys

def flua_write(x):
	sys.stdout.write(x)
	
def flua_writeXbytes(ptr, numBytes):
	sys.stdout.write(bytes(ptr).decode("utf-8")[:numBytes])
	
def flua_writeXbytesLine(ptr, numBytes):
	print(bytes(ptr).decode("utf-8")[:numBytes])
	
def flua_writeln(x):
	if x == True:
		print("true")
	elif x == False:
		print("false")
	else:
		print(x)
	
def flua_flush():
	sys.stdout.flush()