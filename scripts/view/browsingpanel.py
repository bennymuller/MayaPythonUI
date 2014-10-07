import maya.cmds as cmds
import simplygonpanel
reload(simplygonpanel)
from simplygonpanel import SimplygonPanel

CTRL_SETTINGSDIR = "SettingsDir"
CTRL_BROWSEBUTTON = "OptButton"

"""
Wrapper for the browsing panel.
"""
class BrowsingPanel(SimplygonPanel):
	def __init__(self, batchProcessor):
		SimplygonPanel.__init__(self, "Browsing", batchProcessor)
		self.defineControl(CTRL_SETTINGSDIR, "TextField")
		self.defineControl(CTRL_BROWSEBUTTON, "Button")		

	"""
	Opens up a browser window that allows the user to specify where you can find the XML that describes the setting files to use
	"""	
	def onBrowse(self, _):
		selectedSettings = cmds.fileDialog2(fm=1, fileFilter="XML Files (*.xml)", okc="Set")
		if selectedSettings != None:
			cmds.textField(self.getMObj(CTRL_SETTINGSDIR), edit=True, text=selectedSettings[0])
			self._batchProcessor.setSettingsXML(selectedSettings[0])		
			print self._batchProcessor.settingsXML

	"""
	Creates the panel containing the browsing component for the setting file xml and adds it to the main layout.
	@param parentContainer: the container to add the panel to
	"""		
	def createPanel(self, parentContainer):
		layout = cmds.rowLayout (parent= parentContainer, numberOfColumns = 2)
		sd = cmds.textField(parent= layout, ed=False, w=400, text=self._batchProcessor.settingsXML)
		self.setMObj(CTRL_SETTINGSDIR, sd)
		bb = cmds.button(parent= layout, label = "Browse", command = self.onBrowse)	
		self.setMObj(CTRL_BROWSEBUTTON, bb)
		
	"""
	Enables/disables browsing panel
	@param enabled: true to enable all the components.
	"""
	def enable(self, enabled):
		#Only enable the color set selector if user weights are enabled
		cmds.textField(self.getMObj(CTRL_SETTINGSDIR), edit=True, en=enabled)
		cmds.button(self.getMObj(CTRL_BROWSEBUTTON), edit=True, en=enabled)
