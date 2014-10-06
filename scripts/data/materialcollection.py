import maya.cmds as cmds
import utils.mutils
reload (utils.mutils)
import utils.mutils as mutils
from texturecollection import *


targetsToIgnore = ['defaultTextureList', 'place2dTexture']
"""
Class that stores the information about a connection between a material and a texture.
"""
class MaterialTextureConnection:
	"""
	Constructor.
	@param materialAttribute: the attribute on the material involved in the connection (whole string, object and attribute)
	@param textureData: the data object for the connected texture
	@param textureAttribute: the attribute of the connected texture (whole string, object and attribute)
	"""
	def __init__(self, materialAttribute, textureData, textureAttribute):
		self._materialAttribute = materialAttribute
		self._textureData = textureData
		self._textureAttribute = mutils.getAttribute(textureAttribute)
	
	"""
	Returns the texture data of the connected texture
	"""
	@property
	def texture(self):
		return self._textureData

	"""
	Copies the connections from the current texture to the new tetxture.
	@param newTexture: the texture to copy all connnections to.
	"""
	def copyConnections(self, newTexture):	
		# List all connections from the current texture, with the target of the connection as well.
		cons = cmds.listConnections(self._textureData.name, c=True)
		for sourceAttr, target in mutils.pairwise(cons):
			# Get the name of the attribute 
			attribute = mutils.getAttribute(sourceAttr)
			# Get the object type of the connected object
			targetType = cmds.objectType(target)
			# Do not copy connection if the target is to be ignored
			if targetType not in targetsToIgnore:
				#Get the destination attributes on the target object.
				destinationAttributes = cmds.connectionInfo(sourceAttr,dfs=True)
				for da in destinationAttributes:
					#Disconnect the current texture and connect it to the new texture
					mutils.moveConnection(sourceAttr, newTexture.name+"."+attribute, da)
	
	"""
	Will re-route this materials connection to a new texture if needed.
	@param textureCollection: the collection of textures.
	"""	
	def rerouteConnection(self, textureCollection):
		#Check if the current texture should be redirected
		newTexture = textureCollection.redirectTo(self._textureData)
		if newTexture != None:
			# Disconnect the currently used texture and connect the new texture to this material
			mutils.moveConnection(self._textureData.name+"."+self._textureAttribute, newTexture.name+"."+self._textureAttribute, self._materialAttribute) 
			# Copy any other connections that might exit on this texture
			self.copyConnections(newTexture)
			# Set the new texture on this connection
			self._textureData = newTexture

"""
Class that contains all information about a material
"""		
class MaterialData:
	"""
	Constructor
	@param materialName: the name of this material
	@param textureCollection: the collection of all textures
	"""
	def __init__(self, materialName, textureCollection):
		self._name = materialName
		self._textureConnections = []
		# List all directly connected textures
		matType = cmds.objectType(materialName)
		cons = cmds.listConnections(materialName, type="file", c=True)
		if cons != None:
			for attribute, texture in mutils.pairwise(cons):
				# Find the source attribute on the texture in the connection
				textureSourceAttribute = mutils.getConnectedAttribute(attribute,False)
				textureData = textureCollection.getTextureData(texture)
				if textureData == None:
					raise ValueError("Something has gone wrong as we couldn't find the texture data: "+texture+" for: "+materialName)
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
					textureData = textureCollection.getTextureData(texture)
					if textureData == None:
						raise ValueError("Something has gone wrong as we couldn't find the bump texture data: "+texture+" for: "+materialName)
					textureSourceAttribute = mutils.getConnectedAttribute(bumpAttribute,False)
					self._textureConnections.append(MaterialTextureConnection(tCons[0], textureData, textureSourceAttribute))
	
	"""
	Returns the name of this material
	"""	
	@property
	def name(self):
		return self._name
			
	"""
	Returns the list of texture connections on this material
	"""
	@property
	def texturesConnections(self):
		return self._textureConnections
		
	"""
	Returns a list of names to the textures connected to this material
	"""
	@property
	def textureNames(self):
		textureNames = []
		for tc in self._textureConnections:
			textureNames.append(tc.texture.name)
		return textureNames		
		
	"""
	Returns true if this material is a duplicate of the incoming material. This is whenever the two materials are using the same
	textures, or textures that have the same hashvalue.
	@param material2: the material to compare this material to
	"""
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
	
	"""
	Will loop through all connections on this material and re-route all textures that are duplicates.
	@param textureCollection: the collection of textures
	"""
	def rerouteConnections(self, textureCollection):
		for tc in self._textureConnections:
			tc.rerouteConnection(textureCollection)
			
	"""
	Will remove any connections that are not valid anymore, i.e. pointing to objects that doesn't exist.
	"""
	def removeInvalidConnections(self):
		toRemove = []
		for tc in self._textureConnections:
			if not cmds.objExists(tc.texture.name):
				toRemove.append(tc)
		for tc in toRemove:			
			self._textureConnections.remove(tc)	

