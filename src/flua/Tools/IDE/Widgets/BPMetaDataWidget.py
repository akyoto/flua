from PyQt4 import QtGui, QtCore
from flua.Compiler.Utils import *

refTransparencyToolTip = "<p>Shows whether this extern function is referentially transparent or not. <strong>A function is referentially transparent if it can be replaced with its return value without changing the behaviour of the program. It should return the same output for the same input and not cause any side effects.</strong></p>"
threadSafeToolTip = "<p>Shows whether this function can be safely called from multiple threads at the same time.</p>"
forceImplementation = ("force-implementation",      ["Force inclusion in output:", "Bool", "false", False, "<p>Forces this class or function to be included in the target code ignoring whether it is actually used or not. This can be used to ensure an extern source file for a specific target can use it in its source code.</p>"])
forcePara = ("force-parallelization",     ["Force parallelization:", "Bool", "false", False, "<p>Forces the compiler to parallelize the function / loop ignoring whether it actually enhances the performance or not. <strong>Note: You should only check this if you know what you are doing, otherwise this can cause heavy side-effects.</strong></p>"])

functionMetaData = [
	# Name : [Label, DataType, DefaultValue, ReadOnly, ToolTip]
	forcePara,
	("force-inlining",            ["Force inlining:", "Bool", "false", False, "", "<p>Forces the compiler to use inlining for this function. Note that compilers for C++ targets already do a good job in selecting what should be inlined.</p>"]),
	forceImplementation,
	("create-cache",              ["Create a cache:", "Bool", "false", False, "<p>Specifies whether the compiler should automatically create a cache for the results of this function. <strong>This is only possible for referentially transparent functions.</strong></p>"]),
	("endless-recursion-check",   ["Check for endless recursion:", "Bool", "false", False, "<p>Specifies whether the compiler should create a check for endless recursion and throw InfiniteRecursionException when it happens (has a little impact on the performance).</p>"]),
	("referentially-transparent", ["Referentially transparent:", "SingleLine", "Unknown", True, refTransparencyToolTip]),
	("thread-safe",               ["Thread safe:", "SingleLine", "Unknown", True, threadSafeToolTip]),
	("parallelization-threads",   ["Can run on X cores:", "SingleLine", "Unknown", True, "<p>This shows on how many cores this function could run in parallel.</p>"]),
	#("number-of-calls",           ["Number of calls:", "SingleLine", "Unknown", True, "<p>Shows how many times this function was called in the last run.</p>"]),
	#("average-runtime",           ["Average runtime:", "SingleLine", "Unknown", True, "<p>The <strong>average</strong> runtime of the last run.</p>"]),
	("estimated-runtime",         ["Estimated runtime:", "SingleLine", "Unknown", True, "<p>Estimated runtime for this function. This is used by the data dependency analyzer to determine whether it's worth parallelizing this function.</p>"]),
	("last-modification-author",  ["Last modification by:", "SingleLine", "", True, "<p>The person who modified this function last.</p>"]),
	("last-modification-date",    ["Last modification date:", "SingleLine", "", True, "<p>Date this function has been modified last.</p>"]),
	("creation-date",             ["Creation date:", "SingleLine", "", True, "<p>The date this function has been created.</p>"]),
]

