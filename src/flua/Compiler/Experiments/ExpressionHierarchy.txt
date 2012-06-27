
# (1)
sum x, y, z
	return +(x, y, z)


# (2)
sum x, y, z
	+
		x
		y
		z

# (3)
sum x, y, z
	return
		+
			x
			y
			z

# -------------------------------------------------------------
isSomething x
	or
		isVarChar(x)
		and
			x >= 0
			x <= 26

isSomething x
	return or(isVarChar(x), and(x >= 0, x <= 26, x % 2 == 0))