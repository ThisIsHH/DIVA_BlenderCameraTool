import bpy
import json
import math
import os

# We get the current path of where the .blend file is and change the directory to it
blend_file_path = bpy.data.filepath
dir_path = os.path.dirname(blend_file_path)

# InputName
file_name = "Set your .a3da name here"

# Bear in mind to not modify the objs names
empty_camera = bpy.data.objects['CameraTrack']
empty_interest = bpy.data.objects['Interest']
camera = bpy.data.objects['Camera']
scene = bpy.context.scene
max_scene = scene.frame_end+1
fps = bpy.context.scene.render.fps

trans_viewp_list = []
roll_viewp_list = []
fov_list = []
trans_interest_list = []

#
for frame in range(scene.frame_start, scene.frame_end+1):
    bpy.context.scene.frame_set(frame)
    
    # Transformation (x,y,z) of the ViewPoint
    trans_viewp = empty_camera.matrix_local.to_translation()
    trans_viewp_list.append([frame, trans_viewp.x, trans_viewp.y, trans_viewp.z])
    
    # Roll of ViewPoint (ONLY axis Z of the camera)
    roll_viewp = camera.matrix_local.to_euler()
    roll_viewp_list.append([frame, roll_viewp.x, roll_viewp.y, roll_viewp.z])
    
    # We cannot directly animate the FOV. We will use the Focal Length instead
    # Focal Length to FOV: 'FOV = 2 * atan(sensor Width / (2 * focal_length))'
    # # https://www.nikonians.org/reviews/fov-tables
    # # https://b3d.interplanety.org/en/how-to-get-camera- -in-degrees-from-focal-length-in-mm/
    # These URLs were very helpful
    focal_length = camera.data.lens
    sensor_width = camera.data.sensor_width
    fov = 2 * math.atan(sensor_width / (2 * focal_length))
    fov_list.append([frame, fov])
    
    # Transformation (x,y,z) of the Interest
    trans_interest = empty_interest.matrix_local.to_translation()
    trans_interest_list.append([frame, trans_interest.x, trans_interest.y, trans_interest.z])

# json based .a3da camera structure by Korekonder
export = json.dumps(
{
  "A3D": {
    "_": {
      "ConverterVersion": "20050823",
      "FileName": file_name+".a3da",
      "PropertyVersion": "20050706"
    },
    "CameraRoot": [
      {
        "Interest": {
          "Rot": {
            "X": {
              "Type": "None"
            },
            "Y": {
              "Type": "None"
            },
            "Z": {
              "Type": "None"
            }
          },
          "Scale": {
            "X": {
              "Type": "Static",
              "Value": 1
            },
            "Y": {
              "Type": "Static",
              "Value": 1
            },
            "Z": {
              "Type": "Static",
              "Value": 1
            }
          },
          "Trans": {
            "X": {
              "Type": "Hermite",
              "Max": max_scene,
              "Trans": [[i[0], i[1]] for i in trans_interest_list]
            },
            "Y": {
              "Type": "Hermite",
              "Max": max_scene,
              "Trans": [[i[0], i[2]] for i in trans_interest_list]
            },
            "Z": {
              "Type": "Hermite",
              "Max": max_scene,
              "Trans": [[i[0], i[3]] for i in trans_interest_list]
            }
          },
          "Visibility": {
            "Type": "Static",
            "Value": 1
          }
        },
        "ViewPoint": {
          "Aspect": 1.77778005599976,
          "FOVIsHorizontal": True,
          "FOV": {
            "Type": "Hermite",
            "Max": max_scene,
            "Keys": [[i[0], i[1]] for i in fov_list]
          },
          "Roll": {
            "Type": "Hermite",
            "Max": max_scene,
            "Keys": [[i[0], i[3]] for i in roll_viewp_list]
          },
          "Rot": {
            "X": {
              "Type": "None"
            },
            "Y": {
              "Type": "None"
            },
            "Z": {
              "Type": "None"
            }
          },
          "Scale": {
            "X": {
              "Type": "Static",
              "Value": 1
            },
            "Y": {
              "Type": "Static",
              "Value": 1
            },
            "Z": {
              "Type": "Static",
              "Value": 1
            }
          },
          "Trans": {
            "X": {
              "Type": "Hermite",
              "Max": max_scene,
              "Trans": [[i[0], i[1]] for i in trans_viewp_list]
            },
            "Y": {
              "Type": "Hermite",
              "Max": max_scene,
              "Trans": [[i[0], i[2]] for i in trans_viewp_list]
            },
            "Z": {
              "Type": "Hermite",
              "Max": max_scene,
              "Trans": [[i[0], i[3]] for i in trans_viewp_list]
            }
          },
          "Visibility": {
            "Type": "Static",
            "Value": 1
          }
        },
        "Rot": {
          "X": {
            "Type": "None"
          },
          "Y": {
            "Type": "None"
          },
          "Z": {
            "Type": "None"
          }
        },
        "Scale": {
          "X": {
            "Type": "Static",
            "Value": 1
          },
          "Y": {
            "Type": "Static",
            "Value": 1
          },
          "Z": {
            "Type": "Static",
            "Value": 1
          }
        },
        "Trans": {
          "X": {
            "Type": "None"
          },
          "Y": {
            "Type": "None"
          },
          "Z": {
            "Type": "None"
          }
        },
        "Visibility": {
          "Type": "Static",
          "Value": 1
        }
      }
    ],
    "PlayControl": {
      "Begin": 0,
      "FPS": fps,
      "Size": max_scene
    }
  }
},
indent=2)

# Export
with open(os.path.join(dir_path, f"{file_name}.json"), 'w') as f:
    f.write(export)
