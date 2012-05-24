import sys

def bp_print(x):
	#sys.stdout.write(x)
	if str(x).isdigit():
		sys.stdout.write(chr(x))
	else:
		sys.stdout.write(x.decode("utf-8"))
	
def bp_flush():
	sys.stdout.flush()