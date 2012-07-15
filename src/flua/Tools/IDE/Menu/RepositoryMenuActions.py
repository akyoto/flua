from flua.Tools.IDE.Startup import *
from flua.Compiler import *
from PyQt4 import QtNetwork

# RepositoryDownloadThread
class RepositoryDownloadThread(QtCore.QThread, Benchmarkable):
	
	def __init__(self, bpIDE, repoName):
		super().__init__(bpIDE)
		Benchmarkable.__init__(self)
		
		self.bpIDE = bpIDE
		self.repoName = repoName
		self.finished.connect(self.bpIDE.onRepositoryDownloadFinished)
		
	def startWith(self):
		# To make the GUI more responsive
		q = QtCore.QEventLoop(self)
		self.finished.connect(q.quit)
		
		if self.bpIDE.threaded:
			self.start(QtCore.QThread.InheritPriority)
		else:
			self.run()
			self.finished.emit()
		
		# Execute event loop
		q.exec()
		
	def run(self):
		self.startBenchmark("Download %s via git" % self.repoName)
		
		try:
			#if self.logWidget:
			#	fhOut = self.logWidget.write
			#	fhErr = self.logWidget.writeError
			#else:
			fhOut = self.bpIDE.console.log.write#realStdout.write
			fhErr = self.bpIDE.console.log.writeError#realStderr.write
			
			gitCmd = [
				getGitPath() + "git",
				"clone",
				"git://github.com/%s.git" % self.repoName,
				getModuleDir() + self.repoName.split("/")[-1]
			]
			
			startProcess(gitCmd, fhOut, fhErr)
		except Exception as e:
			errorMessage = str(e)
			print(errorMessage)
		finally:
			self.endBenchmark()

# RepositoryMenuActions
class RepositoryMenuActions:
	
	def showRepositoryList(self):
		self.repoDialog, existed = self.getUIFromCache("repositories")
		
		if not existed:
			self.repoDialog.setStyleSheet(self.config.dialogStyleSheet)
			self.repoDialog.repositoryList.setObjectName("RepositoryList")
			
			self.repoDialog.search.textChanged.connect(self.filterRepositories)
			self.repoDialog.repositoryList.currentItemChanged.connect(self.onRepositoryChange)
			
			self.repoDialog.downloadButton.setEnabled(False)
			self.repoDialog.downloadButton.clicked.connect(self.downloadRepository)
		
		self.filterRepositories("")
		self.repoDialog.exec()
		
	def downloadRepository(self):
		item = self.repoDialog.repositoryList.currentItem()
		if not item:
			return
		
		repoName = item.text()
		
		if repoName == "blitzprog/flua":
			return
		
		self.console.activate("Log")
		self.consoleDock.show()
		
		print("Downloading repository: " + repoName)
		thread = RepositoryDownloadThread(self, repoName)
		thread.startWith()
		
	def onRepositoryDownloadFinished(self):
		self.moduleView.reloadModuleDirectory()
		self.filterRepositories(self.repoDialog.search.text())
		print("Finished!")
		
	def onRepositoryChange(self, current, previous):
		if current:
			self.repoDialog.downloadButton.setEnabled(not self.isRepositoryDownloaded(current.text()))
		
	def isRepositoryDownloaded(self, name):
		repoName = name.split("/")[-1]
		return os.path.exists(getModuleDir() + repoName)
		
	def filterRepositories(self, text):
		repoWidget = self.repoDialog.repositoryList
		repoWidget.clear()
		
		for x in self.repos:
			if text in x:
				if self.isRepositoryDownloaded(x):
					newItem = QtGui.QListWidgetItem(self.activeRepositoryIcon, x)
				else:
					newItem = QtGui.QListWidgetItem(self.inactiveRepositoryIcon, x)
				
				repoWidget.addItem(newItem)
		
	def connectWithGitHub(self):
		self.notImplemented()
		
	#def downloadURL(self, url):
	#	self.networkMgr.finished.connect(self.onRepositoryDownloadFinished)
	#	self.networkMgr.get(QtNetwork.QNetworkRequest(QtCore.QUrl(url)))
		
	#def onRepositoryDownloadFinished(self, networkReply):
	#	print(networkReply.readAll())
