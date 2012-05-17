from PyQt4 import QtGui, QtCore
from bp.Compiler.Utils import *

refTransparencyToolTip = "<p>Shows whether this extern function is referentially transparent or not. <strong>A function is referentially transparent if it can be replaced with its return value without changing the behaviour of the program. It should return the same output for the same input and not cause any side effects.</strong></p>"

functionMetaData = [
	# Name : [Label, DataType, DefaultValue, ReadOnly, ToolTip]
	("force-parallelization",     ["Force parallelization:", "Bool", "false", False, "<p>Forces the compiler to parallelize the function ignoring whether it actually enhances the performance or not. <strong>Note: You should only check this if you know what you are doing, otherwise this can cause heavy side-effects.</strong></p>"]),
	("force-inlining",            ["Force inlining:", "Bool", "false", False, "", "<p>Forces the compiler to use inlining for this function. Note that compilers for C++ targets already do a good job in selecting what should be inlined.</p>"]),
	("force-implementation",      ["Force inclusion in output:", "Bool", "false", False, "<p>Forces this function to be included in the target code ignoring whether it is actually used or not. This can be used to ensure an extern source file for a specific target can include this function.</p>"]),
	("create-cache",              ["Create a cache:", "Bool", "false", False, "<p>Specifies whether the compiler should automatically create a cache for the results of this function. <strong>This is only possible for referentially transparent functions.</strong></p>"]),
	("referentially-transparent", ["Referentially transparent:", "SingleLine", "Unknown", True, refTransparencyToolTip]),
	("parallelization-threads",   ["Can run on X cores:", "SingleLine", "Unknown", True, "<p>This shows on how many cores this function could run in parallel.</p>"]),
	("last-modification-author",  ["Last modification by:", "SingleLine", "", True, "<p>The person who modified this function last.</p>"]),
	("last-modification-date",    ["Last modification date:", "SingleLine", "", True, "<p>Date this function has been modified last.</p>"]),
	("number-of-calls",           ["Number of calls:", "SingleLine", "Unknown", True, "<p>Shows how many times this function was called in the last run.</p>"]),
	("average-runtime",           ["Average runtime:", "SingleLine", "Unknown", True, "<p>The <strong>average</strong> runtime of the last run.</p>"]),
	("estimated-runtime",         ["Estimated runtime:", "SingleLine", "Unknown", True, "<p>Estimated runtime for this function. This is used by the data dependency analyzer to determine whether it's worth parallelizing this function.</p>"]),
	("creation-date",             ["Creation date:", "SingleLine", "", True, "<p>The date this function has been created.</p>"]),
]

metaDataForNodeName = {
	"function" : functionMetaData,
	"setter" : functionMetaData,
	"getter" : functionMetaData,
	"operator" : functionMetaData,
	"cast-definition" : functionMetaData,
	
	"extern-function" : [
		("same-output-for-input",     ["Same output for a given input:", "Bool", False, False, "<p>Sets the flag whether this extern function always returns the same output for a given input.</p>"]),
		("no-side-effects",           ["No significant side effects:", "Bool", False, False, "<p>Sets the flag whether this extern function causes no side effects on the program when called multiple times in parallel. <strong>Ask yourself: Can this function be executed safely by 100 threads at the same time or would it have side effects?</strong> Unlike referential transparency the output is allowed to always be different for a given input.</p>"]),
		("referentially-transparent", ["Referentially transparent:", "SingleLine", False, True, refTransparencyToolTip]),
	],
	
	"class" : [
		("ensure-destructor-call",     ["Ensure destructor is called:", "Bool", False, False, "<p>A <strong>hint</strong> to the garbage collector that this function absolutely needs to call its destructor when the object is being destroyed. This might have a tiny impact on the performance of the garbage collector. It is better to not enable this unless you absolutely need to make sure the destructor is called.</p>"]),
	]
}

