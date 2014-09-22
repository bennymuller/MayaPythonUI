# Simplygon Batch Processor for Maya
==================================

## Introduction
The Simplygon Batch Processor allows you to predefine setting files in the Simplygon GUI and expose them for users in Maya. With it you can expose a subset of the settings per settingfile so that it is easy to get into for people that will not be digging deep into Simplygon.
Ideally the settings are then distributed to a versioning system, which allows artists to get the latest version at any given time. It should be viewed as an example of how you can integrate Simplygon into your workflow and making it easy for the users to tweak Simplygon for optimal results. The scripts are provided as-is and support will be given when time is available. 

![Alt text](images/overview.png?raw=true "Overview")

## Install instructions
- Install the Simplygon Maya plugin, following the instructions in Simplygon_Maya_Plugin.pdf in the Simplygon installation folder.
- Copy the files from the scripts folder into a the python script folder. Typically, this is located in Documents\maya\scripts. If you want to run the script straight from the repository you will have to add the following to lines to the maya shelf command (that you will create in the next step):
```
import sys
sys.path.append( '<your github location>/MayaPythonUI/scripts/' )
```
- Add a shelf command with following python code (starting with the above code if you're running it from the repository):
```
import SimplygonBatchProcessor
reload (SimplygonBatchProcessor) """if you want to further develop the plugin, this is good to have to recompile the code"""
SimplygonBatchProcessor.openSimplygonBatchProcessor()
```
- To create shelf command in Maya, you first need to open the shelf editor:

![Alt text](images/shelfeditor.png?raw=true "Shelf editor")

- Create a new script by clicking the marked button and name the script:

![Alt text](images/addscript.png?raw=true "Add script")

- With the newly created script selected, go to the command tab, set it to python mode and paste the code from above:

![Alt text](images/createscript.png?raw=true "Create script")

- Start the shelf command. A docked tab called *Batch Processor* should now be located where the attribute editor is.
- Browse to the xml file located in the setting folder in the top component to test that everything works.

## User weights
In the Simplygon GUI you can paint weights to tell the optimizer where to keep geometry, and where to reduce. This functionality is exposed in the plug-in as well.
In Maya you can add a color channel to your object to give the same instructions. Bear in mind that this only works with MeshLOD, so if you create a proxy the weights will be ingored.
Here are the steps on how to do that in Maya:
- Create/Load an object. For example, a highly tessellated sphere is a good test case.

- Create a color channel and name it to something appropriate.

![Alt text](images/colorset.png?raw=true "Create color set")

- Paint/fill the channel with 128,128,128 to set everything to normal to start off with. If you don't do this Simplygon will interpret unpainted areas as black.

![Alt text](images/floodfill.png?raw=true "Flood fill color set")

- Paint with blacker for areas you want to reduce more, whiter to keep.

![Alt text](images/paintedsphere.png?raw=true "Painted sphere")

- Enable User weights and make sure that the newly created color set is selected. You can also adjust the strength of the weights by sliding the Weight multiplier upwards for more effect.

![Alt text](images/userweights.png?raw=true "User weights")

- To check that your user weights are applied you can send it into Simplygon and enable the brush tool.

![Alt text](images/simplygonweights.png?raw=true "Simplygon Weights")

- You can also choose to optimize it straight away. Choose the "1 Mesh LOD setting" to try it out.

![Alt text](images/optimizedsphere.png?raw=true "Optimized sphere")


##Instructions to create your own settings and XML
After you have created a number of presets (.ini files) through the Simplygon interface you need to create an XML file to wrap the setting files. An example can be viewed in the Settings folder of the repository.
Start by wrapping all the setting files with the following tag:
```
<Setting file="<absolute or relative path to a .ini file" name="<name of the setting, will be displayed in the setting drop list. (must be unique)>">
```

Within each setting block you can create any number of sections. A section can consist of either keys or sections. They do not have to correspond to sections in the .ini file.	
```
<Section description="<Description for the section, will create a collapsable section in the setting window">`
```
			
Within a section you can expose any number of keys from the setting file. The keys have three common attributes:
- **name** = the name of the setting in the .ini file
- **section** = the section where the key can be found in the .ini file
- **description** = the text to show in the interface in association to the key

The following types of keys can be used: 			

###IntRange
Allows for customization of a key in a range of integer values. Example:
```
<Key name="ReductionRatio" section="Root/LODCollectionSection/LOD0Section" type="IntRange" description="Percentage reduction" min="25" max="75"/>
```

###FloatRange
Same as int range but allows floating point values. Example:
```
<Key name="ReductionRatio" section="Root/LODCollectionSection/LOD0Section" type="FloatRange" description="Percentage reduction" min="25" max="75"/>
```

###Droplist
Will create a drop list with a predefined set of values to select between. Each choice is described by a sub key called Choice. Example:
```
<Key name="GeometricImportance" section="Root/LODCollectionSection/LOD0Section/MeshReductionQualitySection/FeaturePreservationSection" type="Droplist" description="Silhouetto">
	<Choice value="Highest" description="<optional, what to show in the interface if you want to obfuscate the value>"/>
	<Choice value="High" description="<optional>"/>
	<Choice value="Normal" description="<optional>"/>
	<Choice value="Low" description="<optional>"/>
	<Choice value="Lowest" description="<optional>"/>
	<Choice value="Off" description="<optional>"/>
</Key>
```
###Checkbox
Will create a checkbox component for boolean values. Example:
```
<Key name="AllowVertexRepositioning" section="Root/LODCollectionSection/LOD0Section/MeshReductionQualitySection" type="Checkbox" description="Reposition vertices"/>
```