metaDataForNodeName = {
	"function" : functionMetaData,
	"setter" : functionMetaData,
	"getter" : functionMetaData,
	"operator" : functionMetaData,
	"cast-definition" : functionMetaData,
	
	"extern-function" : [
		("no-side-effects",           ["No side effects:", "Bool", "false", False, "<p>Sets the flag whether this extern function causes no side effects on the program when called multiple times in parallel. <strong>Ask yourself: Can this function be executed safely by 100 threads at the same time or would it have side effects?</strong> Unlike referential transparency the output is allowed to always be different for a given input.</p>"]),
		("same-output-for-input",     ["Same output for a given input:", "Bool", "false", False, "<p>Sets the flag whether this extern function always returns the same output for a given input.</p>"]),
		("thread-safe",               ["Thread safe:", "SingleLine", "Unknown", True, threadSafeToolTip]),
		("referentially-transparent", ["Referentially transparent:", "SingleLine", "false", True, refTransparencyToolTip]),
	],
	
	"class" : [
		("ensure-destructor-call",     ["Ensure finalizer is called:", "Bool", "false", False, "<p>A <strong>hint</strong> to the garbage collector that objects of this class absolutely need to call the 'finalize' method (destructor) when the object is being destroyed. This might have a tiny impact on the performance of the garbage collector. It is better to not enable this unless you absolutely need to make sure the destructor is called.</p>"]),
		forceImplementation,
		("default-class-version",      ["Use this class by default:", "Bool", "false", False, "<p>Use this version of the class as the default one.</p>"]),
	],
	
	"for" : [
		forcePara,
	],
	
	#"parallel" : [
	#	("wait-for-all-threads",     ["Wait for all calls / threads to finish:", "Bool", "true", False, "<p>Activate this if you need all parallel calls to finish their work before continuing the program flow.</p>"]),
	#]
}

metaDataTitleForNodeName = {
	"function" : "Function",
	"setter" : "Setter",
	"getter" : "Getter",
	"operator" : "Operator",
	"cast-definition" : "Cast",
	"extern-function" : "Extern function",
	"class" : "Class",
	"for" : "For loop",
	"parallel" : "Parallel block",
}

class BPMetaDataWidget(QtGui.QWidget):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.bpIDE = parent
		self.node = None
		self.viewOnNode = None
		self.viewOnCE = None
		self.widgetByMetaTag = None
		self.lastLineIndex = -2
		self.autoHide = False
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
		# Only check for return if we are in the same CE
		if self.viewOnCE == self.bpIDE.codeEdit:
			# Are we still in the same line?
			if self.bpIDE.codeEdit and self.bpIDE.codeEdit.getLineIndex() == self.lastLineIndex:
				return
			
			# Avoid doing unnecessary stuff
			if self.viewOnNode is None:
				# Widget is currently showing nothing
				if self.node is None:
					return
				elif ((self.node.nodeType != Node.ELEMENT_NODE) or not self.node.tagName in metaDataForNodeName) and self.node.parentNode.parentNode.nodeType == Node.ELEMENT_NODE and (not self.node.parentNode.parentNode.tagName in metaDataForNodeName):
					return
			else:
				# Widget is currently showing some items
				if (self.node and self.node.isSameNode(self.viewOnNode)) or (self.node and self.node.parentNode and self.node.parentNode.parentNode.isSameNode(self.viewOnNode)):
					if (self.node.nodeType != Node.ELEMENT_NODE) or not (self.node.tagName in metaDataForNodeName and self.node.parentNode.parentNode.tagName in metaDataForNodeName):
						return
		
		if self.bpIDE.codeEdit:
			self.lastLineIndex = self.bpIDE.codeEdit.getLineIndex()
		
		# Clear all current form items
		self.clear()
		self.viewOnNode = None
		self.viewOnCE = self.bpIDE.codeEdit
		
		# Reset title
		if self.autoHide:
			self.bpIDE.metaDataViewDock.hide()
		self.bpIDE.metaDataViewDock.setWindowTitle("Meta data")
		
		# Valid node?
		if not self.node or self.node.nodeType == Node.TEXT_NODE:
			return
		
		# Is there any meta data options available for this or its parent node?
		nodeName = self.node.tagName
		
		if not nodeName in metaDataForNodeName:
			# Enable/Disable parent node check
			if 1:
				tmpNode = self.node.parentNode.parentNode
				nodeName = tmpNode.tagName
				
				if not nodeName in metaDataForNodeName:
					return
				
				self.node = tmpNode
			else:
				return
		
		# Save
		self.viewOnNode = self.node
		
		# Set up the values from this node if there are any
		metaNode = getElementByTagName(self.node, "meta")
		if not metaNode:
			metaNode = self.doc.createElement("meta")
			#print("Creating meta node for " + self.node.toxml() + " because it didn't exist yet.")
			self.node.appendChild(metaNode)
		
		# New form layout
		formWidget = QtGui.QWidget(self)
		formLayout = QtGui.QFormLayout(formWidget)
		formLayout.setContentsMargins(3, 3, 3, 3)
		self.widgetByMetaTag = dict()
		
		# Set dock name
		if self.autoHide:
			self.bpIDE.metaDataViewDock.show()
		self.bpIDE.metaDataViewDock.setWindowTitle("Meta data: %s" % metaDataTitleForNodeName[nodeName])
		
		# Build the form
		for metaTag, metaInfo in metaDataForNodeName[nodeName]:
			labelName = metaInfo[0]
			dataType = metaInfo[1]
			defaultValue = metaInfo[2]
			readOnly = metaInfo[3]
			statusTip = metaInfo[4]
			
			# Label
			label = QtGui.QLabel(labelName)
			
			# Hide this meta tag when it's not needed
			if metaTag == "default-class-version":
				fileName = stripAll(self.bpIDE.codeEdit.getFilePath())
				if self.bpIDE.codeEdit and fileName != "Mutable" and fileName != "Immutable":
					continue
			
			# Widget
			widget = None
			if dataType == "SingleLine":
				widget = BPMetaLineEdit(self, metaNode, metaTag, defaultValue, self.doc)
			elif dataType == "Bool":
				widget = BPMetaCheckBox(self, metaNode, metaTag, defaultValue, self.doc)
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
	
