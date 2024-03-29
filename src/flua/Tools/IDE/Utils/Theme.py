from PyQt4 import QtGui, QtCore

def cf(color, style='', background=''):
	"""Return a QTextCharFormat with the given attributes.
	"""
	_color = QtGui.QColor()
	_color.setNamedColor(color)
	
	_format = QtGui.QTextCharFormat()
	_format.setForeground(_color)
	
	if background:
		_bg = QtGui.QColor()
		_bg.setNamedColor(background)
		_format.setBackground(_bg)
	
	if 'bold' in style:
		_format.setFontWeight(QtGui.QFont.Bold)
	if 'italic' in style:
		_format.setFontItalic(True)
	if 'underline' in style:
		_format.setFontUnderline(True)
	
	return _format
