import maya.cmds as cmds
import sys
from materialcollection import *
import utils.mutils as mutils


"""
Stores the information about a connection between a shading engine and a material
"""
class ShadingEngineMaterialConnection:
	"""
	Constructor
	@param materialAttribute: the attribute on the material connected to the shader
	@param materialData: the data describing the connected material
	@param shadingEngineAttribute: the attribute on the shader connected to the material
	@param shadingEngine: the shader
	"""
	def __init__(self, materialAttribute, materialData, shadingEngineAttribute, shadingEngine):
		self._materialAttribute = materialAttribute
		self._materialData = materialData
		self._shadingEngineAttribute = shadingEngineAttribute
		self._shadingEngine = shadingEngine
		
	"""
	Returns the attribute on the material
	"""
	@property
	def materialAttribute(self):
		return self._materialAttribute

	"""
	Returns the data describing the connected material
	"""	
	@property
	def materialData(self):
		return self._materialData

	"""
	Returns the attribute on the shader that is connected to the material
	"""
	@property
	def shadingEngineAttribute(self):
		return self._shadingEngineAttribute

	"""
	Returns the shader name
	"""
	@property
	def shadingEngine(self):
		return self._shadingEngine

	"""
	Reroutes the shapes material connection to a new material if needed.
	@param materialCollection: the collection of all materials
	"""
	def rerouteShape(self, materialCollection):
		newMaterial = materialCollection.redirectTo(self.materialData)
		if newMaterial:
			# The current material needs to be replaced. Disconnect that one and connect the shader to the new material.
			mutils.moveConnection(self.materialData.name+"."+self.materialAttribute, newMaterial.name+"."+self.materialAttribute, self.shadingEngine+"."+self.shadingEngineAttribute)
			self._materialData = newMaterial

SURFACESHADERATTR = 'surfaceShader'
"""
The data about a shape in an object
"""
class ShapeData:
	"""
	Constructor
	@param shapeName: the name of this shape
	@param materialCollection: the collection of all materials 
	"""
	def __init__(self, shapeName, materialCollection):
		shadingEngines = cmds.listConnections(shapeName, type='shadingEngine')
		self._shapeName = shapeName
		self._materialConnections = []
		if shadingEngines != None:
			for se in shadingEngines:
				materialAttribute = cmds.connectionInfo(se+'.'+SURFACESHADERATTR, sfd=True)
				matAndAttr = mutils.getObjectAndAttribute(materialAttribute)
				materialData = materialCollection.getMaterialData(matAndAttr[0])
				if materialData != None:
					self._materialConnections.append(ShadingEngineMaterialConnection(matAndAttr[1], materialData, SURFACESHADERATTR, se))
	
	"""
	Will reroute all shaders in this shape to new materials if needed.
	@param materialCollection: the collection of all materials 	
	"""
	def rerouteShape(self, materialCollection):
		for mc in self._materialConnections:
			mc.rerouteShape(materialCollection)			

	"""
	Returns the names of all materials connected to this shape
	"""
	@property
	def materialNames(self):
		materialNames = []
		for mc in self._materialConnections:
			materialNames.append(mc.materialData.name)
		return materialNames
		
	"""
	Returns the names of all textures connected to this shape
	"""
	@property
	def textureNames(self):
		textureNames = []
		for mc in self._materialConnections:
			textureNames.extend(mc.materialData.textureNames)
		return textureNames		

	"""
	Cleans out any connections to materials that does not exist any more.
	"""
	def removeInvalidConnections(self):
		toRemove = []
		for mc in self._materialConnections:
			if not cmds.objExists(mc.materialData.name):
				toRemove.append(mc)
		for mc in toRemove:			
			self._materialConnections.remove(mc)			
				
LOD_KEYWORD = '_LOD'
"""
Contains data about an object
"""		
class ObjectData:
	"""
	Constructor.
	@param objectName: name of this object
	@param materialCollection: the collection of all materials
	"""
	def __init__(self, objectName, materialCollection):
		#Find all connected shapes
		shapeNames = cmds.listRelatives(objectName, path=True)
		self._shapes = []
		self._objectName = objectName
		#Which lod is this part of?
		lodStrIndex = objectName.rfind(LOD_KEYWORD)
		if lodStrIndex != -1:
			self._LODNum = int(objectName[lodStrIndex+len(LOD_KEYWORD):])
		else:
			self._LODNum = -1
		#Create shapes data for all connected shapes
		if shapeNames != None:
			for s in shapeNames:
				self._shapes.append(ShapeData(s, materialCollection))
			
	"""
	Reroutes all the connections to materials in subshapes
	@param materialCollection: the collection of all materials
	"""
	def rerouteObject(self, materialCollection):
		for s in self._shapes:
			s.rerouteShape(materialCollection)
	
	"""
	Returns the LOD index of this object
	"""
	@property
	def LODNum(self):
		return self._LODNum

	"""
	Returns the name of this object
	"""
	@property
	def name(self):
		return self._objectName
		
	"""
	Returns the names of all materials connected to this object
	"""
	@property
	def materialNames(self):
		materialNames = []
		for s in self._shapes:
			materialNames.extend(s.materialNames)
		return materialNames
		
	"""
	Returns the names of all textures connected to this object
	"""
	@property
	def textureNames(self):
		textureNames = []
		for s in self._shapes:
			textureNames.extend(s.textureNames)
		return textureNames	

	"""
	Removes any invalid connections to materials in this object
	"""
	def removeInvalidConnections(self):
		for s in self._shapes:
			s.removeInvalidConnections()

