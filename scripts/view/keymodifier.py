import maya.cmds as cmds
import xml.etree.ElementTree as etree
"""
Parent class for components that can be used to modify a key in the settings file
"""
class KeyModifier:
	def __init__(self, xmlElement):
		self.description = xmlElement.get("description")
		#Points out which key/section of the config file this is modfying
		self.keyName = xmlElement.get("name")
		self.keySection = xmlElement.get("section")

	"""
	@returns: the name of the key in the configuration file this modifier is targeting
	"""		
	def getKeyName(self):
		return self.keyName

	"""
	@returns: the section of the key in the configuration file this modifier is targeting
	"""		
	def getKeySection(self):
		return self.keySection
		
	"""
	Must be defined in an implementing component. Should create the a component and place it in the parent container.
	@param parentContainer: the container to put the component in
	"""
	def createComponent(self, parentContainer):
		pass
		
	"""
	Must be defined in an implementing component and return the current value of the component	
	@returns: the current value of the component
	"""
	def getValue(self):
		pass

	"""
	Must be defined in an implementing component and allow for the setting of the value of the component
	@param value: a string to set as value for this component
	"""
	def setValue(self, value):
		pass
		
	"""
	Must be defined in an implementing component. Should enable/disable all controls
	@param enabled: true if the component should be enabled.
	"""
	def enable(self, enabled):
		pass	
		
"""
Class that creates a drop list component to select the value for a key from.
"""		
class DropListData(KeyModifier):
	def __init__(self, xmlElement):
		KeyModifier.__init__(self, xmlElement)
		# We need both a dictionary and a description array to maintain item ordering while allowing for description and values.
		self.choices = {}		
		self.descriptions = []
		for key in xmlElement.findall('Choice'):
			val = key.get("value")
			desc = key.get("description")
			if desc == None:
				desc = val
			self.choices[desc] = val
			self.descriptions.append(desc)
			
	"""
	Creates the drop list with a description text as well.
	@param parentContainer: the container the component will be placed in
	"""
	def createComponent(self, parentContainer):
		layout = cmds.rowLayout (parent= parentContainer, numberOfColumns = 2)
		cmds.text(parent= layout, l=self.description, align="right", w=150)
		self.selector = cmds.optionMenu(parent= layout, w=350)
		for desc in self.descriptions:
			cmds.menuItem(parent=self.selector, label=desc)
		return layout
		
	"""
	@returns: the value (not the description) of current select item of the component
	"""
	def getValue(self):
		selectedOption = cmds.optionMenu(self.selector, query=True, value=True)
		return self.choices[selectedOption]
		
	"""
	Sets the selected item in the drop list. The incoming value should be the underlying value, not the description.
	@param value: the value (not the description) of current select item of the component
	"""
	def setValue(self, value):
		for k,v in self.choices.iteritems():
			if v == value:
				cmds.optionMenu(self.selector, edit=True, value=k)	
	
	"""
	Enables/disables the drop list
	@param enabled: true if the component should be enabled.
	"""
	def enable(self, enabled):
		cmds.optionMenu(self.selector, edit=True, en=enabled)
		
		
"""
Class for a boolean key value
"""
class CheckBoxData(KeyModifier):
	def __init__(self, xmlElement):
		KeyModifier.__init__(self, xmlElement)
			
	"""
	Creates the check box
	@param parentContainer: the container the component will be placed in
	"""
	def createComponent(self, parentContainer):
		self.checkBox = cmds.checkBox(parent= parentContainer, w=500, l=self.description)
		return self.checkBox
		
	"""
	@returns: the state of the checkbox as a string boolean (false/true)
	"""
	def getValue(self):
		if cmds.checkBox(self.checkBox, query = True, value=True):
			return "true"
		return "false"
	"""
	Sets the state of the checkbox
	@param value: a string boolean (false/true)
	"""
	def setValue(self, value):
		v = False
		if value == "true":
			v = True
		cmds.checkBox(self.checkBox, edit = True, value=v)
		
	"""
	Enables/disables the check box
	@param enabled: true if the component should be enabled.
	"""
	def enable(self, enabled):
		cmds.checkBox(self.checkBox, edit=True, en=enabled)
		
"""
Small little helper function that converts a string to int (even if it's a float string)	
@param str: the string to convert to an int
@return: an int value
"""
def getIntValue(str):
	try:
		return int(str)
	except ValueError:
		return int(float(str))	
		
"""
Class for an integer range slider
"""
class IntRangeData(KeyModifier):
	def __init__(self, xmlElement):
		KeyModifier.__init__(self, xmlElement)
		self.min = getIntValue(xmlElement.get("min"))
		self.max = getIntValue(xmlElement.get("max"))
	

	"""
	Creates the slider control
	@param parentContainer: the container the component will be placed in
	"""
	def createComponent(self, parentContainer):
		self.slider = cmds.intSliderGrp(parent= parentContainer, field=True, label=self.description, minValue=self.min, maxValue=self.max)
		return self.slider
		
	"""
	@returns: the state of the slider as a string
	"""
	def getValue(self):
		return str(cmds.intSliderGrp(self.slider, query = True, value=True))
		
	"""
	Sets the state of the slider
	@param value: a string that is an int or a float
	"""
	def setValue(self, value):
		cmds.intSliderGrp(self.slider, edit = True, value=getIntValue(value))
				
	"""
	Enables/disables the slider
	@param enabled: true if the component should be enabled.
	"""
	def enable(self, enabled):
		cmds.intSliderGrp(self.slider, edit=True, en=enabled)
		
		
"""
Class for an float range slider
"""
class FloatRangeData(KeyModifier):
	def __init__(self, xmlElement):
		KeyModifier.__init__(self, xmlElement)
		self.min = float(xmlElement.get("min"))
		self.max = float(xmlElement.get("max"))
	
	"""
	Creates the slider control
	@param parentContainer: the container the component will be placed in
	"""
	def createComponent(self, parentContainer):
		self.slider = cmds.floatSliderGrp(parent= parentContainer, field=True, label=self.description, minValue=self.min, maxValue=self.max)
		return self.slider
		
	"""
	@returns: the state of the slider as a string
	"""
	def getValue(self):
		return str(cmds.floatSliderGrp(self.slider, query = True, value=True))
		
	"""
	Sets the state of the slider
	@param value: a string that is an int or a float
	"""
	def setValue(self, value):
		cmds.floatSliderGrp(self.slider, edit = True, value=getIntValue(value))
				
	"""
	Enables/disables the slider
	@param enabled: true if the component should be enabled.
	"""
	def enable(self, enabled):
		cmds.intSliderGrp(self.slider, edit=True, en=enabled)
		