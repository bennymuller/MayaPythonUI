import maya.mel as mel
import maya.cmds as cmds
import inspect, os

import model.optimizationmanager
reload(model.optimizationmanager)
from model.optimizationmanager import *
import data.simplygonjob
reload (data.simplygonjob)
from data.simplygonjob import *
import data.processdirectives
reload (data.processdirectives)
from data.processdirectives import *	
import view.optimizationpanel
reload(view.optimizationpanel)
from view.optimizationpanel import OptimizationPanel
import view.browsingpanel
reload(view.browsingpanel)
from view.browsingpanel import BrowsingPanel
import view.jobpanel
reload(view.jobpanel)
from view.jobpanel import JobPanel


__author__ = "Samuel Rantaeskola"
__copyright__ = "Copyright 2014, Donya Labs AB"
__credits__ = ["Samuel Rantaeskola"]
__license__ = "ALv2"
__version__ = "0.3"
__maintainer__ = "Samuel Rantaeskola"
__email__ = "samuel@simplygon.com"
__status__ = "Prototype"

SETTINGS_FILE_SETTING = "SimplygonSettingsFileXML"
TEMP_SETTING_FILE = "__temp_processing.ini"
SIMPLYGON_LOGO = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))+"/simplygon_logo.png" #Replace this line to point out your logo
		
"""
The main class for the Simplygon Batch processor. Handles a dock window and setting up all the components.
"""		
class SimplygonBatchProcessor:
	def __init__(self):		
		self._browsingPanel = BrowsingPanel(self)
		self._jobPanel = JobPanel(self)
		self._optimizationPanel = OptimizationPanel(self)
		self._settingsManager = None
		self._settingsXML = ""
		self._jobs = []
		# Fetch the settings file folder from the environment.
		if cmds.optionVar(exists= SETTINGS_FILE_SETTING):
			self._settingsXML = cmds.optionVar(q=SETTINGS_FILE_SETTING)
			self._settingsManager = OptimizationSettingsManager(self._settingsXML)
	
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	START PROPERTIES
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@property
	def settingsXML(self):
		return self._settingsXML

	@settingsXML.setter			
	def settingsXML(self, settingsXML):
		self._settingsXML = settingsXML
		cmds.optionVar( sv=(SETTINGS_FILE_SETTING, self._settingsXML) )
		if self._settingsManager != None:
			self._settingsManager.clear()
		self._settingsManager = OptimizationSettingsManager(self._settingsXML)
		self._optimizationPanel.setSettingsManager(self._settingsManager)

	@property
	def jobs(self):
		return self._jobs
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	END PROPERTIES
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
		
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
		melCmd = "Simplygon -sf \""+directives.settingFile+"\" "
		if directives.batchMode:
			melCmd += "-b "
		#Check if the user weights are enabled, in that case send that along to Simplygon.
		if directives.useWeights:
			if directives.colorSet != None:
				melCmd += "-caw \""+directives.colorSet+"\" -wm "+ str(directives.weightMultiplier)

		job = SimplygonJob()
		job.directives = directives
		job.start()
		result = mel.eval(melCmd)
		job.end()
		# Need to capture failure
		job.succesful = True
		self._jobs.append(job)
		#Remove the temporary processing file
		os.remove(tempFile)
		if self._jobPanel.autoClean:
			job.pruneTexturesAndMaterials()
			job.makeLayers()
			job.moveTextures(self._jobPanel.textureDir)		


	"""
	Refreshes the content in all views.
	@param enabled: true if items should be enabled.
	"""	
	def refreshViews(self):
		self._optimizationPanel.updateColorSets()		
		enable = True
		selection = cmds.ls(sl=1)
		if selection == None or selection==[]:
			enable = False
		self._optimizationPanel.enable(enable)
		
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
	cmds.scriptJob( event= ["SelectionChanged",batchProcessor.refreshViews], protected=True, parent = dock)
