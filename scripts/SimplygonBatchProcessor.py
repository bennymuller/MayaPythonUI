import maya.cmds as cmds
import inspect, os
import ManageOutputWindowModule
reload(ManageOutputWindowModule)
from ManageOutputWindowModule import *
import OptimizationManagerModule
reload(OptimizationManagerModule)
from OptimizationManagerModule import *
import SimplygonProcessingModule
reload(SimplygonProcessingModule)
from SimplygonProcessingModule import *
import OptimizationPanelModule
reload(OptimizationPanelModule)
from OptimizationPanelModule import OptimizationPanel

__author__ = "Samuel Rantaeskola"
__copyright__ = "Copyright 2014, Donya Labs AB"
__credits__ = ["Samuel Rantaeskola"]
__license__ = "ALv2"
__version__ = "0.2"
__maintainer__ = "Samuel Rantaeskola"
__email__ = "samuel@simplygon.com"
__status__ = "Prototype"

SETTINGS_FILE_SETTING = "SimplygonSettingsFileXML"
TEMP_SETTING_FILE = "__temp_processing.ini"
SIMPLYGON_LOGO = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))+"/simplygon_logo.png" #Replace this line to point out your logo


class BrowsingPanel:
	def __init__(self, batchProcessor):
		self._batchProcessor = batchProcessor
		self._settingsDirCtrl = None
		self._settingsFileListCtrl = None
		self._browseButton = None
		self._settingsXML = ""

	"""
	Opens up a browser window that allows the user to specify where you can find the XML that describes the setting files to use
	"""	
	def onBrowse(self, _):
		self._settingsXML = cmds.fileDialog2(fm=1, fileFilter="XML Files (*.xml)", okc="Set")[0]
		cmds.textField(self._settingsDirCtrl, edit=True, text=self._settingsXML)
		# Set up a new settings manager with the new XML.
		self._settingsManager = OptimizationSettingsManager(self._settingsXML)
		self._batchProcessor.settingFileChanged(self._settingsXML)		

	"""
	Creates the panel containing the browsing component for the setting file xml and adds it to the main layout.
	@param parentContainer: the container to add the panel to
	"""		
	def createPanel(self, parentContainer):
		layout = cmds.rowLayout (parent= parentContainer, numberOfColumns = 2)
		self._settingsDirCtrl = cmds.textField(parent= layout, ed=False, w=400, text=self._settingsXML)
		cmds.button(parent= layout, label = "Browse", command = self.onBrowse)	

	def setSettingsXML(self, settingsXML):
		self._settingsXML = settingsXML
		
	"""
	Enables/disables browsing panel
	@param enabled: true to enable all the components.
	"""
	def enable(self, enabled):
		#Only enable the color set selector if user weights are enabled
		cmds.textField(self._settingsDirCtrl, edit=True, en=enabled)
		cmds.button(self._browseButton, edit=True, en=enabled)

		
TEXTURE_DESTINATION_SETTING="SimplygonTextureDestination"		
JOB_AUTO_CLEAN="SimplygonJobAutoClean"		
class JobPanel:
	def __init__(self, batchProcessor):
		self._batchProcessor = batchProcessor
		self._jobs = []
				
	def createPanel(self, parentContainer):
		layout = cmds.frameLayout(parent= parentContainer, l="Jobs", collapsable=False)
		autoClean = False
		if cmds.optionVar(exists= JOB_AUTO_CLEAN):
			print cmds.optionVar(q=JOB_AUTO_CLEAN)
			autoClean = cmds.optionVar(q=JOB_AUTO_CLEAN) == "True"
		self._autoCleanUp = cmds.checkBox(l="Auto Clean Up Jobs", value=autoClean, w=150, parent= layout, onc=self.onAutoClean, ofc=self.onAutoClean)

		browseLayout = cmds.rowLayout (parent= layout, numberOfColumns = 3)
		# Fetch the texture destination folder from the environment.
		textureDestination = ""		
		if cmds.optionVar(exists= TEXTURE_DESTINATION_SETTING):
			textureDestination = cmds.optionVar(q=TEXTURE_DESTINATION_SETTING)
		
		cmds.text(parent= browseLayout, label = "Texture destination:")		
		self._textureDestinationDir = cmds.textField(parent= browseLayout, ed=False, w=400, text=textureDestination)
		cmds.button(parent= browseLayout, label = "Browse", command = self.onBrowse)		
		cmds.button(parent= layout, label = "Manage Output", command = self.onManageOutput)	
	
	def addJob(self, job):
		self._jobs.append(job)
		if cmds.checkBox(self._autoCleanUp, query = True, value=True):
			job.pruneTexturesAndMaterials()
			job.makeLayers()
			directory = cmds.textField(self._textureDestinationDir, query=True, text=True)
			job.moveTextures(directory)		
		
	def onManageOutput(self, job):
		window = ManageOutputWindow(self._jobs)
		window.showWindow()
	"""
	"""	
	def onBrowse(self, _):
		textureDestination = cmds.fileDialog2(fm=3, okc="Set")[0]
		if textureDestination != None:
			cmds.textField(self._textureDestinationDir, edit=True, text=textureDestination)
			cmds.optionVar( sv=(TEXTURE_DESTINATION_SETTING, textureDestination) )

	def onAutoClean(self, _):
		cmds.optionVar( sv=(JOB_AUTO_CLEAN, cmds.checkBox(self._autoCleanUp, query = True, value=True)))
		
	"""
	Enable/disable the controls in the window
	@param enabled: true if the controls should be enabled.
	"""	
	def enable(self, enabled):
		pass

		
