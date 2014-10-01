import maya.cmds as cmds
import maya.mel as mel
from time import gmtime, strftime
import TextureManagerModule
import MaterialManagerModule
import ObjectManagerModule
reload (TextureManagerModule)
reload (MaterialManagerModule)
reload (ObjectManagerModule)

from TextureManagerModule import *
from MaterialManagerModule import *
from ObjectManagerModule import *

class ProcessDirectives:
	def __init__(self):
		self._batchMode = False
		self._settingFile = ""
		self._useWeights = False
		self._colorSet = ""
		self._weightMultiplier = 1
	
	@property
	def useWeights(self):
		return self._useWeights
	@useWeights.setter
	def useWeights(self, enabled):
		self._useWeights = enabled		

	@property
	def settingFile(self):
		return self._settingFile
	@settingFile.setter
	def settingFile(self, filePath):
		self._settingFile = filePath

	@property
	def batchMode(self):
		return self._batchMode
	@batchMode.setter
	def batchMode(self, enabled):
		self._batchMode = enabled

	@property
	def colorSet(self):
		return self._colorSet
	@colorSet.setter
	def colorSet(self, setName):
		self._colorSet = setName

	@property	
	def weightMultiplier(self):
		return self._weightMultiplier		
	@weightMultiplier.setter
	def weightMultiplier(self, multiplier):
		self._weightMultiplier = multiplier

	
		
class SimplygonJob:
	def __init__(self):		
		self._directives = None
		self._succesful = False
		self._time = strftime("%H:%M:%S", gmtime())
		self._textureManager = None
		self._materialManager = None
		self._objectManager = None
		
	@property
	def time(self):
		return self._time
		
	@property
	def	name(self):
		# Time will suffice as description for now
		return self.time
		
	@property
	def directives(self):
		return self._directives
	@directives.setter
	def directives(self, settings):
		self._directives = settings
		
	def start(self):
		self._textureManager = TextureManager()
		self._materialManager = MaterialManager()
		self._objectManager = ObjectManager()
		self._textureManager.initJob()
		self._materialManager.initJob()
		self._objectManager.initJob()
		
	def getDiff(self, before, after):
		diff = []
		for item in after:
			if item not in before:
				diff.append(item)	
		return diff
		
	def end(self):
		self._textureManager.jobDone()
		self._materialManager.jobDone(self._textureManager)
		self._objectManager.jobDone(self._materialManager)

			
	def findConnectedMaterials(self, texture):
		sgInfo = cmds.listConnections(texture)
		print "----"+texture+"----"
		print sgInfo
		

	def getLODs(self):
		return self._objectManager.getLODs()

		
	def makeLayers(self):
		lods = self._objectManager.getLODs()
		for lod in lods:
			layer = cmds.createDisplayLayer(empty=True, n="LOD"+str(lod))
			cmds.editDisplayLayerMembers(layer, lods[lod].objectNames) 
	
	def pruneTexturesAndMaterials(self):
		self._materialManager.reconnectMaterials()
		self._objectManager.reconnectObjects()
		self._textureManager.deleteDuplicates()
		self._materialManager.deleteDuplicates()
		
		
	def splitLODs(self):
		self._objectManager.splitLODs()
	
	def moveTextures(self, destinationFolder):
		pass

	def setPrefix(self, prefix):
		pass
		
	def removeInvalidAssets(self):
		self._objectManager.removeInvalidAssets()
		self._textureManager.removeInvalidAssets()
		self._materialManager.removeInvalidAssets()
		
	def isEmpty(self):	
		return False
		
	@property	
	def succesful(self):
		return self._succesful		
	@succesful.setter
	def succesful(self, isSuccess):
		self._succesful = isSuccess		
		
class SimplygonProcessor:
	def __init__(self):		
		self.history = []
	
	def process(self, directives):
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
		self.history.append(job)
		return job