"""
A material collection contains all the material data that is created when a simplygon job is run.
Before starting a job you need to run takeSnapShot so that it can store all materials that exists before.
After a job is done you need to run calculateDiff so that the material collection is pruned to only the materials
that was created during the job. 
"""			
class MaterialCollection:
	def __init__(self):
		self._materialData = []
		self._duplicates = []
		self._textureCollection = None
	"""
	Takes a snapshot of the materials in the scene as it is right now.
	"""
	def takeSnapShot(self):
		self.snapShot = cmds.ls( materials=True)
	
	"""
	Compares the materials in the current scene with the snapshot and stores a material data for all
	materials that has been added to the scene.
	It will also calculate duplicates for easy removal.
	@param textureCollection: the collection of all textures. Used to link materials to the correct texture datas.
	"""	
	def calculateDiff(self,textureCollection):
		# Time to find out which materials were added
		self._textureCollection = textureCollection
		materialsNow = cmds.ls( materials=True)
		for m in materialsNow:
			if m not in self.snapShot:
				self._materialData.append(MaterialData(m, self._textureCollection))
		self.calculateDuplicates()
	
	"""
	Groups the newly created materials by duplicates. Can only been called after a snapshot and a diff
	has been made.
	"""
	def calculateDuplicates(self):	
		self._duplicates = []
		for md in self._materialData:
			added = False
			for l in self._duplicates:
				#The first material in the list is considered the base
				if l[0].isEqual(md):
					l.append(md)
					added = True
			if not added:
				self._duplicates.append([md])

	"""
	Reconnects all materials pointing to duplicate textures to new textures.
	"""	
	def rerouteMaterials(self):
		for m in self._materialData:
			m.rerouteConnections(self._textureCollection)

	"""
	@param name: name of the material to get the data for
	"""
	def getMaterialData(self, name):
		for md in self._materialData:
			if md.name == name:
				return md
		return None

	"""
	Returns the material data to relink the incoming data to if it's a duplicate and not the base material.
	If the incoming material is a base or not a duplicate, None will be returned.
	@param materialData: The material to check if it should be replaced
	"""	
	def redirectTo(self, materialData):
		for l in self._duplicates:
			for i in range(1, len(l)):
				if l[i] == materialData:
					return l[0]
		#No need to replace the material
		return None
		
	"""
	Deletes all materials that are duplicates for the scene. Should only be called after the objects have been 
	reconnected to new materials.
	"""
	def deleteDuplicates(self):
		#Loop over all the duplicates and delete all but one material in each bucket
		for l in self._duplicates:
			for i in range(1, len(l)):
				cmds.delete(l[i].name)
				self._materialData.remove(l[i])
		self._duplicates = []
		
	"""
	Removes any materials that doesn't exist in the scene anymore.
	"""
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
