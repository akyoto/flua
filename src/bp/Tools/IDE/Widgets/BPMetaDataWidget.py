from PyQt4 import QtGui, QtCore
from bp.Compiler.Utils import *

functionMetaData = [
	# Name : [Label, DataType, DefaultValue, ReadOnly, ToolTip]
	("force-parallelization",    ["Force parallelization:", "Bool", "false", False, "<p>Forces the compiler to parallelize the function ignoring whether it actually enhances the performance or not. <strong>Note: You should only check this if you know what you are doing, otherwise this can cause heavy side-effects.</strong></p>"]),
	("force-inlining",           ["Force inlining:", "Bool", "false", False, "", "<p>Forces the compiler to use inlining for this function. Note that compilers for C++ targets already do a good job in selecting what should be inlined.</p>"]),
	("force-implementation",     ["Force inclusion in output:", "Bool", "false", False, "<p>Forces this function to be included in the target code ignoring whether it is actually used or not. This can be used to ensure an extern source file for a specific target can include this function.</p>"]),
	("parallelization-threads",  ["Can run on X cores:", "SingleLine", "Unknown", True, "<p>This shows on how many cores this function could run in parallel.</p>"]),
	("last-modification-author", ["Last modification by:", "SingleLine", "", True, "<p>The person who modified this function last.</p>"]),
	("last-modification-date",   ["Last modification date:", "SingleLine", "", True, "<p>Date this function has been modified last.</p>"]),
	("last-runtime",             ["Last runtime:", "SingleLine", "Unknown", True, "<p>The <strong>average</strong> runtime of the last run.</p>"]),
	("average-runtime",          ["Average runtime:", "SingleLine", "Not executed yet", True, "<p>The <strong>average</strong> runtime of all runs.</p>"]),
	("estimated-runtime",        ["Estimated runtime:", "SingleLine", "Unknown", True, "<p>Estimated runtime for this function. This is used by the data dependency analyzer to determine whether it's worth parallelizing this function.</p>"]),
	("creation-date",            ["Creation date:", "SingleLine", "", True, "<p>The date this function has been created.</p>"]),
]

metaDataForNodeName = {
	"function" : functionMetaData,
	"setter" : functionMetaData,
	"getter" : functionMetaData,
	"operator" : functionMetaData,
	"cast-definition" : functionMetaData,
}

class BPMetaDataWidget(QtGui.QWidget):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.bpIDE = parent
		self.node = None
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
		
	def setNode(self, node, doc):
		self.node = node
		self.doc = doc
		
	def showEvent(self, event):
		self.updateView()
		event.accept()
		
	def updateView(self):
		# Clear all items
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
				widget = QtGui.QLineEdit(self)
			elif dataType == "Bool":
				widget = BPMetaCheckBox(self, metaNode, metaTag, defaultValue, self.doc)
			
			formLayout.setContentsMargins(3, 3, 3, 3)
			
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
	def setupMetaInfo(self, node, elemName, doc):
		self.node = node
		self.elemName = elemName
		self.doc = doc
		self.elemNode = getElementByTagName(self.node, self.elemName)
		
	def setValue(self, value):
		if not self.elemNode:
			self.elemNode = self.doc.createElement(self.elemName)
			self.node.appendChild(self.elemNode)
		
		if self.elemNode.childNodes:
			self.elemNode.firstChild.nodeValue = value
		else:
			self.elemNode.appendChild(self.doc.createTextNode(value))
		

class BPMetaCheckBox(QtGui.QCheckBox, BPMetaObject):
	
	def __init__(self, parent, node, elemName, defaultValue, doc):
		super().__init__(parent)
		self.bpIDE = parent.bpIDE
		self.setupMetaInfo(node, elemName, doc)
		if self.elemNode:
			self.setChecked(self.elemNode.firstChild.nodeValue == "true")
		elif defaultValue:
			self.setChecked(defaultValue == "true")
		self.stateChanged.connect(self.onStateChange)
		
	def onStateChange(self, state):
		if state:
			self.setValue("true")
		else:
			self.setValue("false")
			
		# Focus the editor again
		self.bpIDE.codeEdit.setFocus()
