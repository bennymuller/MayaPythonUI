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


__author__ = "Samuel Rantaeskola"
__copyright__ = "Copyright 2014, Donya Labs AB"
__credits__ = ["Samuel Rantaeskola"]
__license__ = "ALv2"
__version__ = "0.2"
__maintainer__ = "Samuel Rantaeskola"
__email__ = "samuel@simplygon.com"
__status__ = "Prototype"

SETTINGS_FILE_SETTING = "SimplygonSettingsFileXML9dsa"
TEMP_SETTING_FILE = "__temp_processing.ini"
SIMPLYGON_LOGO = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))+"/simplygon_logo.png" #Replace this line to point out your logo

"""
Wrapper for the user weight data panel. 
"""
class UserWeightsPanel:
	def __init__(self, batchProcessor):
		self._batchProcessor = batchProcessor
		self._userWeightCheckBoxCtrl = None
		self._colorSetListCtrl = None
		self._wmSliderCtrl = None

	"""
	Creates the panel that contains the user weights settings
	@param parentContainer: the container to add the user weight panel to 
	@return: the layout that contains all the components
	"""
	def createPanel(self, parentContainer):
		# Add the user weights components
		layout = cmds.frameLayout(parent= parentContainer, l="User weights", collapsable=True, collapse=True, font = "boldLabelFont")
		cmds.separator(parent= layout, height=1, style="none")
		weightsLayout = cmds.rowLayout (parent= layout, numberOfColumns = 2)
		self._userWeightCheckBoxCtrl = cmds.checkBox(l="Enable", w=150, parent= weightsLayout, onc=self.updateColorSets, ofc=self.updateColorSets)
		self._colorSetListCtrl = cmds.optionMenu(parent= weightsLayout, w=350, en=False)
		cmds.separator(parent= layout, height=1, style="none")
		weightsMulLayout = cmds.rowLayout (parent= layout, numberOfColumns = 2)
		cmds.text(parent= weightsMulLayout, l="Weights multiplier", align="right", w=150)
		self._wmSliderCtrl = cmds.intSlider(min=1, max=8, value=1, step=1, parent= weightsMulLayout, w=350)
		cmds.separator(parent= layout, height=1, style="none")	
		return layout

	"""
	@return: true if the user weight checkbox is checked
	"""
	@property
	def useUserWeights(self):
		return cmds.checkBox(self._userWeightCheckBoxCtrl, query = True, value=True)

	"""
	@return: the integer value that the weight multiplier slider is set to
	"""
	@property
	def weightMultiplier(self):
		return cmds.intSlider(self._wmSliderCtrl, query=True, value=True)

	"""
	@return: the selected color set
	"""
	@property
	def colorSet(self):
		return cmds.optionMenu(self._colorSetListCtrl, query=True, value=True)
		

	"""
	Should be called every time the color set selector needs to be updated. Will remove the current
	set of options and fetch the current possible sets and add them to the droplist
	"""
	def updateColorSets(self, *args):
		# Delete the current set of color sets
		try:
			menuItems = cmds.optionMenu(self._colorSetListCtrl, q=True, itemListLong=True)
			if menuItems != None and menuItems != []:
				cmds.deleteUI(menuItems)
		except:
			pass
		colorSets = cmds.polyColorSet( query=True, allColorSets=True)
		if colorSets :
			for c in colorSets:
				cmds.menuItem(parent=self._colorSetListCtrl, label=c)
		if cmds.checkBox(self._userWeightCheckBoxCtrl, query = True, value=True):
			cmds.optionMenu(self._colorSetListCtrl, edit=True, en=True)	
			cmds.intSlider(self._wmSliderCtrl, edit=True, en=True)				
		else: 
			cmds.optionMenu(self._colorSetListCtrl, edit=True, en=False)	
			cmds.intSlider(self._wmSliderCtrl, edit=True, en=False)	
			
		
	"""
	Enables/disables the user weight selection
	@param enabled: true to enable all the components.
	"""
	def enable(self, enabled):
		#Only enable the color set selector if user weights are enabled
		cmds.checkBox(self._userWeightCheckBoxCtrl, edit=True, en=enabled)
		useUserWeights = cmds.checkBox(self._userWeightCheckBoxCtrl, query = True, value=True)
		cmds.optionMenu(self._colorSetListCtrl, edit=True, en=enabled and useUserWeights)
		cmds.intSlider(self._wmSliderCtrl, edit=True, en=enabled and useUserWeights)				

		
