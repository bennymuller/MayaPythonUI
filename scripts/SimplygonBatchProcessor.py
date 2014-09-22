import maya.cmds as cmds
import maya.mel as mel
import inspect, os
import OptimizationManagerModule
reload(OptimizationManagerModule)
from OptimizationManagerModule import *

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

"""
Wrapper for the user weight data panel. 
"""
class UserWeightsData:
	def __init__(self):
		self.userWeightCheckBoxCtrl = None
		self.colorSetListCtrl = None
		self.wmSliderCtrl = None
		self.wmText = None

	"""
	Creates the panel that contains the user weights settings
	@param parentContainer: the container to add the user weight panel to 
	@return: the layout that contains all the components
	"""
	def createComponent(self, parentContainer):
		# Add the user weights components
		layout = cmds.frameLayout(parent= parentContainer, l="User weights", collapsable=True)
		cmds.separator(parent= layout, height=1, style="none")
		weightsLayout = cmds.rowLayout (parent= layout, numberOfColumns = 2)
		self.userWeightCheckBoxCtrl = cmds.checkBox(l="Enable", w=150, parent= weightsLayout, onc=userWeightsChanged, ofc=userWeightsChanged)
		self.colorSetListCtrl = cmds.optionMenu(parent= weightsLayout, w=350, en=False)
		cmds.separator(parent= layout, height=1, style="none")
		weightsMulLayout = cmds.rowLayout (parent= layout, numberOfColumns = 2)
		cmds.text(parent= weightsMulLayout, l="Weights multiplier", align="right", w=150)
		self.wmSliderCtrl = cmds.intSlider(min=1, max=8, value=1, step=1, parent= weightsMulLayout, w=350)
		cmds.separator(parent= layout, height=1, style="none")	
		return layout

	"""
	@return: true if the user weight checkbox is checked
	"""
	def useUserWeights(self):
		return cmds.checkBox(self.userWeightCheckBoxCtrl, query = True, value=True)

	"""
	@return: the integer value that the weight multiplier slider is set to
	"""
	def getWeightMultiplier(self):
		return cmds.intSlider(self.wmSliderCtrl, query=True, value=True)

	"""
	@return: the selected color set
	"""
	def getColorSet(self):
		return cmds.optionMenu(self.colorSetListCtrl, query=True, value=True)
		

	"""
	Should be called every time the color set selector needs to be updated. Will remove the current
	set of options and fetch the current possible sets and add them to the droplist
	"""
	def updateColorSets(self):
		# Delete the current set of color sets
		try:
			menuItems = cmds.optionMenu(self.colorSetListCtrl, q=True, itemListLong=True)
			if menuItems != None and menuItems != []:
				cmds.deleteUI(menuItems)
		except:
			pass
		colorSets = cmds.polyColorSet( query=True, allColorSets=True)
		if colorSets :
			for c in colorSets:
				cmds.menuItem(parent=self.colorSetListCtrl, label=c)
		if cmds.checkBox(self.userWeightCheckBoxCtrl, query = True, value=True):
			cmds.optionMenu(self.colorSetListCtrl, edit=True, en=True)	
			cmds.intSlider(self.wmSliderCtrl, edit=True, en=True)				
		else: 
			cmds.optionMenu(self.colorSetListCtrl, edit=True, en=False)	
			cmds.intSlider(self.wmSliderCtrl, edit=True, en=False)	
			
		
	"""
	Enables/disables the user weight selection
	@param enabled: true to enable all the components.
	"""
	def enable(self, enabled):
		#Only enable the color set selector if user weights are enabled
		cmds.checkBox(self.userWeightCheckBoxCtrl, edit=True, en=enabled)
		useUserWeights = cmds.checkBox(self.userWeightCheckBoxCtrl, query = True, value=True)
		cmds.optionMenu(self.colorSetListCtrl, edit=True, en=enabled and useUserWeights)
		cmds.intSlider(self.wmSliderCtrl, edit=True, en=enabled and useUserWeights)				

