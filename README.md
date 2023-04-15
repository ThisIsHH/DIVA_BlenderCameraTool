# DIVA_BlenderCameraTool
A .blend/.py that allow you to animate and export a JSON Project Diva A3DA Camera.

# How the script works
The script takes all the values in the scene and the values of every specific object (this could be a problem if we talk about the file size).

# How to use
## Camera Animation
Open the .blend file and go to the 'Animation' tab.
You can animate the following objects:

* CameraTrack (Loc x,y,z)
	* Camera (Focal Length, Rot z)
* Interest (Loc x,y,z)

(If a property have a Lock, is not supposed to be animated)
	
DIVA uses a camera system based on a Camera Position and an Interest. The Camera Position is where in the 3D space the camera is, while the Interest is where the camera is looking.
For example, if you have your 'Interest' positioned at (0,0,0) and you move your 'CameraTrack', the camera will always be pointing at your (0,0,0) 'Interest'.
Animate the 'camera' as desired.

## JSON Export/Conversion
When you're ready to export your work, follow these steps:

1- Go to the 'Scripting' tab, in *file_name = "Set your .a3da name here"* (line 11), change the name you want. For example:
*file_name = "CAMPV300_BASE"* (Do not write the file extension)
Run the script.
Your export is going to be in the same directory where the .blend file is located.

2- Use Korekonder's PD Tool for conversion:
Run PD Tool and select 'AC/DT/F/AFT Converting Tools' -> A3DA -> Select your JSON export -> A3DA [AFT/FT/M39] (tested in this option).

# Important notes
Ensure that the correct 'Frame Rate' is selected in your 'Output Properties' (commonly 60 fps).
You can use the graph editor, constraints, and many other Blender functions to animate the Camera.

# Credits
[korenkonder](https://github.com/korenkonder) for JSON A3DA layout and PD Tool.
https://github.com/korenkonder/PD_Tool
