import maya.cmds as cmds
import simplygonpanel
reload(simplygonpanel)
from simplygonpanel import SimplygonPanel

CTRL_USERWEIGHTS = "UseUserWeigths"
CTRL_COLORSETS = "ColorSets"
CTRL_WEIGHTMULTIPLIER = "WeightMultiplier"

"""
Wrapper for the user weight data panel. 
"""
class UserWeightsPanel(SimplygonPanel):
	def __init__(self, batchProcessor):
		SimplygonPanel.__init__(self, "UserWeights", batchProcessor)
		self.defineControl(CTRL_USERWEIGHTS, "CheckBox")
		self.defineControl(CTRL_COLORSETS, "OptionsMenu")
		self.defineControl(CTRL_WEIGHTMULTIPLIER, "IntSlider")

	"""
	Creates the panel that contains the user weights settings
	@param parentContainer: the container to add the user weight panel to 
	"""
	def createPanel(self, parentContainer):
		# Add the user weights components
		layout = cmds.frameLayout(parent= parentContainer, l="User weights", collapsable=True, collapse=True, font = "boldLabelFont")
		cmds.separator(parent= layout, height=1, style="none")
		weightsLayout = cmds.rowLayout (parent= layout, numberOfColumns = 2)
		cb = cmds.checkBox(l="Enable", w=150, parent= weightsLayout, onc=self.updateColorSets, ofc=self.updateColorSets)
		self.setMObj(CTRL_USERWEIGHTS, cb)
		cls = cmds.optionMenu(parent= weightsLayout, w=350, en=False)
		self.setMObj(CTRL_COLORSETS, cls)
		cmds.separator(parent= layout, height=1, style="none")
		weightsMulLayout = cmds.rowLayout (parent= layout, numberOfColumns = 2)
		cmds.text(parent= weightsMulLayout, l="Weights multiplier", align="right", w=150)
		wm = cmds.intSlider(min=1, max=8, value=1, step=1, parent= weightsMulLayout, w=350)
		self.setMObj(CTRL_WEIGHTMULTIPLIER, wm)
		cmds.separator(parent= layout, height=1, style="none")	

	"""
	@return: true if the user weight checkbox is checked
	"""
	@property
	def useUserWeights(self):
		return cmds.checkBox(self.getMObj(CTRL_USERWEIGHTS), query = True, value=True)

	"""
	@return: the integer value that the weight multiplier slider is set to
	"""
	@property
	def weightMultiplier(self):
		return cmds.intSlider(self.getMObj(CTRL_WEIGHTMULTIPLIER), query=True, value=True)

	"""
	@return: the selected color set
	"""
	@property
	def colorSet(self):
		return cmds.optionMenu(self.getMObj(CTRL_COLORSETS), query=True, value=True)
		

	"""
	Should be called every time the color set selector needs to be updated. Will remove the current
	set of options and fetch the current possible sets and add them to the droplist
	"""
	def updateColorSets(self, *args):
		# Delete the current set of color sets
		csSelector = self.getMObj(CTRL_COLORSETS)
		try:
			menuItems = cmds.optionMenu(csSelector, q=True, itemListLong=True)
			if menuItems != None and menuItems != []:
				cmds.deleteUI(menuItems)
		except:
			pass
		colorSets = cmds.polyColorSet( query=True, allColorSets=True)
		if colorSets :
			for c in colorSets:
				cmds.menuItem(parent=csSelector, label=c)
		if self.useUserWeights:
			cmds.optionMenu(csSelector, edit=True, en=True)	
			cmds.intSlider(self.getMObj(CTRL_WEIGHTMULTIPLIER), edit=True, en=True)				
		else: 
			cmds.optionMenu(csSelector, edit=True, en=False)	
			cmds.intSlider(self.getMObj(CTRL_WEIGHTMULTIPLIER), edit=True, en=False)	
			
		
	"""
	Enables/disables the user weight selection
	@param enabled: true to enable all the components.
	"""
	def enable(self, enabled):
		#Only enable the color set selector if user weights are enabled
		cmds.checkBox(self.getMObj(CTRL_USERWEIGHTS), edit=True, en=enabled)
		cmds.optionMenu(self.getMObj(CTRL_COLORSETS), edit=True, en=enabled and self.useUserWeights)
		cmds.intSlider(self.getMObj(CTRL_WEIGHTMULTIPLIER), edit=True, en=enabled and self.useUserWeights)				
