import time

class Benchmarkable:
	def __init__(self):
		self.benchmarkName = ""
		self.benchmarkTimerStart = 0
		self.benchmarkTimerEnd = 0
	
	def startBenchmark(self, name = ""):
		self.benchmarkName = name
		self.benchmarkTimerStart = time.time()
		
	def endBenchmark(self):
		self.benchmarkTimerEnd = time.time()
		buildTime = self.benchmarkTimerEnd - self.benchmarkTimerStart
		print((self.benchmarkName + ":").ljust(69) + str(int(buildTime * 1000)).rjust(7) + " ms")
