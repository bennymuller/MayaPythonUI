import ConfigParser
import maya.cmds as cmds
import inspect, os
import xml.etree.ElementTree as etree
import view.keymodifier
reload(view.keymodifier)
from view.keymodifier import *

"""
Class that contains data about a section in the settings XML. It can also generate for the interface. 
"""
class SectionData:
	def __init__(self, xmlElement, indentLevel):
		self.description = xmlElement.get("description")
		self.children = []
		self.indentLevel = indentLevel
		# Read all the sub sections and sub keys in this section.
		for child in xmlElement: 
			if child.tag == 'Key':
				type = child.get("type")
				if type == "Droplist":
					self.children.append(DropListData(child))	
				elif type == "Checkbox":
					self.children.append(CheckBoxData(child))	
				elif type == "IntRange":
					self.children.append(IntRangeData(child))	
				elif type == "FloatRange":
					self.children.append(FloatRangeData(child))	
			elif child.tag == 'Section':
				self.children.append(SectionData(child, indentLevel+1))
				
	"""
	Creates the user interface for this section.
	@param parentContainer: the container to put the UI elements in.
	@return: the UI layout
	"""
	def createComponent(self, parentContainer):
		font = "boldLabelFont"
		if self.indentLevel >= 1:
			font = "tinyBoldLabelFont"
		layout = cmds.frameLayout(parent= parentContainer, l=self.description, collapsable=True, collapse=True, li=self.indentLevel*10, font=font)
		for child in self.children:
			#Add some air between the keys
			if not isinstance(child, SectionData):
				cmds.separator(parent= layout, height=1, style="none")
			child.createComponent(layout)
		#Add som air between the components
		cmds.separator(parent= layout, height=1, style="none")
		return layout

		
	"""
	Enables/disables this section
	@param enabled: true if the component should be enables
	"""
	def enable(self, enabled):
		for child in self.children:
			child.enable(enabled)

	"""
	@return: a list of all keys in this section and it's subsections
	"""
	def getKeys(self):
		keys = []
		for child in self.children:
			if isinstance(child, SectionData):
				keys.extend(child.getKeys())			
			else:
				keys.append(child)	
		return keys
			
"""
 Data container class that keeps track of the setting files and the exposed sections.
"""		
class SettingData:
	def __init__(self, xmlElement, basePath, id):
		self._file = xmlElement.get("file")
		self._name = xmlElement.get("name")
		self._id = id
		if not os.path.isabs(self._file):
			self._file = basePath+"/"+self._file
		if not os.path.isfile(self._file):
			print "Warning: The file "+self._file+" referenced in "+self.name+" could not be found."
		self._sections = []
		for section in xmlElement.findall('Section'):
			self._sections.append(SectionData(section,0))
			
	@property
	def id(self):
		return self._id

	@property
	def settingsFile(self):
		return self._file

	@property
	def sections(self):
		return self._sections

	@property
	def name(self):
		return self._name
		
		
"""
Class that managing the setting files, exposing variables and creating a setting file before optimization
"""	
class OptimizationSettingsManager:
	def __init__(self, xmlFile):
		tree = etree.parse(xmlFile)
		root = tree.getroot()
		self.settingDatas = []
		self.currentContainer = None
		self.currentConfig = None
		self.currentSetting = None
		basePath = os.path.dirname(xmlFile).replace("\\", "/")
		settingID = 0
		for settingData in root.findall('Setting'):
			self.settingDatas.append(SettingData(settingData, basePath,settingID))
			settingID+=1

	"""
	@return: the list of setting datas of all the available settings files
	"""			
	def getSettings(self): 
		return self.settingDatas
		
	"""
	@return: the setting data of the setting matching the input ID
	"""	
	def getSetting(self, settingID):
		return self.settingDatas[settingID]
		
	"""
	Enables/disables all the components in the optimization panel
	@param enabled: true if the component should be enables
	"""
	def enable(self, enabled):
		for section in self.currentSetting.sections:
			section.enable(enabled)		
			
	"""
	When the selected setting is changed this function should be called to update the whole optimization panel.
	Loads the configuration for the selected setting file.
	Creates the components for the exposed keys and adds them to the container.
	Sets default values for the keys.
	@param container: the container to place all UI elements in.
	@param selectedSettingID: the id of the newly selected setting.
	"""
	def settingChanged(self, container, selectedSettingID):
		settingData = self.getSetting(selectedSettingID)
		# Load the configuration file
		self.currentConfig = self.loadConfigurationFile(settingData.settingsFile)
		self.clear()
		# Create the components that are exposed through the xml
		self.currentSetting = settingData
		self.currentContainer = cmds.columnLayout (parent= container, adjustableColumn = True)
		if selectedSettingID != None:
			sections = settingData.sections
			for section in sections:
				section.createComponent(self.currentContainer)
		
		self.setDefaultValues()

	"""
	Removes all UI components from the interfaces
	"""
	def clear(self):
		#Clear the current interface
		if self.currentContainer != None:
			cmds.deleteUI(self.currentContainer)
		
	"""
	Loads the .ini file
	@param configFile: the .ini file to load
	@returns: a ConfigParser.RawConfigParser containing the .ini data
	"""
	def loadConfigurationFile(self, configFile):
		config = ConfigParser.RawConfigParser()
		config.read(configFile)
		return config

	"""
	Writes a config file into the provided path that contains the settings from the loaded .ini file with 
	the settings overriden by the user merged in.
	@param outFile: the file to write the config to
	"""
	def writeTempConfig(self, outFile):
		#Before we write the file we must transfer the user specified values to the config.
		for section in self.currentSetting.sections:
			keys = section.getKeys()
			for key in keys:
				name = key.getKeyName()				
				section = key.getKeySection()
				if self.currentConfig.has_option(section, name):
					value = key.getValue()
					self.currentConfig.set(section, name,value)
				else:
					print "Warning! The key: "+section+"/"+name+" does not exist in the config file! Check the xml description for the settings file: "+self.currentSetting.name		
		self.currentConfig.write(outFile)
		
	"""
	Loops through all the keys in the current setting and sets the default values from the loaded config.
	"""
	def setDefaultValues(self):
		for section in self.currentSetting.sections:
			keys = section.getKeys()
			for key in keys:
				name = key.getKeyName()				
				section = key.getKeySection()
				if self.currentConfig.has_option(section, name):
					value = self.currentConfig.get(section, name)
					key.setValue(value)
				else:
					print "Warning! The key: "+section+"/"+name+" does not exist in the config file! Check the xml description for the settings file: "+self.currentSetting.settingName 