import sys

def bp_write(x):
	sys.stdout.write(x)
	
def bp_write_xbytes(ptr, numBytes):
	sys.stdout.write(bytes(ptr).decode("utf-8")[:numBytes])
	
def bp_writeln(x):
	if x == True:
		print("true")
	elif x == False:
		print("false")
	else:
		print(x)
	
def bp_flush():
	sys.stdout.flush()