class BPMetaDataWidget(QtGui.QWidget):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.bpIDE = parent
		self.node = None
		self.viewOnNode = None
		self.widgetByMetaTag = None
		self.lastLineIndex = -2
		self.stackedLayout = QtGui.QStackedLayout()
		self.setLayout(self.stackedLayout)
		
		#self.setContentsMargins(0, 0, 0, 0)
		#self.stackedLayout.setContentsMargins(0, 0, 0, 0)
		
		self.setMinimumWidth(250)
		self.setStyleSheet(self.bpIDE.config.dialogStyleSheet)
		
	def clear(self):
		while self.stackedLayout.count():
			widget = self.stackedLayout.itemAt(0).widget()
			widget.close()
			self.stackedLayout.removeWidget(widget)
		self.viewOnNode = None
		
	def setNode(self, node, doc):
		self.node = node
		self.doc = doc
		
	def showEvent(self, event):
		self.updateView()
		event.accept()
		
	def updateView(self):
		# Are we still in the same line?
		if self.bpIDE.codeEdit and self.bpIDE.codeEdit.getLineIndex() == self.lastLineIndex:
			return
		self.lastLineIndex = self.bpIDE.codeEdit.getLineIndex()
		
		# Avoid doing unnecessary stuff
		if self.viewOnNode is None:
			# Widget is currently showing nothing
			if self.node is None:
				return
			elif not self.node.tagName in metaDataForNodeName:
				return
		else:
			# Widget is currently showing some items
			if (self.node and self.node.isSameNode(self.viewOnNode)):
				return
		
		# Clear all current form items
		self.clear()
		
		# Valid node?
		if not self.node or self.node.nodeType == Node.TEXT_NODE:
			return
		
		# Is there any meta data options available for this node?
		nodeName = self.node.tagName
		if not nodeName in metaDataForNodeName:
			return
		
		# Set up the values from this node if there are any
		metaNode = getElementByTagName(self.node, "meta")
		if not metaNode:
			metaNode = self.doc.createElement("meta")
			self.node.appendChild(metaNode)
		
		# New form layout
		formWidget = QtGui.QWidget(self)
		formLayout = QtGui.QFormLayout(formWidget)
		formLayout.setContentsMargins(3, 3, 3, 3)
		self.widgetByMetaTag = dict()
		
		# Build the form
		for metaTag, metaInfo in metaDataForNodeName[nodeName]:
			labelName = metaInfo[0]
			dataType = metaInfo[1]
			defaultValue = metaInfo[2]
			readOnly = metaInfo[3]
			statusTip = metaInfo[4]
			
			# Label
			label = QtGui.QLabel(labelName)
			
			# Widget
			widget = None
			if dataType == "SingleLine":
				widget = BPMetaLineEdit(self, metaNode, metaTag, defaultValue, self.doc)
				if defaultValue:
					widget.setText(defaultValue)
			elif dataType == "Bool":
				widget = BPMetaCheckBox(self, metaNode, metaTag, defaultValue, self.doc)
				if defaultValue == "true":
					widget.setChecked("true")
				widget.stateChanged.connect(widget.onStateChange)
			
			self.widgetByMetaTag[metaTag] = widget
			
			# Readonly
			if readOnly:
				widget.setReadOnly(True)
			
			if statusTip:
				label.setToolTip(statusTip)
				label.setWhatsThis(statusTip)
				widget.setToolTip(statusTip)
				widget.setWhatsThis(statusTip)
			
			# Add to layout
			formLayout.addRow(label, widget)
		
		# Replace with current layout
		self.stackedLayout.addWidget(formWidget)
		
		# Save
		self.viewOnNode = self.node
	
