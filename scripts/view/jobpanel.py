import maya.cmds as cmds
import simplygonpanel
reload(simplygonpanel)
from simplygonpanel import SimplygonPanel
import manageoutputwindow
reload(manageoutputwindow)
from manageoutputwindow import *

CTRL_AUTOCLEANUP = "AutoCleanUp"
CTRL_TEXTUREDEST = "TextureDestination"
CTRL_MANAGEOUTPUT = "ManageOuput"
CTRL_BROWSE = "Browse"
TEXTURE_DESTINATION_SETTING="SimplygonTextureDestination"		
JOB_AUTO_CLEAN="SimplygonJobAutoClean"		

"""
Wrapper for the job management panel.
"""
class JobPanel(SimplygonPanel):
	def __init__(self, batchProcessor):
		SimplygonPanel.__init__(self, "Jobs", batchProcessor)
		self.defineControl(CTRL_AUTOCLEANUP, "CheckBox")
		self.defineControl(CTRL_TEXTUREDEST, "TextField")		
		self.defineControl(CTRL_MANAGEOUTPUT, "Button")		
		self.defineControl(CTRL_BROWSE, "Button")		
	"""
	Creates the panel containing the job management controls.
	param parentContainer: the container to put the panel in
	"""
	def createPanel(self, parentContainer):
		layout = cmds.frameLayout(parent= parentContainer, l="Jobs", collapsable=False)
		autoClean = False
		if cmds.optionVar(exists= JOB_AUTO_CLEAN):
			autoClean = cmds.optionVar(q=JOB_AUTO_CLEAN) == "True"
		ac = cmds.checkBox(l="Auto Clean Up Jobs", value=autoClean, w=150, parent= layout, onc=self.onAutoClean, ofc=self.onAutoClean)
		self.setMObj(CTRL_AUTOCLEANUP, ac)
		
		browseLayout = cmds.rowLayout (parent= layout, numberOfColumns = 3)
		# Fetch the texture destination folder from the environment.
		textureDestination = ""		
		if cmds.optionVar(exists= TEXTURE_DESTINATION_SETTING):
			textureDestination = cmds.optionVar(q=TEXTURE_DESTINATION_SETTING)
		
		cmds.text(parent= browseLayout, label = "Texture destination:")		
		td = cmds.textField(parent= browseLayout, ed=False, w=400, text=textureDestination)
		self.setMObj(CTRL_TEXTUREDEST, td)				
		self.setMObj(CTRL_BROWSE, cmds.button(parent= browseLayout, label = "Browse", command = self.onBrowse))		
		self.setMObj(CTRL_MANAGEOUTPUT, cmds.button(parent= layout, label = "Manage Output", command = self.onManageOutput))
	
	"""
	Returns true if the user has selected to auto clean the job
	"""
	@property
	def autoClean(self):
		return cmds.checkBox(self.getMObj(CTRL_AUTOCLEANUP), query = True, value=True)

	"""
	Returns the texture directory
	"""
	@property
	def textureDir(self):
		return cmds.textField(self.getMObj(CTRL_TEXTUREDEST), query=True, text=True)
	
	"""
	Shows a window that allows the user to manage the list of jobs.
	"""
	def onManageOutput(self, _):
		window = ManageOutputWindow(self._batchProcessor)
		window.showWindow()
	
	"""
	Allows the user to set a directory to put all created textures in
	"""	
	def onBrowse(self, _):
		textureDestination = cmds.fileDialog2(fm=3, okc="Set")[0]
		if textureDestination != None:
			cmds.textField(self.getMObj(CTRL_TEXTUREDEST), edit=True, text=textureDestination)
			cmds.optionVar( sv=(TEXTURE_DESTINATION_SETTING, textureDestination) )

	"""
	Called when the state of the auto clean checkbox changes to set the env variable
	"""	
	def onAutoClean(self, _):
		cmds.optionVar( sv=(JOB_AUTO_CLEAN, cmds.checkBox(self.getMObj(CTRL_AUTOCLEANUP), query = True, value=True)))
		
	"""
	Enable/disable the controls in the window
	@param enabled: true if the controls should be enabled.
	"""	
	def enable(self, enabled):
		cmds.checkBox(self.getMObj(CTRL_AUTOCLEANUP), edit=True, enable=enabled)
		cmds.textField(self.getMObj(CTRL_TEXTUREDEST), edit=True, enable=enabled)
		cmds.button(self.getMObj(CTRL_MANAGEOUTPUT), edit=True, enable=enabled)
		cmds.button(self.getMObj(CTRL_BROWSE), edit=True, enable=enabled)