import maya.cmds as cmds
import SimplygonPanelModule
reload(SimplygonPanelModule)
from SimplygonPanelModule import SimplygonPanel
import UserWeightPanelModule
reload(UserWeightPanelModule)
from UserWeightPanelModule import UserWeightsPanel

CTRL_OPTCONTAINTER = "OptContainer"
CTRL_OPTBUTTON = "OptButton"
CTRL_SIMPLYGONBUTTON = "SimplygonButton"
CTRL_SETTINGSSELECTOR = "SettingsSelector"

"""
Wrapper for the optimization setting panel.
"""
class OptimizationPanel(SimplygonPanel):
	def __init__(self, batchProcessor):
		SimplygonPanel.__init__(self, "OptimizationSettings", batchProcessor)
		self._userWeightPanel = UserWeightsPanel(batchProcessor)
		self._settingsManager = None
		self.defineControl(CTRL_OPTCONTAINTER, "Container")
		self.defineControl(CTRL_OPTBUTTON, "Button")
		self.defineControl(CTRL_SIMPLYGONBUTTON, "Button")
		self.defineControl(CTRL_SETTINGSSELECTOR, "OptionMenu")

	"""
	Sets the manager of all the optimization settings. It's a bit messed up as it also holds some GUI logic. (TODO: Fix that!)
	@param settingManager: the new settings manager
	"""
	def setSettingsManager(self, settingManager):
		self._settingsManager = settingManager
		if self._settingsManager != None:
			self.updateSettingFileList()

		
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
		
	"""
	Forwards the call to the user weights panel
	"""
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
		ss = cmds.optionMenu(parent= layout, cc=self.settingChanged)
		self.setMObj(CTRL_SETTINGSSELECTOR, ss)
		if self._settingsManager != None:
			self.updateSettingFileList()
		cmds.separator(parent= layout, height=20, style="none")
					
	"""
	Creates the main window
	@param parentContainer: the container to add the panel to
	"""		
	def createPanel(self, parentContainer):
		# Add the setting selector panel
		self.createSettingSelectorPanel(parentContainer)		
		oc = cmds.frameLayout(parent= parentContainer, borderStyle = 'etchedOut', borderVisible=True, lv =False)
		self.setMObj(CTRL_OPTCONTAINTER,oc)
		self._userWeightPanel.createPanel(parentContainer)
		endLayout = cmds.rowLayout(numberOfColumns=2, parent= parentContainer)
		ob = cmds.button(parent= endLayout, label="Optimize", c=self.onOptimize, w=250)		
		self.setMObj(CTRL_OPTBUTTON,ob)
		sb = cmds.button(parent= endLayout, label="Send to Simplygon", c=self.onSimplygon, w=250)
		self.setMObj(CTRL_SIMPLYGONBUTTON,sb)
		
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
		settingSelector = self.getMObj(CTRL_SETTINGSSELECTOR)
		selectedItemIndex = cmds.optionMenu(settingSelector, query=True, select=True)-1
		menuItems = cmds.optionMenu(settingSelector, q=True, itemListLong=True)
		selectedSettingID = 0
		if menuItems != None and (menuItems != [] or len(menuItems) < selectedItemIndex):
			selectedSettingID = cmds.menuItem(menuItems[selectedItemIndex], query=True, data=True)

		if self._settingsManager != None:
			self._settingsManager.settingChanged(self.getMObj(CTRL_OPTCONTAINTER), selectedSettingID)
		self._batchProcessor.settingChanged()

	"""
	Refreshes the settings drop list based of the current settings in the settings manager.
	"""	
	def updateSettingFileList(self):
		# Delete the current set of settings
		settingSelector = self.getMObj(CTRL_SETTINGSSELECTOR)
		try:
			menuItems = cmds.optionMenu(settingSelector, q=True, itemListLong=True)
			if menuItems != None and menuItems != []:
				cmds.deleteUI(menuItems)
		except:
			pass
		settings = self._settingsManager.getSettings()
		for s in settings:
			cmds.menuItem(parent=settingSelector, label=s.name, data=s.id)
		self._settingsManager.settingChanged(self.getMObj(CTRL_OPTCONTAINTER), 0)
			
	"""
	Enable/disable the controls in the window
	@param enabled: true if the controls should be enabled.
	"""	
	def enable(self, enabled):
		cmds.button(self.getMObj(CTRL_OPTBUTTON), edit=True, en=enabled)
		cmds.button(self.getMObj(CTRL_SIMPLYGONBUTTON), edit=True, en=enabled)
		if self._settingsManager != None:
			self._settingsManager.enable(enabled)
		self._userWeightPanel.enable(enabled)