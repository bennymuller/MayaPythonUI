import maya.cmds as cmds
import simplygonpanel
reload(simplygonpanel)
from simplygonpanel import SimplygonPanel

CTRL_VIEWCONTAINER = "ViewContainer"
CTRL_JOBLIST = "JobList"
CTRL_LODASSETS = "LODAssetContainer"
MO_WINDOW_NAME = "SimplygonOutputManager"
"""
Window that allows the user to manage the output from jobs.
"""
class ManageOutputWindow(SimplygonPanel):
	def __init__(self, batchProcessor):
		SimplygonPanel.__init__(self, "ManageOutput", batchProcessor)
		self.defineControl(CTRL_VIEWCONTAINER, "Container")
		self.defineControl(CTRL_LODASSETS, "Container")
		self.defineControl(CTRL_JOBLIST, "OptionMenu")
		self._currentContainer = None
	
	"""
	Create the job selection panel.
	@param parentContainer: the container to add the components to
	"""
	def createJobSelector(self, parentContainer):
		layout = cmds.rowLayout(parent= parentContainer,numberOfColumns=2, adjustableColumn=2)	
		cmds.text(l="Jobs:")
		jobList = cmds.optionMenu(parent= layout, cc=self.jobSelectionChanged)
		self.setMObj(CTRL_JOBLIST, jobList)
		jobIndex = 0
		for job in self._batchProcessor.jobs:
			cmds.menuItem(parent=jobList, label=job.name, data=jobIndex)
			jobIndex+=1

	"""
	Creates the panel where all the lod assets will be listed.
	@param parentContainer: the container to add the panel to
	"""
	def createLODListPanel(self, parentContainer):
		scrollLayout = cmds.scrollLayout(parent= parentContainer, childResizable = True, horizontalScrollBarThickness=16, verticalScrollBarThickness=16)
		self.setMObj(CTRL_LODASSETS, cmds.columnLayout(parent=scrollLayout, adjustableColumn=True, h=800))

	"""
	Creates the panel with all the user action buttons.
	@param parentContainer: the container to add the components to
	"""	
	def createActionPanel(self, parentContainer):
		layout = cmds.columnLayout(parent= parentContainer, adjustableColumn=True)
		cmds.button(parent= layout, label = "Clean job", command = self.onCleanJob)	
		cmds.button(parent= layout, label = "Split LODs", command = self.onSplit)	
		cmds.button(parent= layout, label = "Make Layers", command = self.onLayers)	
		cmds.button(parent= layout, label = "Move Textures", command = self.onMoveTextures)	
		
	"""
	Shows the manage output window
	"""
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
		
	"""
	Adds the list of objects to the scroll list
	@param scrollList: UI list to add the object names to
	@param objNames: list of object names to add to the scroll list
	"""
	def addObjects(self, scrollList, objNames):
		for n in objNames:
			cmds.textScrollList(scrollList, e=True, append = n)
		
	"""
	Upates the interface
	"""
	def refresh(self):
		self.jobSelectionChanged(None)		

				
	"""
	Adds the assets that exists in the list of lods to the UI.
	@param lods: list of assets to show
	"""
	def showLODAssets(self, lods):
		if self.getMObj(CTRL_VIEWCONTAINER) !=None:
			cmds.deleteUI(self.getMObj(CTRL_VIEWCONTAINER))
		container = cmds.columnLayout(parent=self.getMObj(CTRL_LODASSETS))
		self.setMObj(CTRL_VIEWCONTAINER,container)
		for lod in lods:
			layout = cmds.frameLayout(parent= container, l="LOD"+str(lod), collapsable=True, font = "boldLabelFont")
			listPanel = cmds.rowLayout(parent= layout, numberOfColumns=3, adjustableColumn1=True, adjustableColumn2=True, adjustableColumn3=True)
			self.addObjects(cmds.textScrollList(parent= listPanel), set(lods[lod].objectNames))
			self.addObjects(cmds.textScrollList(parent= listPanel), set(lods[lod].materialNames))
			self.addObjects(cmds.textScrollList(parent= listPanel), set(lods[lod].textureNames))

	"""
	Returns the currently selected job
	"""	
	def getSelectedJob(self):
		selectedItemIndex = cmds.optionMenu(self.getMObj(CTRL_JOBLIST), query=True, select=True)-1
		menuItems = cmds.optionMenu(self.getMObj(CTRL_JOBLIST), q=True, itemListLong=True)
		selectedJobIndex = 0
		if menuItems != None and (menuItems != [] or len(menuItems) < selectedItemIndex):
			selectedJobIndex = cmds.menuItem(menuItems[selectedItemIndex], query=True, data=True)
		else:
			return None
		return self._batchProcessor.jobs[selectedJobIndex]
		
	"""
	Called whenever the job selection has changed
	"""
	def jobSelectionChanged(self, _):
		#Potentially dangerous if it removes the currently selected job
		self.updateJobList()
		job = self.getSelectedJob()
		if job != None:
			self.showLODAssets(job.getLODs())
	
	"""
	Called when the user invokes the job cleaning
	"""
	def onCleanJob(self, _):
		self.updateJobList()
		job = self.getSelectedJob()
		if job != None:
			job.pruneTexturesAndMaterials()
		#We need to update the list of assets as the job will change it.
		self.refresh()

	"""
	Called when the user invokes splitting the lods
	"""
	def onSplit(self, _):
		self.updateJobList()
		job = self.getSelectedJob()
		if job != None:
			job.splitLODs()

	"""
	Called when the user invokes making layers
	"""
	def onLayers(self, _):
		self.updateJobList()
		job = self.getSelectedJob()
		if job != None:
			job.makeLayers()

	"""
	Called when the user invokes the action of moving assets
	"""	
	def onMoveTextures(self, _):
		self.updateJobList()
		job = self.getSelectedJob()
		directory = cmds.fileDialog2(fm=3, okc="Move To")[0]
		job.moveTextures(directory)


	"""
	Loops through all jobs and cleans the up.
	"""
	def updateJobList(self):
		toRemove = []
		for job in self._batchProcessor.jobs:
			job.removeInvalidAssets()
				
			
