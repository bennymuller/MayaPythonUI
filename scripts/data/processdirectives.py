"""
Class that contains the directives that are used to initiate a Simplygon job.
"""
class ProcessDirectives:
	def __init__(self):
		self._batchMode = False
		self._settingFile = ""
		self._useWeights = False
		self._colorSet = ""
		self._weightMultiplier = 1
	
	"""
	Property that specifies whether to use custom color sets from Maya when starting the Simplygon process. Should always be
	set in combination with colorSet.
	"""
	@property
	def useWeights(self):
		return self._useWeights
	@useWeights.setter
	def useWeights(self, enabled):
		self._useWeights = enabled		

	"""
	The color set that should be used as custom weights
	"""
	@property
	def colorSet(self):
		return self._colorSet
	@colorSet.setter
	def colorSet(self, setName):
		self._colorSet = setName

	"""
	The multiplier to increase the power of the user weights by.
	"""
	@property	
	def weightMultiplier(self):
		return self._weightMultiplier		
	@weightMultiplier.setter
	def weightMultiplier(self, multiplier):
		self._weightMultiplier = multiplier		
	"""
	The path to the settingfile to use during the job
	"""
	@property
	def settingFile(self):
		return self._settingFile
	@settingFile.setter
	def settingFile(self, filePath):
		self._settingFile = filePath

	"""
	True if the process should be run without going through the SimplygonGUI. 
	"""
	@property
	def batchMode(self):
		return self._batchMode
	@batchMode.setter
	def batchMode(self, enabled):
		self._batchMode = enabled