class BPMetaObject:
	def setupMetaInfo(self, bpIDE, node, elemName, doc):
		self.node = node
		self.elemName = elemName
		self.doc = doc
		self.elemNode = getElementByTagName(self.node, self.elemName)
		self.bpIDE = bpIDE
		
	def focusEditor(self):
		if self.bpIDE.codeEdit:
			self.bpIDE.codeEdit.setFocus()
		
	def setValue(self, value):
		if not self.elemNode:
			self.elemNode = self.doc.createElement(self.elemName)
			self.node.appendChild(self.elemNode)
		
		if self.elemNode.childNodes:
			self.elemNode.firstChild.nodeValue = value
		else:
			self.elemNode.appendChild(self.doc.createTextNode(value))
		
		# Modification state
		if self.bpIDE.codeEdit:
			self.bpIDE.codeEdit.qdoc.setModified(True)
			self.bpIDE.codeEdit.rehighlightCurrentLine()

class BPMetaLineEdit(QtGui.QLineEdit, BPMetaObject):
	
	def __init__(self, parent, node, elemName, defaultValue, doc):
		super().__init__(parent)
		self.metaDataWidget = parent
		self.bpIDE = parent.bpIDE
		self.setupMetaInfo(self.bpIDE, node, elemName, doc)
		
		if self.node.parentNode.tagName == "extern-function" and self.elemName == "referentially-transparent":
			sideEffects = self.metaDataWidget.widgetByMetaTag["no-side-effects"]
			sameOutput = self.metaDataWidget.widgetByMetaTag["same-output-for-input"]
			if sideEffects.isChecked() and sameOutput.isChecked():
				self.setText("Yes")
			else:
				self.setText("No")
		else:
			if self.elemNode:
				self.setText(self.elemNode.firstChild.nodeValue)
			elif defaultValue:
				self.setText(defaultValue)

class BPMetaCheckBox(QtGui.QCheckBox, BPMetaObject):
	
	def __init__(self, parent, node, elemName, defaultValue, doc):
		super().__init__(parent)
		self.metaDataWidget = parent
		self.bpIDE = parent.bpIDE
		self.setupMetaInfo(self.bpIDE, node, elemName, doc)
		if self.elemNode:
			self.setChecked(self.elemNode.firstChild.nodeValue == "true")
		elif defaultValue:
			self.setChecked(defaultValue == "true")
		
	def nextCheckState(self):
		if (not self.isChecked()):
			# Checking the box
			if self.elemName == "create-cache":
				if not getMetaDataBool(self.elemNode, "referentially-transparent"):
					self.bpIDE.notify("You can only create a cache for referentially transparent functions.")
					self.focusEditor()
					return
			# elif self.elemName == "referentially-transparent":
				# # Referential transparency means the other 2 boxes need to be checked
				# sideEffects = self.metaDataWidget.widgetByMetaTag["no-side-effects"]
				# if not sideEffects.isChecked():
					# sideEffects.setChecked(True)
					
				# sameOutput = self.metaDataWidget.widgetByMetaTag["same-output-for-input"]
				# if not sameOutput.isChecked():
					# sameOutput.setChecked(True)
		else:
			# Unchecking the box
			if self.elemName == "no-side-effects":
				refTransparent = self.metaDataWidget.widgetByMetaTag["referentially-transparent"]
				refTransparent.setText("No")
			elif self.elemName == "same-output-for-input":
				refTransparent = self.metaDataWidget.widgetByMetaTag["referentially-transparent"]
				refTransparent.setText("No")
		
		state = not self.isChecked()
		self.setChecked(state)
		self.onStateChange(state)
		
		# Update referential transparency
		if self.elemName == "same-output-for-input" or self.elemName == "no-side-effects":
			sideEffects = self.metaDataWidget.widgetByMetaTag["no-side-effects"]
			sameOutput = self.metaDataWidget.widgetByMetaTag["same-output-for-input"]
			
			if sideEffects.isChecked() and sameOutput.isChecked():
				refTransparent = self.metaDataWidget.widgetByMetaTag["referentially-transparent"]
				refTransparent.setText("Yes")
		
		# Focus the editor again
		self.focusEditor()
		
	def onStateChange(self, state):
		if state:
			self.setValue("true")
		else:
			self.setValue("false")
			
		# Focus the editor again
		self.focusEditor()
