import ConfigParser
import maya.cmds as cmds
import inspect, os
import xml.etree.ElementTree as etree
import KeyModifierModule
reload(KeyModifierModule)
from KeyModifierModule import *

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
		layout = cmds.frameLayout(parent= parentContainer, l=self.description, collapsable=True, li=self.indentLevel*10, font=font)
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
	def __init__(self, xmlElement, basePath):
		self.file = xmlElement.get("file")
		self.name = xmlElement.get("name")
		if not os.path.isabs(self.file):
			self.file = basePath+"/"+self.file
		if not os.path.isfile(self.file):
			print "Warning: The file "+self.file+" referenced in "+self.name+" could not be found."
		print self.file
		self.sections = []
		for section in xmlElement.findall('Section'):
			self.sections.append(SectionData(section,0))

	"""
	@return: the file attribute of this setting data
	"""		
	def getSettingsFile(self):
		return self.file

	"""
	@return: a list of all sections in this setting data
	"""		
	def getSections(self):
		return self.sections;
		
		
"""
Class that managing the setting files, exposing variables and creating a setting file before optimization
"""	
class OptimizationSettingsManager:
	def __init__(self, xmlFile):
		tree = etree.parse(xmlFile)
		root = tree.getroot()
		self.settingDatas = {}
		self.currentContainer = None
		self.currentConfig = None
		self.currentSetting = ""
		basePath = os.path.dirname(xmlFile).replace("\\", "/")
		for settingData in root.findall('Setting'):
			if settingData.get("name") in self.settingDatas:
				print "Warning! The setting data "+settingData.get("name")+" is declared several times. Have you been sloppy-pasting?"
			self.settingDatas[settingData.get("name")] = SettingData(settingData, basePath)

	"""
	@return: a list of the names of all the available settings files
	"""			
	def getSettingNames(self): 
		settingNames = []
		for key in self.settingDatas:
			settingNames.append(key)
		return settingNames
		
	"""
	@return: the setting data of the setting matching the input name
	"""	
	def getSettingsFile(self, settingsName):
		return self.settingDatas[settingsName].getSettingsFile()

	"""
	@return: the the list of sections from the setting data matching the name
	"""	
	def getSections(self, settingName):
		return self.settingDatas[settingName].getSections()
		
	"""
	Enables/disables all the components in the optimization panel
	@param enabled: true if the component should be enables
	"""
	def enable(self, enabled):
		sections = self.getSections(self.currentSetting)
		for section in sections:
			section.enable(enabled)		
			
	"""
	When the selected setting is changed this function should be called to update the whole optimization panel.
	Loads the configuration for the selected setting file.
	Creates the components for the exposed keys and adds them to the container.
	Sets default values for the keys.
	@param container: the container to place all UI elements in.
	@param selectedSettingName: the name of the newly selected setting.
	"""
	def settingChanged(self, container, selectedSettingName):
		# Load the configuration file
		self.currentConfig = self.loadConfigurationFile(self.getSettingsFile(selectedSettingName))

		#Clear the current interface
		if self.currentContainer != None:
			cmds.deleteUI(self.currentContainer)
	
		# Create the components that are exposed through the xml
		self.currentSetting = selectedSettingName
		self.currentContainer = cmds.columnLayout (parent= container, adjustableColumn = True)
		if selectedSettingName != None:
			sections = self.getSections(selectedSettingName)
			for section in sections:
				section.createComponent(self.currentContainer)
		
		self.setDefaultValues()
	
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
		sections = self.getSections(self.currentSetting)
		for section in sections:
			keys = section.getKeys()
			for key in keys:
				name = key.getKeyName()				
				section = key.getKeySection()
				if self.currentConfig.has_option(section, name):
					value = key.getValue()
					self.currentConfig.set(section, name,value)
				else:
					print "Warning! The key: "+section+"/"+name+" does not exist in the config file! Check the xml description for the settings file: "+self.currentSetting 		
		self.currentConfig.write(outFile)
		
	"""
	Loops through all the keys in the current setting and sets the default values from the loaded config.
	"""
	def setDefaultValues(self):
		sections = self.getSections(self.currentSetting)
		for section in sections:
			keys = section.getKeys()
			for key in keys:
				name = key.getKeyName()				
				section = key.getKeySection()
				if self.currentConfig.has_option(section, name):
					value = self.currentConfig.get(section, name)
					key.setValue(value)
				else:
					print "Warning! The key: "+section+"/"+name+" does not exist in the config file! Check the xml description for the settings file: "+self.currentSetting 