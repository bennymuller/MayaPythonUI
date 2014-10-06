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