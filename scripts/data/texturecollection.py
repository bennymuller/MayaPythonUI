import maya.cmds as cmds
import os
import shutil
import hashlib

"""
Will calculate the hash value for the incoming file using the defined hasher.
@param aFile: the file to calculate hashvalue for
@param hasher: the hasher to use
@return: the hash value for the file
"""
def hashfile(afile, hasher, blocksize=65536):
	buf = afile.read(blocksize)
	while len(buf) > 0:
		hasher.update(buf)
		buf = afile.read(blocksize)
	return hasher.digest()

"""
Class that contains the information about a texture.
"""
class TextureData:
	"""
	Construtor.
	@param textureName: the name for this texture
	"""
	def __init__(self, textureName):
		self._name = textureName
		self._materialConnection = None
		self._filePath = cmds.getAttr(textureName+'.fileTextureName')
		self._hash = hashfile(open(self._filePath , 'rb'), hashlib.sha256()) 
			
	"""
	Returns if this texture is equal or as the incoming texture. Either they're pointing the same file or
	the files have the same hash value.
	@param textureData: the texture to compare with
	@return: true if the textures are equal
	"""
	def isEqual(self, textureData):
		return self.name == textureData.name or self.filePath == textureData.filePath or self.hash == textureData.hash
	
	"""
	Returns the name of this texture
	"""
	@property
	def name(self):
		return self._name

	"""
	Returns the hash value of the texture file
	"""
	@property
	def hash(self):
		return self._hash

	"""
	Returns the path to the texture file
	"""	
	@property
	def filePath(self):
		return self._filePath

	"""
	Moves the texture file to directory and relinks the texture object
	@directory: the folder to move the texture file to
	"""
	def moveTo(self, directory):
		fileName = os.path.basename(os.path.realpath(self.filePath))
		destination = directory+"/"+fileName
		shutil.move(self.filePath, destination)
		self._filePath = destination
		cmds.setAttr(self.name+'.fileTextureName', self._filePath, type="string")

"""
Class that stores all textures generated in a simplygon job.
"""
class TextureCollection:
	def __init__(self):
		self._textureData = []
		self._duplicates = {}
	
	"""
	Takes a snapshot of the textures in the scene as it is right now.
	"""
	def takeSnapShot(self):
		self._textures = cmds.ls( textures=True)
		
	
	"""
	Compares the textures in the current scene with the snapshot and stores a texture data for all
	textures that has been added to the scene.
	It will also calculate duplicates for easy removal.
	"""	
	def calculateDiff(self):
		# Time to find out which textures were added
		texturesNow = cmds.ls( textures=True)
		for t in texturesNow:
			if t not in self._textures:
				self._textureData.append(TextureData(t))
		self.calculateDuplicates()

	"""
	Organizes the textures by hash value so that textures can be easily replaced.
	"""
	def calculateDuplicates(self):
		self._duplicates = {}
		#Group all textures by their hash value to sort out duplications
		for td in self._textureData:
			if(td.hash not in self._duplicates):
				self._duplicates[td.hash] = []
			self._duplicates[td.hash].append(td)

	"""
	Returns the texture with matching the incoming name.
	@param name: name of the texture to get
	"""	
	def getTextureData(self, name):
		for td in self._textureData:
			if td.name == name:
				return td
		return None

	"""
	Returns the texture data to relink the incoming data to if it's a duplicate and not the base texture.
	If the incoming texture is a base or not a duplicate, None will be returned.
	@param textureData: The texture to check if it should be replaced
	"""		
	def redirectTo(self, textureData):
		if textureData.hash in self._duplicates and len(self._duplicates[textureData.hash]) >1:
			replacement = self._duplicates[textureData.hash][0]
			if textureData.name != replacement:
				return replacement
		#No need to replace the texture
		return None
	
	"""
	Will clean out all the duplicate textures also deleting the files
	"""
	def deleteDuplicates(self):
		#Loop over all the duplicates and delete all but one texture in each bucket
		for hash in self._duplicates:
			tdList = self._duplicates[hash]
			for i in range(1, len(tdList)):
				td = tdList[i]
				cmds.delete(td.name)
				try:
					os.remove(td.filePath)
				except OSError:
					pass
				self._textureData.remove(td)
		self._duplicates = {}

	"""
	Will clear this collection of any textures that doesn't exist in the scene anymore
	"""
	def removeInvalidAssets(self):
		toRemove = []
		for td in self._textureData:
			if not cmds.objExists(td.name):
				toRemove.append(td)
		for td in toRemove:			
			self._textureData.remove(td)

		# We need to update the list of duplicates
		self.calculateDuplicates()
	
	"""
	Will move all textures in this collection to the specified directory
	@param directory: the directory to move all textures to.
	"""
	def moveTextures(self, directory):
		for td in self._textureData:
			td.moveTo(directory)