"""
The main class for the Simplygon Batch processor. Handles a dock window and setting up all the components.
"""		
class SimplygonBatchProcessor:
	def __init__(self):		
		#Start listening to selection changes to modify the color set selector
		self.WINDOW_NAME = "SimplygonBatchProcessor"
		self.DOCK_NAME =self.WINDOW_NAME+"Dock"
		self.settingsXML = ""
		self.userWeightData = UserWeightsData()

		#For clarity all of the controls are declared here.
		self.settingsDirCtrl = None
		self.settingsFileListCtrl = None
		self.optimizeButton = None
		self.mainLayout = None
		self.optimizationContainer = None
		self.simplygonButton = None
		self.settingsManager = None
		#END controls
		
		# Fetch the settings file folder from the environment.
		if cmds.optionVar(exists= SETTINGS_FILE_SETTING):
			self.settingsXML = cmds.optionVar(q=SETTINGS_FILE_SETTING)
			self.settingsManager = OptimizationSettingsManager(self.settingsXML)

	"""
	Opens up a browser window that allows the user to specify where you can find the XML that describes the setting files to use
	"""	
	def onBrowse(self, _):
		self.settingsXML = cmds.fileDialog2(fm=1, fileFilter="XML Files (*.xml)", okc="Set")[0]
		cmds.optionVar( sv=(SETTINGS_FILE_SETTING, self.settingsXML) )
		cmds.textField(self.settingsDirCtrl, edit=True, text=self.settingsXML)
		# Set up a new settings manager with the new XML.
		self.settingsManager = OptimizationSettingsManager(self.settingsXML)
		self.updateSettingFileList()
			
	"""
	Refreshes the settings drop list based of the current settings in the settings manager.
	"""	
	def updateSettingFileList(self):
		# Delete the current set of settings
		try:
			menuItems = cmds.optionMenu(self.settingsFileListCtrl, q=True, itemListLong=True)
			if menuItems != None and menuItems != []:
				cmds.deleteUI(menuItems)
		except:
			pass
		settingNames = self.settingsManager.getSettingNames()
		for settingName in settingNames:
			cmds.menuItem(parent=self.settingsFileListCtrl, label=settingName)
	"""
	Starts a Simplygon optimization in batch mode with the currently selected settings.
	"""	
	def onOptimize(self, _):
		self.startSimplygon(True)

	"""
	Starts the Simplygon GUI with the currently selected settings and selected objects.
	"""	
	def onSimplygon(self, _):
		self.startSimplygon(False)
	
	"""
	Starts a new Simplygon process. Will generate a temporary settings file to use during this optimization.
	@param batch: true if the process should be run in batch mode
	"""	
	def startSimplygon(self, batch):
		tempPath = os.path.dirname(os.path.realpath(self.settingsXML))
		tempFile = tempPath+"/"+TEMP_SETTING_FILE
		tempFile = tempFile.replace("\\", "/")
		# Write out a temporary settings file with the overriden settings included
		with open(tempFile, 'wb') as outFile:
			self.settingsManager.writeTempConfig(outFile)
		melCmd = "Simplygon -sf \""+tempFile+"\""
		if batch:
			melCmd += " -b"
		#Check if the user weights are enabled, in that case send that along to Simplygon.
		uwEnabled = self.userWeightData.useUserWeights();
		if uwEnabled:
			colorSet = self.userWeightData.getColorSet()
			if colorSet != None:
				melCmd += " -caw \""+colorSet+"\" -wm "+ str(self.userWeightData.getWeightMultiplier())
		print melCmd
		lods = mel.eval(melCmd)
		#Remove the temporary processing file
		os.remove(tempFile)

	"""
	Will update the settings components whenever the selected setting has been changed.
	"""	
	def settingChanged(self):
		selectedSettingName = cmds.optionMenu(self.settingsFileListCtrl, query=True, value=True)
		self.settingsManager.settingChanged(self.optimizationContainer, selectedSettingName)
		self.enable(somethingSelected())
		
	"""
	Enable/disable the controls in the window
	@param enabled: true if the controls should be enabled.
	"""	
	def enable(self, enabled):
		cmds.button(self.optimizeButton, edit=True, en=enabled)
		cmds.button(self.simplygonButton, edit=True, en=enabled)
		if self.userWeightData != None:
			self.userWeightData.enable(enabled)
		if self.settingsManager != None:
			self.settingsManager.enable(enabled)
			
	"""
	Pipes the update on to the user weight panel
	"""	
	def updateColorSets(self):
		self.userWeightData.updateColorSets()		
		
	#START UI BUILDING

	"""
	Creates the panel containing the browsing component for the setting file xml and adds it to the main layout.
	"""		
	def createBrowsingPanel(self):
		layout = cmds.rowLayout (parent= self.mainLayout, numberOfColumns = 2)
		self.settingsDirCtrl = cmds.textField(parent= layout, ed=False, w=400, text=self.settingsXML)
		cmds.button(parent= layout, label = "Browse", command = self.onBrowse)	
		
	"""
	Creates the panel containing the setting drop list and add it to the main layout.
	"""	
	def createSettingSelectorPanel(self):
		layout = cmds.columnLayout (parent= self.mainLayout, adjustableColumn = True)
		# Create the header
		cmds.text(parent= layout, l="Optimization settings", align="center", font="boldLabelFont")
		cmds.separator(parent= layout, height=20, style="doubleDash")

		#Add the settings browser component
		self.settingsFileListCtrl = cmds.optionMenu(parent= layout, cc=settingChanged)
		if len(self.settingsXML) > 0:
			self.updateSettingFileList()
		cmds.separator(parent= layout, height=20, style="none")
		
	"""
	Creates the main window
	"""		
	def setupWindow(self):
		#Delete the window if there already is an open instance
		if cmds.window(self.WINDOW_NAME, exists=True):
			cmds.deleteUI(self.WINDOW_NAME)
		if cmds.dockControl(self.DOCK_NAME, exists=True):
			cmds.deleteUI(self.DOCK_NAME)

		window = cmds.window(self.WINDOW_NAME, title="Batch Processor", iconName="DL" )
		self.mainLayout = cmds.columnLayout (adjustableColumn = True)
		
		# Add the simplygon logo for graphical splendor.
		cmds.image(parent = self.mainLayout, image=SIMPLYGON_LOGO, w=300)
		
		# Add the components that shows allows for browsing to the setting file directory
		self.createBrowsingPanel()

		# Add the setting selector panel
		self.createSettingSelectorPanel()
		
		self.optimizationContainer = cmds.columnLayout (parent= self.mainLayout, adjustableColumn = True)
		self.userWeightData.createComponent(self.optimizationContainer)

		#Add the optimization button
		endLayout = cmds.columnLayout (parent = self.mainLayout, adjustableColumn = True)
		cmds.separator(parent= endLayout, height=20, style="none")
		self.optimizeButton = cmds.button(parent= endLayout, label="Optimize", c=self.onOptimize)		

		cmds.separator(parent= endLayout, height=20, style="none")
		self.simplygonButton = cmds.button(parent= endLayout, label="Send to Simplygon", c=self.onSimplygon)		

		#Force an update of the color set selector
		self.updateColorSets()
		# Force an update of the setting selector
		if self.settingsManager != None:
			self.settingChanged()
		else:
			self.enable(False)
		
		cmds.dockControl(self.DOCK_NAME, area="right", content=window, l="Batch Processor", width=500)

# This is ugly as hell, but since Maya seems to randomly crash when events are triggered on member functions we pipe them outside.
batchProcessor = ""
	
"""
Called when there is a change in selection in the settings drop list
"""	
def settingChanged(_):
	batchProcessor.settingChanged()

"""
Called when the user enables/disables the user weight check box.
"""	
def userWeightsChanged(_):
	batchProcessor.updateColorSets()

"""
@return: true if something is currently selected.
"""	
def somethingSelected():
	selection = cmds.ls(sl=1)
	if selection == None or selection==[]:
		return False 
	else:
		return True
		
"""
Called when something is selected in the main viewport. Forces an update of the color selector and enabling/disabling controls
"""	
def selectionChanged():
	batchProcessor.updateColorSets()
	batchProcessor.enable(somethingSelected())
		
"""
Main function to start the plugin.
"""	
def openSimplygonBatchProcessor():
	global batchProcessor
	batchProcessor = SimplygonBatchProcessor()
	batchProcessor.setupWindow()
	# Start a script job that listens to selection changed events.
	cmds.scriptJob( event= ["SelectionChanged",selectionChanged], protected=True, parent = batchProcessor.DOCK_NAME)
