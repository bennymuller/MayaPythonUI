import maya.cmds as cmds
from SimplygonProcessingModule import SimplygonJob

MO_WINDOW_NAME = "SimplygonOutputManager"
class ManageOutputWindow:
	def __init__(self, jobs):
		self._jobs = jobs
		self._jobList = None
		self._currentContainer = None
		
	def createJobSelector(self, parentContainer):
		layout = cmds.rowLayout(parent= parentContainer,numberOfColumns=2, adjustableColumn=2)	
		cmds.text(l="Jobs:")
		self._jobList = cmds.optionMenu(parent= layout, cc=self.jobSelectionChanged)
		jobIndex = 0
		for job in self._jobs:
			cmds.menuItem(parent=self._jobList, label=job.name, data=jobIndex)
			jobIndex+=1

	def createLODListPanel(self, parentContainer):
		scrollLayout = cmds.scrollLayout(parent= parentContainer, childResizable = True, horizontalScrollBarThickness=16, verticalScrollBarThickness=16)
		self._lodAssetContainer = cmds.columnLayout(parent=scrollLayout, adjustableColumn=True, h=800)

	def createActionPanel(self, parentContainer):
		layout = cmds.columnLayout(parent= parentContainer, adjustableColumn=True)
		cmds.button(parent= layout, label = "Clean job", command = self.onCleanJob)	
		cmds.button(parent= layout, label = "Split LODs", command = self.onSplit)	
		cmds.button(parent= layout, label = "Make Layers", command = self.onLayers)	
		cmds.button(parent= layout, label = "Move Textures", command = self.onMoveTextures)	
		
	def showWindow(self):
		self.updateJobList()
		if cmds.window(MO_WINDOW_NAME, exists=True):
			cmds.deleteUI(MO_WINDOW_NAME)

		window = cmds.window(MO_WINDOW_NAME, title="Manage Output", iconName="DL", w=800, h=800)
		mainLayout = cmds.columnLayout(parent= window, adjustableColumn=True)
		self.createJobSelector(mainLayout)
 
		subLayout = cmds.rowLayout(parent= mainLayout, numberOfColumns=2, adjustableColumn=1)
		self.createLODListPanel(subLayout)

		self.createActionPanel(subLayout)
		#Force an update of the asset lists
		self.jobSelectionChanged(None)		
		cmds.showWindow(window)
		
	def addObjects(self, scrollList, objNames):
		for n in objNames:
			cmds.textScrollList(scrollList, e=True, append = n)
		
	def refresh(self):
		self.jobSelectionChanged(None)		

				
	def showLODAssets(self, lods):
		if self._currentContainer !=None:
			cmds.deleteUI(self._currentContainer)
		self._currentContainer = cmds.columnLayout(parent=self._lodAssetContainer)
		for lod in lods:
			layout = cmds.frameLayout(parent= self._currentContainer, l="LOD"+str(lod), collapsable=True, font = "boldLabelFont")
			listPanel = cmds.rowLayout(parent= layout, numberOfColumns=3, adjustableColumn1=True, adjustableColumn2=True, adjustableColumn3=True)
			self.addObjects(cmds.textScrollList(parent= listPanel), set(lods[lod].objectNames))
			self.addObjects(cmds.textScrollList(parent= listPanel), set(lods[lod].materialNames))
			self.addObjects(cmds.textScrollList(parent= listPanel), set(lods[lod].textureNames))

		
	def getSelectedJob(self):
		selectedItemIndex = cmds.optionMenu(self._jobList, query=True, select=True)-1
		menuItems = cmds.optionMenu(self._jobList, q=True, itemListLong=True)
		selectedJobIndex = 0
		if menuItems != None and (menuItems != [] or len(menuItems) < selectedItemIndex):
			selectedJobIndex = cmds.menuItem(menuItems[selectedItemIndex], query=True, data=True)
		else:
			return None
		return self._jobs[selectedJobIndex]
		

	def jobSelectionChanged(self, _):
		#Potentially dangerous if it removes the currently selected job
		self.updateJobList()
		job = self.getSelectedJob()
		if job != None:
			self.showLODAssets(job.getLODs())
		
	def onCleanJob(self, _):
		self.updateJobList()
		job = self.getSelectedJob()
		if job != None:
			job.pruneTexturesAndMaterials()
		#We need to update the list of assets as the job will change it.
		self.refresh()

	def onSplit(self, _):
		self.updateJobList()
		job = self.getSelectedJob()
		if job != None:
			job.splitLODs()

	def onLayers(self, _):
		self.updateJobList()
		job = self.getSelectedJob()
		if job != None:
			job.makeLayers()
		
	def onMoveTextures(self, _):
		self.updateJobList()
		job = self.getSelectedJob()
		directory = cmds.fileDialog2(fm=3, okc="Move To")[0]
		job.moveTextures(directory)

		
	def updateJobList(self):
		toRemove = []
		for job in self._jobs:
			job.removeInvalidAssets()
			if job.isEmpty():
				job.delete()
				toRemove.append(r)
		for r in toRemove:
			self._jobs.remove(r)
		
		if len(toRemove) > 0:
			try:
				menuItems = cmds.optionMenu(self._settingsFileListCtrl, q=True, itemListLong=True)
				if menuItems != None and menuItems != []:
					cmds.deleteUI(menuItems)
			except:
				pass
			jobIndex = 0
			for job in self._jobs:
				cmds.menuItem(parent=self._jobList, label=job.name, data=jobIndex)
				jobIndex+=1
		
			
