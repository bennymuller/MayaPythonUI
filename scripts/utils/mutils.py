import maya.cmds as cmds
from itertools import tee, izip

"""
Creates an iterable for a list that consists of tuples of 2.
@param iterable: the list to make an iterable for
"""
def pairwise(iterable):
    a = iter(iterable)
    return izip(a, a)

"""
Returns the attribute component of the object.attribute string
@param attrString: the attribute string
"""	
def getAttribute(attrString):
	attrIndex = attrString.rfind('.')
	return attrString[attrIndex+1:]

"""
Returns a tuple of two elements, the first one is the object and the second one is the attribute.
@attrString: string to splice
"""
def getObjectAndAttribute(attrString):
	attrIndex = attrString.rfind('.')
	return (attrString[:attrIndex],attrString[attrIndex+1:])
	
"""
Returns the attribute that is connected to the current attribute. Expecting there to be exactly one connection, otherwise
an exception will be raised.
@param attribute: the attribute to find the connection for
@param isSource: true if the attribute is the source, false if it's the destination.
@return: the connected attribute string
"""	
def getConnectedAttribute(attribute, isSource):
	if isSource:
		connectedAttribute = cmds.connectionInfo(attribute,dfs=True)
	else:
		connectedAttribute = cmds.connectionInfo(attribute,sfd=True)
	#If we're getting a list back we should verify that it's only connected to one attribute
	if connectedAttribute != None and isinstance(connectedAttribute, list):
		if len(connectedAttribute) > 1:
			raise ValueError("Unexpectedly found several connections for the attribute: "+attribute	)			
		connectedAttribute = connectedAttribute[0]
	return connectedAttribute
	
"""
Moves the connection from the old attribute to the new attribute.
@param oldSrcAttr: the previous source attribute
@param newSrcAttr: the new source attribute
@param targetAttr: the target attribute
"""
def moveConnection(oldSrcAttr, newSrcAttr, targetAttr):	
	cmds.disconnectAttr(oldSrcAttr, targetAttr) 		
	cmds.connectAttr(newSrcAttr, targetAttr, f=True)