class OptimizationPanel:
	def __init__(self, batchProcessor):
		self._batchProcessor = batchProcessor
		self._userWeightPanel = UserWeightsPanel(batchProcessor)
		self._optimizationContainer = None
		self._settingsManager = None
		self._optimizeButton = None
		self._simplygonButton = None

	def setSettingsXML(self, settingsXML):
		if self._settingsManager != None:
			self._settingsManager.clear()
		self._settingsManager = OptimizationSettingsManager(settingsXML)

		
	"""
	@return: true if the user weight checkbox is checked
	"""
	@property
	def useUserWeights(self):
		return self._userWeightPanel.useUserWeights

	"""
	@return: the integer value that the weight multiplier slider is set to
	"""
	@property
	def weightMultiplier(self):
		return self._userWeightPanel.weightMultiplier

	"""
	@return: the selected color set
	"""
	@property
	def colorSet(self):
		return self._userWeightPanel.colorSet
		
	def updateColorSets(self):
		self._userWeightPanel.updateColorSets()
		
	"""
	Creates the panel containing the setting drop list and add it to the main layout.
	@param parentContainer: the container to add the panel to
	"""	
	def createSettingSelectorPanel(self, parentContainer):
		layout = cmds.columnLayout (parent= parentContainer, adjustableColumn = True)
		# Create the header
		cmds.text(parent= layout, l="Optimization settings", align="center", font="boldLabelFont")
		cmds.separator(parent= layout, height=20, style="doubleDash")

		#Add the settings browser component
		self._settingsFileListCtrl = cmds.optionMenu(parent= layout, cc=self.settingChanged)
		if self._settingsManager != None:
			self.updateSettingFileList()
		cmds.separator(parent= layout, height=20, style="none")
		
	
	@property
	def settingsManager(self):
		return self._settingsManager
	
	def writeTempConfig(self, outFile):
		self._settingsManager.writeTempConfig(outFile)
		
	"""
	Creates the main window
	@param parentContainer: the container to add the panel to
	"""		
	def createPanel(self, parentContainer):
		# Add the setting selector panel
		self.createSettingSelectorPanel(parentContainer)		
		self._optimizationContainer = cmds.frameLayout(parent= parentContainer, borderStyle = 'etchedOut', borderVisible=True, lv =False)
		self._userWeightPanel.createPanel(parentContainer)
		endLayout = cmds.rowLayout(numberOfColumns=2, parent= parentContainer)
		self._optimizeButton = cmds.button(parent= endLayout, label="Optimize", c=self.onOptimize, w=250)		
		self._simplygonButton = cmds.button(parent= endLayout, label="Send to Simplygon", c=self.onSimplygon, w=250)
		
	"""
	Starts a Simplygon optimization in batch mode with the currently selected settings.
	"""	
	def onOptimize(self, _):
		self._batchProcessor.startSimplygon(True)

	"""
	Starts the Simplygon GUI with the currently selected settings and selected objects.
	"""	
	def onSimplygon(self, _):
		self._batchProcessor.startSimplygon(False)		

			
	"""
	Will update the settings components whenever the selected setting has been changed.
	"""	
	def settingChanged(self, *args):
		selectedItemIndex = cmds.optionMenu(self._settingsFileListCtrl, query=True, select=True)-1
		menuItems = cmds.optionMenu(self._settingsFileListCtrl, q=True, itemListLong=True)
		selectedSettingID = 0
		if menuItems != None and (menuItems != [] or len(menuItems) < selectedItemIndex):
			selectedSettingID = cmds.menuItem(menuItems[selectedItemIndex], query=True, data=True)

		if self._settingsManager != None:
			self._settingsManager.settingChanged(self._optimizationContainer, selectedSettingID)
		self._batchProcessor.enable(somethingSelected())

	"""
	Refreshes the settings drop list based of the current settings in the settings manager.
	"""	
	def updateSettingFileList(self):
		# Delete the current set of settings
		try:
			menuItems = cmds.optionMenu(self._settingsFileListCtrl, q=True, itemListLong=True)
			if menuItems != None and menuItems != []:
				cmds.deleteUI(menuItems)
		except:
			pass
		settings = self._settingsManager.getSettings()
		for s in settings:
			cmds.menuItem(parent=self._settingsFileListCtrl, label=s.name, data=s.id)
		self._settingsManager.settingChanged(self._optimizationContainer, 0)
			
	"""
	Enable/disable the controls in the window
	@param enabled: true if the controls should be enabled.
	"""	
	def enable(self, enabled):
		cmds.button(self._optimizeButton, edit=True, en=enabled)
		cmds.button(self._simplygonButton, edit=True, en=enabled)
		if self._settingsManager != None:
			self._settingsManager.enable(enabled)
		self._userWeightPanel.enable(enabled)

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

class JobPanel:
	def __init__(self, batchProcessor):
		self._batchProcessor = batchProcessor
		self._jobs = []
				
	def createPanel(self, parentContainer):
		layout = cmds.frameLayout(parent= parentContainer, l="Jobs", collapsable=False)
		cmds.button(parent= layout, label = "Manage Output", command = self.onManageOutput)	
	
	def addJob(self, job):
		self._jobs.append(job)
		
	def onManageOutput(self, job):
		window = ManageOutputWindow(self._jobs)
		window.showWindow()
		
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
		self._settingsXML = None
		# Fetch the settings file folder from the environment.
		if cmds.optionVar(exists= SETTINGS_FILE_SETTING):
			self._settingsXML = cmds.optionVar(q=SETTINGS_FILE_SETTING)
			self._optimizationPanel.setSettingsXML(self._settingsXML)
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
			self._optimizationPanel.writeTempConfig(outFile)

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
		self._optimizationPanel.setSettingsXML(self._settingsXML)
		self._optimizationPanel.updateSettingFileList()
		

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
		# Force an update of the setting selector
		if self._optimizationPanel.settingsManager != None:
			self._optimizationPanel.settingChanged(None)
		else:
			self.enable(False)				

			
	"""
	Called when something is selected in the main viewport. Forces an update of the color selector and enabling/disabling controls
	"""	
	def selectionChanged(self):
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