class BPMetaObject:
	def setupMetaInfo(self, metaDataWidget, node, elemName, doc):
		self.metaDataWidget = metaDataWidget
		self.bpIDE = metaDataWidget.bpIDE
		self.node = node
		self.elemName = elemName
		self.doc = doc
		self.elemNode = getElementByTagName(self.node, self.elemName)
		
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
			
	def metaDataIsChecked(self, tagName):
		return self.metaDataWidget.widgetByMetaTag[tagName].isChecked()

class BPMetaLineEdit(QtGui.QLineEdit, BPMetaObject):
	
	def __init__(self, parent, node, elemName, defaultValue, doc):
		super().__init__(parent)
		self.setupMetaInfo(parent, node, elemName, doc)
		
		if self.node.parentNode.tagName == "extern-function":
			if self.elemName == "referentially-transparent":
				if self.metaDataIsChecked("no-side-effects") and self.metaDataIsChecked("same-output-for-input"):
					self.setText("Yes")
				else:
					self.setText("No")
			elif self.elemName == "thread-safe":
				if self.metaDataIsChecked("no-side-effects"):
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
		self.setupMetaInfo(parent, node, elemName, doc)
		
		if self.elemNode:
			self.setChecked(self.elemNode.firstChild.nodeValue == "true")
		elif defaultValue:
			self.setChecked(defaultValue == "true")
		
	def nextCheckState(self):
		if (not self.isChecked()):
			# Checking the box
			if self.elemName == "create-cache":
				if not getMetaDataBool(self.elemNode, "referentially-transparent"):
					self.bpIDE.notify("You can only create a cache for referentially transparent functions which always produce the same output for a given input.")
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
				threadSafe = self.metaDataWidget.widgetByMetaTag["thread-safe"]
				threadSafe.setText("No")
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
			
			if self.metaDataIsChecked("no-side-effects"):
				self.metaDataWidget.widgetByMetaTag["thread-safe"].setText("Yes")
				if self.metaDataIsChecked("same-output-for-input"):
					self.metaDataWidget.widgetByMetaTag["referentially-transparent"].setText("Yes")
		
		# Focus the editor again
		self.focusEditor()
		
	def onStateChange(self, state):
		if state:
			self.setValue("true")
		else:
			self.setValue("false")
			
		# Focus the editor again
		self.focusEditor()
