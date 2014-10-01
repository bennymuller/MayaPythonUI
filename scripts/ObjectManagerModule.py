import maya.cmds as cmds
import sys
from MaterialManagerModule import *

def getMaterialAndAttribute(attrString):
	attrIndex = attrString.rfind('.')
	return (attrString[:attrIndex],attrString[attrIndex+1:])

class ShadingEngineMaterialConnection:
	def __init__(self, materialAttribute, materialData, shadingEngineAttribute, shadingEngine):
		self._materialAttribute = materialAttribute
		self._materialData = materialData
		self._shadingEngineAttribute = shadingEngineAttribute
		self._shadingEngine = shadingEngine
		
	@property
	def materialAttribute(self):
		return self._materialAttribute

	@property
	def materialData(self):
		return self._materialData

	@property
	def shadingEngineAttribute(self):
		return self._shadingEngineAttribute

	@property
	def shadingEngine(self):
		return self._shadingEngine

SURFACESHADERATTR = 'surfaceShader'
class ShapeData:
	def __init__(self, shapeName, materialManager):
		shadingEngines = cmds.listConnections(shapeName, type='shadingEngine')
		self._shapeName = shapeName
		self._materialConnections = []
		if shadingEngines != None:
			for se in shadingEngines:
				materialAttribute = cmds.connectionInfo(se+'.'+SURFACESHADERATTR, sfd=True)
				matAndAttr = getMaterialAndAttribute(materialAttribute)
				materialData = materialManager.getMaterialData(matAndAttr[0])
				if materialData != None:
					self._materialConnections.append(ShadingEngineMaterialConnection(matAndAttr[1], materialData, SURFACESHADERATTR, se))
	
	def reconnectShape(self, materialManager):
		for mc in self._materialConnections:
			newMaterial = materialManager.redirectTo(mc.materialData)
			if newMaterial:
				cmds.disconnectAttr(mc.materialData.name+"."+mc.materialAttribute, mc.shadingEngine+"."+mc.shadingEngineAttribute) 		
				cmds.connectAttr(newMaterial.name+"."+mc.materialAttribute, mc.shadingEngine+"."+mc.shadingEngineAttribute, f=True)

	@property
	def materialNames(self):
		materialNames = []
		for mc in self._materialConnections:
			materialNames.append(mc.materialData.name)
		return materialNames
		
	@property
	def textureNames(self):
		textureNames = []
		for mc in self._materialConnections:
			textureNames.extend(mc.materialData.textureNames)
		return textureNames		

	def removeInvalidConnections(self):
		toRemove = []
		for mc in self._materialConnections:
			if not cmds.objExists(mc.materialData.name):
				toRemove.append(mc)
		for mc in toRemove:			
			self._materialConnections.remove(mc)			
				
LOD_KEYWORD = '_LOD'		
class ObjectData:
	def __init__(self, objectName, materialManager):
		shapeNames = cmds.listRelatives(objectName, path=True)
		self._shapes = []
		self._objectName = objectName
		lodStrIndex = objectName.rfind(LOD_KEYWORD)
		if lodStrIndex != -1:
			self._LODNum = int(objectName[lodStrIndex+len(LOD_KEYWORD):])
		else:
			self._LODNum = -1
		if shapeNames != None:
			for s in shapeNames:
				self._shapes.append(ShapeData(s, materialManager))
			
	def reconnectObject(self, materialManager):
		for s in self._shapes:
			s.reconnectShape(materialManager)
	
	@property
	def LODNum(self):
		return self._LODNum

	@property
	def name(self):
		return self._objectName
		
	@property
	def materialNames(self):
		materialNames = []
		for s in self._shapes:
			materialNames.extend(s.materialNames)
		return materialNames
		
	@property
	def textureNames(self):
		textureNames = []
		for s in self._shapes:
			textureNames.extend(s.textureNames)
		return textureNames	

	def removeInvalidConnections(self):
		for s in self._shapes:
			s.removeInvalidConnections()

class LODData:
	def __init__(self,index):
		self._objectData = []
		self._index = index
		
	def addObject(self,obj):
		self._objectData.append(obj)

	@property
	def objectNames(self):
		objectNames = []
		for o in self._objectData:
			objectNames.append(o.name)
		return objectNames

	@property
	def materialNames(self):
		materialNames = []
		for o in self._objectData:
			materialNames.extend(o.materialNames)
		return materialNames
		
	@property
	def textureNames(self):
		textureNames = []
		for o in self._objectData:
			textureNames.extend(o.textureNames)
		return textureNames
		
	def splitOut(self):
		objs = self.objectNames
		bbox = cmds.exactWorldBoundingBox(objs)
		for n in objs:
			objAttr = n+".translateX"
			translate = (self._index+1)*((bbox[3]-bbox[0])*1.1)
			cmds.setAttr(objAttr, lock=False)
			cmds.setAttr(objAttr, translate)

		
class ObjectManager:
	def __init__(self):
		self._objectData = []
		self._materialManager = None
	
	def initJob(self):
		self.objects = cmds.ls( type='transform', l=True)
		
	def jobDone(self, materialManager):
		self._materialManager = materialManager
		# Time to find out which objects were added
		objectsNow = cmds.ls( type='transform', l=True)
		for o in objectsNow:
			if o not in self.objects:
				self._objectData.append(ObjectData(o, self._materialManager))
		self.buildLods()
		
	def reconnectObjects(self):
		for o in self._objectData:
			o.reconnectObject(self._materialManager)
			
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

	def splitLODs(self):
		for l in self._LODs:
			self._LODs[l].splitOut()
			
	def getLODs(self):
		return self._LODs
		
	def removeInvalidAssets(self):
		toRemove = []
		for od in self._objectData:
			if not cmds.objExists(od.name):
				toRemove.append(od)
				print "REmoving: "+od
			else:
				od.removeInvalidConnections()
		for od in toRemove:			
			self._objectData.remove(od)	
		# We need to rebuild the LOD data
		self.buildLods()
	