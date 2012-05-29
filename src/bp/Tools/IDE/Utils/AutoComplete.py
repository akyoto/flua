
def buildShortcutDict(functionList):
	shortCuts = dict()
	for funcName in functionList:
		chars = funcName[0]
		previousIsUpper = False
		for char in funcName:
			if char.isupper() or char.isdigit():
				if not previousIsUpper:
					chars += char.lower()
					previousIsUpper = True
			elif previousIsUpper:
				previousIsUpper = False
				
		if chars:
			shortCuts[chars] = funcName
	return shortCuts