"""
Stores information about all the objects within a lod index
"""
class LODData:
	"""
	Constructor
	@param index: the index of this LOD data
	"""
	def __init__(self,index):
		self._objectData = []
		self._index = index
		
	"""
	Adds an object to this LOD.
	@param obj: the object to add to this LOD
	"""
	def addObject(self,obj):
		self._objectData.append(obj)

	"""
	Returns the names of all the objects in this LOD
	"""
	@property
	def objectNames(self):
		objectNames = []
		for o in self._objectData:
			objectNames.append(o.name)
		return objectNames

	"""
	Returns the names of all the materials in this LOD
	"""
	@property
	def materialNames(self):
		materialNames = []
		for o in self._objectData:
			materialNames.extend(o.materialNames)
		return materialNames
		
	"""
	Returns the names of all the textures in this LOD
	"""
	@property
	def textureNames(self):
		textureNames = []
		for o in self._objectData:
			textureNames.extend(o.textureNames)
		return textureNames
		
	"""
	Translates this LOD out in x direction to break LODs apart.
	"""
	def splitOut(self):
		objs = self.objectNames
		bbox = cmds.exactWorldBoundingBox(objs)
		for n in objs:
			objAttr = n+".translateX"
			translate = (self._index+1)*((bbox[3]-bbox[0])*1.1)
			cmds.setAttr(objAttr, lock=False)
			cmds.setAttr(objAttr, translate)

"""
Contains all the objects that was created during a SImplygon job.
"""		
class ObjectCollection:
	def __init__(self):
		self._objectData = []
		self._materialCollection = None
	
	"""
	Takes a snapshot of the objects in the scene as it is right now.
	"""
	def takeSnapShot(self):
		self.objects = cmds.ls( type='transform', l=True)
	
	"""
	Compares the objects in the current scene with the snapshot and stores a objects data for all
	objects that has been added to the scene.
	@param materialCollection: the collection of all materials. Used to link objects to the correct material datas.
	"""	
	def calculateDiff(self, materialCollection):
		self._materialCollection = materialCollection
		# Time to find out which objects were added
		objectsNow = cmds.ls( type='transform', l=True)
		for o in objectsNow:
			if o not in self.objects:
				self._objectData.append(ObjectData(o, self._materialCollection))
		self.buildLods()
	
	"""
	Rerouts all connections in objects to new materials if needed.
	"""
	def rerouteObjects(self):
		for o in self._objectData:
			o.rerouteObject(self._materialCollection)
	
	"""
	Breaks the objects into LODs according to their LOD number
	"""
	def buildLods(self):
		# Since there can be several jobs in one scene, LOD numbers can grow. We need to find the lowest num in this scene.
		lowestLODNum = sys.maxint
		for o in self._objectData:
			if o.LODNum != -1 and o.LODNum < lowestLODNum:
				lowestLODNum = o.LODNum
		self._LODs = {}
		for o in self._objectData:
			if o.LODNum != -1:
				lodIndex = o.LODNum-lowestLODNum
				if lodIndex not in self._LODs:
					self._LODs[lodIndex] = LODData(lodIndex)
				lodData = self._LODs[lodIndex]
				lodData.addObject(o)

	"""
	Translates the LODs out to break them apart.
	"""
	def splitLODs(self):
		for l in self._LODs:
			self._LODs[l].splitOut()
			
	"""
	Returns a list of all the lods
	"""
	def getLODs(self):
		return self._LODs
	
	"""
	Removes any invalid object or connections in the object collection.
	"""	
	def removeInvalidAssets(self):
		toRemove = []
		for od in self._objectData:
			if not cmds.objExists(od.name):
				toRemove.append(od)
			else:
				od.removeInvalidConnections()
		for od in toRemove:			
			self._objectData.remove(od)	
		# We need to rebuild the LOD data
		self.buildLods()
	