"""
The main class for the Simplygon Batch processor. Handles a dock window and setting up all the components.
"""		
class SimplygonBatchProcessor:
	def __init__(self):		
		self.simplygonProcessor = SimplygonProcessor()
		self._browsingPanel = BrowsingPanel(self)
		self._jobPanel = JobPanel(self)
		self._optimizationPanel = OptimizationPanel(self)
		self._settingsManager = None
		self._settingsXML = None
		# Fetch the settings file folder from the environment.
		if cmds.optionVar(exists= SETTINGS_FILE_SETTING):
			self._settingsXML = cmds.optionVar(q=SETTINGS_FILE_SETTING)
			self._settingsManager = OptimizationSettingsManager(self._settingsXML)
			self._browsingPanel.setSettingsXML(self._settingsXML)
		
	"""
	Starts a new Simplygon process. Will generate a temporary settings file to use during this optimization.
	@param batch: true if the process should be run in batch mode
	"""	
	def startSimplygon(self, batch):
		tempPath = os.path.dirname(os.path.realpath(self._settingsXML))
		tempFile = tempPath+"/"+TEMP_SETTING_FILE
		tempFile = tempFile.replace("\\", "/")
		# Write out a temporary settings file with the overriden settings included
		with open(tempFile, 'wb') as outFile:
			self._settingsManager.writeTempConfig(outFile)


		directives = ProcessDirectives()
		directives.settingFile = tempFile
		directives.batchMode = batch
		directives.useWeights = self._optimizationPanel.useUserWeights
		directives.colorSet = self._optimizationPanel.colorSet
		directives.weightMultiplier = self._optimizationPanel.weightMultiplier
		job = self.simplygonProcessor.process(directives)
		self._jobPanel.addJob(job)
		#Remove the temporary processing file
		os.remove(tempFile)
		
	def settingFileChanged(self, settingsXML):
		self._settingsXML = settingsXML
		cmds.optionVar( sv=(SETTINGS_FILE_SETTING, self._settingsXML) )
		if self._settingsManager != None:
			self._settingsManager.clear()
		self._settingsManager = OptimizationSettingsManager(self._settingsXML)
		self._optimizationPanel.setSettingsManager(self._settingsManager)
	
	def settingChanged(self):
		self.enable(somethingSelected())


	"""
	Enable/disable the controls in the window
	@param enabled: true if the controls should be enabled.
	"""	
	def enable(self, enabled):
		self._optimizationPanel.enable(enabled)

	"""
	Pipes the update on to the user weight panel
	"""	
	def updateColorSets(self):
		print "selction changed"
		self._optimizationPanel.updateColorSets()		

	#START UI BUILDING

	"""
	Creates the job panel
	@param parentContainer: the container to add the panel to
	"""		
	def createJobPanel(self, parentContainer):
		layout = cmds.frameLayout(parent= parentContainer, l="Jobs", collapsable=True)

	
	"""
	Creates the main window
	@param parentContainer: the container to add the panel to
	"""		
	def createContent(self, parentContainer):
		self._browsingPanel.createPanel(parentContainer)
		self._optimizationPanel.createPanel(parentContainer)
		self._jobPanel.createPanel(parentContainer)
		self._optimizationPanel.setSettingsManager(self._settingsManager)
		if self._settingsManager == None:
			self.enable(False)				

			
	"""
	Called when something is selected in the main viewport. Forces an update of the color selector and enabling/disabling controls
	"""	
	def selectionChanged(self):
		print "selction changed"
		self.updateColorSets()
		self.enable(somethingSelected())


"""
@return: true if something is currently selected.
"""	
def somethingSelected():
	selection = cmds.ls(sl=1)
	if selection == None or selection==[]:
		return False 
	else:
		return True		

WINDOW_NAME = "SimplygonBatchProcessor"
DOCK_NAME = WINDOW_NAME+"Dock"
	
	
"""
Function to expose functionality outside of this module
"""	
def createContent(parentContainer):
	batchProcessor = SimplygonBatchProcessor()
	batchProcessor.createContent(parentContainer)
	return batchProcessor
	
"""
Main function to start the plugin.
"""	
def openSimplygonBatchProcessor():
	#Delete the window if there already is an open instance
	if cmds.window(WINDOW_NAME, exists=True):
		cmds.deleteUI(WINDOW_NAME)
	if cmds.dockControl(DOCK_NAME, exists=True):
		cmds.deleteUI(DOCK_NAME)

	window = cmds.window(WINDOW_NAME, title="Batch Processor", iconName="DL" )
	layout = cmds.columnLayout (adjustableColumn = True)
	dock = cmds.dockControl(DOCK_NAME, area="right", content=window, l="Batch Processor", width=500)
	# Add the simplygon logo for graphical splendor.
	cmds.image(parent = layout, image=SIMPLYGON_LOGO, w=300)
	batchProcessor = createContent(layout)
	# Start a script job that listens to selection changed events.
	cmds.scriptJob( event= ["SelectionChanged",batchProcessor.selectionChanged], protected=True, parent = dock)
