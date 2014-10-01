import maya.cmds as cmds
from itertools import tee, izip
from TextureManagerModule import *

def pairwise(iterable):
    a = iter(iterable)
    return izip(a, a)

def getAttribute(attrString):
	attrIndex = attrString.rfind('.')
	return attrString[attrIndex+1:]

targetsToIgnore = ['defaultTextureList', 'place2dTexture']
class MaterialTextureConnection:
	def __init__(self, materialAttribute, textureData, textureAttribute):
		self._materialAttribute = materialAttribute
		self._textureData = textureData
		attrIndex = textureAttribute.rfind('.')
		self._textureAttribute = getAttribute(textureAttribute)
		textureData.materialConnection = self
	
	@property
	def texture(self):
		return self._textureData
		
	def copyConnections(self, newTexture):	
		cons = cmds.listConnections(self._textureData.name, c=True)
		for sourceAttr, target in pairwise(cons):
			attribute = getAttribute(sourceAttr)
			targetType = cmds.objectType(target)
			if targetType not in targetsToIgnore:
				destinationAttributes = cmds.connectionInfo(sourceAttr,dfs=True)
				for da in destinationAttributes:
					cmds.disconnectAttr(sourceAttr,da) 		
					cmds.connectAttr(newTexture.name+"."+attribute,da, f=True)
							
	def reconnectTexture(self, textureManager):
		#Check if the current texture should be redirected
		newTexture = textureManager.redirectTo(self._textureData)
		if newTexture != None:
			cmds.disconnectAttr(self._textureData.name+"."+self._textureAttribute,self._materialAttribute) 		
			cmds.connectAttr(newTexture.name+"."+self._textureAttribute,self._materialAttribute, f=True)
			self.copyConnections(newTexture)
			self._textureData = newTexture

def getConnectedAttribute(attribute, isSource):
	if isSource:
		connectedAttribute = cmds.connectionInfo(attribute,dfs=True)
	else:
		connectedAttribute = cmds.connectionInfo(attribute,sfd=True)
	if connectedAttribute != None and isinstance(connectedAttribute, list):
		if len(connectedAttribute) > 1:
			print "Unexpectedly found several connections for the attribute: "+attribute				
			#TODO: Exception handling
		connectedAttribute = connectedAttribute[0]
	return connectedAttribute
		
class MaterialData:
	def __init__(self, materialName, textureManager):
		self._name = materialName
		self._textureConnections = []
		# List all directly connected textures
		matType = cmds.objectType(materialName)
		cons = cmds.listConnections(materialName, type="file", c=True)
		if cons != None:
			for attribute, texture in pairwise(cons):
				# Find the source attribute on the texture in the connection
				textureSourceAttribute = getConnectedAttribute(attribute,False)
				textureData = textureManager.getTextureData(texture)
				if textureData == None:
					print "Something has gone wrong as we couldn't find the texture data: "+texture+" for: "+materialName
				else:			
					# Tuple of attributes in the texture that is connected to the material data
					self._textureConnections.append(MaterialTextureConnection(attribute, textureData, textureSourceAttribute))
		# Check if there is a normal map
		bumps = cmds.listConnections(materialName, type="bump2d")
		if bumps != None:
			for b in bumps:
				tCons = cmds.listConnections(b, type="file", c=True)
				if tCons != None:
					bumpAttribute = tCons[0]
					texture = tCons[1]
					textureData = textureManager.getTextureData(texture)
					if textureData == None:
						print "Something has gone wrong as we couldn't find the texture data: "+texture+" for: "+materialName
					ot = cmds.objectType(b)
					textureSourceAttribute = getConnectedAttribute(bumpAttribute,False)
					self._textureConnections.append(MaterialTextureConnection(tCons[0], textureData, textureSourceAttribute))
			
	@property
	def name(self):
		return self._name
			
	@property
	def texturesConnections(self):
		return self._textureConnections
		
	@property
	def textureNames(self):
		textureNames = []
		for tc in self._textureConnections:
			textureNames.append(tc.texture.name)
		return textureNames		
		
	def isEqual(self, material2):
		for t1 in self.texturesConnections:
			exists = False
			for t2 in material2.texturesConnections:
				if t1.texture.isEqual(t2.texture):
					exists = True
			if not exists:
				return False
		for t1 in material2.texturesConnections:
			exists = False
			for t2 in self.texturesConnections:
				if t1.texture.isEqual(t2.texture):
					exists = True
			if not exists:
				return False
		return True
	
	def reconnectTextures(self, textureManager):
		for tc in self._textureConnections:
			tc.reconnectTexture(textureManager)
			
	def removeInvalidConnections(self):
		toRemove = []
		for tc in self._textureConnections:
			if not cmds.objExists(tc.texture.name):
				toRemove.append(tc)
		for tc in toRemove:			
			self._textureConnections.remove(tc)	

class MaterialManager:
	def __init__(self):
		self._materialData = []
		self._duplicates = []
		self._textureManager = None
	
	def initJob(self):
		self.materials = cmds.ls( materials=True)
		print self.materials
		
	def jobDone(self,textureManager):
		# Time to find out which materials were added
		self._textureManager = textureManager
		materialsNow = cmds.ls( materials=True)
		print materialsNow
		for m in materialsNow:
			if m not in self.materials:
				self._materialData.append(MaterialData(m, self._textureManager))
		self.calculateDuplicates()
	
	def calculateDuplicates(self):	
		self._duplicates = []
		for md in self._materialData:
			added = False
			for l in self._duplicates:
				if l[0].isEqual(md):
					l.append(md)
					added = True
			if not added:
				self._duplicates.append([md])
				
	def reconnectMaterials(self):
		for m in self._materialData:
			m.reconnectTextures(self._textureManager)

	def getMaterialData(self, name):
		for md in self._materialData:
			if md.name == name:
				return md
		return None

		
	def redirectTo(self, materialData):
		for l in self._duplicates:
			for i in range(1, len(l)):
				if l[i] == materialData:
					return l[0]
		#No need to replace the material
		return None
		
	def deleteDuplicates(self):
		#Loop over all the duplicates and delete all but one material in each bucket
		for l in self._duplicates:
			for i in range(1, len(l)):
				cmds.delete(l[i].name)
				self._materialData.remove(l[i])
		self._duplicates = []
		
	def removeInvalidAssets(self):
		toRemove = []
		for md in self._materialData:
			if not cmds.objExists(md.name):
				toRemove.append(md)
			else:
				md.removeInvalidConnections()
		for md in toRemove:			
			self._materialData.remove(md)

		# We need to update the list of duplicates
		self.calculateDuplicates()
