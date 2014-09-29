import maya.cmds as cmds
import os
import hashlib

def hashfile(afile, hasher, blocksize=65536):
	buf = afile.read(blocksize)
	while len(buf) > 0:
		hasher.update(buf)
		buf = afile.read(blocksize)
	return hasher.digest()

class TextureData:
	def __init__(self, textureName):
		self._name = textureName
		self._materialConnection = None
		self._filePath = cmds.getAttr(textureName+'.fileTextureName')
		self._hash = hashfile(open(self._filePath , 'rb'), hashlib.sha256()) 
			
	def isEqual(self, textureData):
		return self.name == textureData.name or self.filePath == textureData.filePath or self.hash == textureData.hash
		
	@property
	def materialConnection(self):
		return self._materialConnection

	@materialConnection.setter
	def materialConnection(self, mc):
		self._materialConnection = mc

	@property
	def name(self):
		return self._name

	@property
	def hash(self):
		return self._hash

	@property
	def filePath(self):
		return self._filePath

		
class TextureManager:
	def __init__(self):
		self._textureData = []
		self._duplicates = {}
	
	def initJob(self):
		self._textures = cmds.ls( textures=True)
		
	def jobDone(self):
		# Time to find out which textures were added
		texturesNow = cmds.ls( textures=True)
		for t in texturesNow:
			if t not in self._textures:
				self._textureData.append(TextureData(t))

		#Group all textures by their hash value to sort out duplications
		for td in self._textureData:
			if(td.hash not in self._duplicates):
				self._duplicates[td.hash] = []
			self._duplicates[td.hash].append(td)

				
	def getTextureData(self, name):
		for td in self._textureData:
			if td.name == name:
				return td
		return None

		
	def redirectTo(self, textureData):
		if textureData.hash in self._duplicates and len(self._duplicates[textureData.hash]) >1:
			replacement = self._duplicates[textureData.hash][0]
			if textureData.name != replacement:
				return replacement
		#No need to replace the texture
		return None
		
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

