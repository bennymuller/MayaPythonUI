import maya.cmds as cmds

"""
Wrapper class to keep track of controls that are used in the SimplygonPanels.
"""
class SimplygonControl:
	def __init__(self, name, type):
		self._name = name
		self._type = type
		self._mObj = None
	
	"""
	Returns the name (not maya name) of this component.
	"""
	@property
	def name(self):
		return self._name

	"""
	Returns the type (not necessarily compatible with maya) of this component.
	"""
	@property
	def type(self):
		return self._type
		
	"""
	Returns the Maya object corresponding to this control.
	"""
	@property
	def mObj(self):
		return self._mObj

	"""
	Sets the Maya object corresponding to this control.
	"""
	@mObj.setter
	def mObj(self, mObj):
		self._mObj = mObj
		
"""
Parent class for panels that are used in the SimplygonBatchProcessor
"""
class SimplygonPanel:
	def __init__(self, name, batchProcessor):
		self._name = name
		self._batchProcessor = batchProcessor
		self._controls = {}
		
	"""
	Returns the name of this panel.
	"""
	@property
	def name(self):
		return self._name

	"""
	Returns the batch processor
	"""
	@property
	def batchProcessor(self):
		return self._batchProcessor				
		
	"""
	Defines a control that will exist in the context of this panel.
	@param name: Name of the control, must be unique within this panel
	@param type: Type of control, might come in handy at some point
	"""
	def defineControl(self, name, type):
		if name in self._controls:
			print "Error: The control "+name+" has already been defined in the panel "+self.name
		self._controls[name] = SimplygonControl(name, type)
		
	"""
	Clears the controls in this panel. Also deleting any MayaObj's from the UI.
	"""
	def clearControls(self):
		for name, control in self._controls.iteritems():
			if control.mObj != None:
				cmds.deleteUI(control.mObj)
		self._controls = {}
	
	"""
	Returns the control with the corresponding name, None if the control does not exist.
	@param name: Name of the control to get
	"""
	def getControl(self, name):
		return self._controls[name]
		
	"""
	Returns the maya object of the control with the corresponding name, None if the control does not exist.
	@param name: Name of the control to get
	"""
	def getMObj(self, name):
		control = self.getControl(name)
		if control == None:
			raise NameError("Cannot return the maya object for "+name+". It doesn't exist.")
		return control.mObj
		
	"""
	Sets the maya object of the control with the corresponding name, if the control does not exist a NameError will be thrown.
	@param name: Name of the control to get
	"""
	def setMObj(self, name, mObj):
		control = self.getControl(name)
		if control == None:
			raise NameError("Cannot set the maya object for component "+name+". It doesn't exist.")
		control.mObj = mObj
		
		
	"""
	--------------------------------------------------------------------------------------
	INTERFACE FUNCTIONS
	--------------------------------------------------------------------------------------
	"""
	
	"""
	Should be implemented by all classes
	@param parentContainer: the container to add the components to
	"""
	def createPanel(self, parentContainer):
		raise NotImplementedError("createPanel is not implemented on the panel: "+self.name)