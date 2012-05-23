# Just testing some new syntax stuff.

String
	iterator
		line
			return my.until("\n")
			
		word
			return my.nextWord()
			
		char
			return my.nextChar()

# line, word, char
# or
# lines, words, chars ?


# (1)
for line in code.lines
	print line
	
# (2)
for each word in code as w
	print w
	
# (3)
each line in code
	print my

# (4)
code => line => print

# (5)
print code.lines.each
print code.words.each
print code.characters.each

# (6)
print each line from code where line.startsWith("")
print each word from code
print each character from code

pattern
	search
		{Function}(each {IteratorType} from {Expression 1} where {Expression 2})
	replace
		for x in {Expression 1}.{IteratorType}s
			if {Expression 2}
				{Function}(x)



# Generators
String
	# Using yield
	generator
		lines
			pos = 0
			for i = 0 until my.length
				if my.data[i] == '\n'
					yield String(my.data, pos, i)
					pos = i
	
	find chars, from
		
	# Using traditional iterator styles
	iterate
		line
			pos = my.find("\n", iterator.pos)
			if not pos
				iterator.stop()
			iterator.pos = pos + 1
			return line
			
		word
			
