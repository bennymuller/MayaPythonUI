from time import gmtime, strftime
import texturecollection
import materialcollection
import objectcollection
reload (texturecollection)
reload (materialcollection)
reload (objectcollection)

from texturecollection import *
from materialcollection import *
from objectcollection import *

class SimplygonJob:
	def __init__(self):		
		self._directives = None
		self._succesful = False
		self._time = strftime("%H:%M:%S", gmtime())
		self._textureCollection = None
		self._materialCollection = None
		self._objectCollection = None
		
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
		self._textureCollection = TextureCollection()
		self._materialCollection = MaterialCollection()
		self._objectCollection = ObjectCollection()
		self._textureCollection.takeSnapShot()
		self._materialCollection.takeSnapShot()
		self._objectCollection.takeSnapShot()
		
	def getDiff(self, before, after):
		diff = []
		for item in after:
			if item not in before:
				diff.append(item)	
		return diff
		
	def end(self):
		self._textureCollection.calculateDiff()
		self._materialCollection.calculateDiff(self._textureCollection)
		self._objectCollection.calculateDiff(self._materialCollection)

			
	def findConnectedMaterials(self, texture):
		sgInfo = cmds.listConnections(texture)
		print "----"+texture+"----"
		print sgInfo
		

	def getLODs(self):
		return self._objectCollection.getLODs()

		
	def makeLayers(self):
		lods = self._objectCollection.getLODs()
		for lod in lods:
			layer = cmds.createDisplayLayer(empty=True, n="LOD"+str(lod))
			cmds.editDisplayLayerMembers(layer, lods[lod].objectNames) 
	
	def pruneTexturesAndMaterials(self):
		self._materialCollection.rerouteMaterials()
		self._objectCollection.rerouteObjects()
		self._textureCollection.deleteDuplicates()
		self._materialCollection.deleteDuplicates()
		
		
	def splitLODs(self):
		self._objectCollection.splitLODs()
	
	def moveTextures(self, directory):
		if directory == None or directory == "":
			raise RuntimeError("No directory specified to move textures to")

		self._textureCollection.moveTextures(directory)

	def rename(self, replaceString, newString):
		#Not yet implemented. Should allow to rename objects, materials, textures by replacing parts of their names. 
		pass
		
	def removeInvalidAssets(self):
		self._objectCollection.removeInvalidAssets()
		self._textureCollection.removeInvalidAssets()
		self._materialCollection.removeInvalidAssets()
		
	def isEmpty(self):	
		return False
		
	@property	
	def succesful(self):
		return self._succesful		
	@succesful.setter
	def succesful(self, isSuccess):
		self._succesful = isSuccess	