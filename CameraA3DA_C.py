import bpy
import json
import math
import os

# We get the current path of where the .blend file is and change the directory to it
blend_file_path = bpy.data.filepath
dir_path = os.path.dirname(blend_file_path)

# InputName
file_name = "Set your .a3da name here"

# ExD
scene = bpy.context.scene
max_scene = scene.frame_end+1
fps = bpy.context.scene.render.fps

class keys:
    def __init__(self, frame, value, leftp, rightp):
        self.frame = frame
        self.value = value
        self.leftp = leftp
        self.rightp = rightp
        self.in_t = None #
        self.out_t = None #

# Location for Interest and ViewPoint
def anim_loc(obj, axis):
    if obj is None:
        return None
    
    if obj.animation_data is None or obj.animation_data.action is None:
        return obj.location[axis]
    
    anim = obj.animation_data.action.fcurves.find('location', index=axis)
    if anim is None:
        return obj.location[axis]

    res = []
    for pointv in anim.keyframe_points:
        frame = int(pointv.co[0])
        value = pointv.co[1]
        leftp = pointv.handle_left[1]
        rightp = pointv.handle_right[1]
        res.append(keys(frame, value, leftp, rightp))

    length = len(res)
    for i in range(length):
        if i == 0:
            res[i].in_t = 0.0
        # Current keyframe and the previous one
        else:
            t = res[i].frame - res[i-1].frame
            res[i].in_t = 3 * (res[i].value - res[i].leftp) / t

        if i == length - 1:
            res[i].out_t = 0.0
        # Next keyframe and the current one
        else:
            t = res[i+1].frame - res[i].frame
            res[i].out_t = 3 * (res[i].rightp - res[i].value) / t

    return res

# Rotation (Z) for CameraObject
def anim_rot(obj, axis):
    if obj is None:
        return None
    
    if obj.animation_data is None or obj.animation_data.action is None:
        return obj.rotation_euler[axis]
    
    anim = obj.animation_data.action.fcurves.find('rotation_euler', index=axis)
    if anim is None:
        return obj.rotation_euler[axis]

    res = []
    for pointv in anim.keyframe_points:
        frame = int(pointv.co[0])
        value = pointv.co[1]
        leftp = pointv.handle_left[1]
        rightp = pointv.handle_right[1]
        res.append(keys(frame, value, leftp, rightp))

    length = len(res)
    for i in range(length):
        if i == 0:
            res[i].in_t = 0.0
        # Current keyframe and the previous one
        else:
            t = res[i].frame - res[i-1].frame
            res[i].in_t = 3 * (res[i].value - res[i].leftp) / t

        if i == length - 1:
            res[i].out_t = 0.0
        # Next keyframe and the current one
        else:
            t = res[i+1].frame - res[i].frame
            res[i].out_t = 3 * (res[i].rightp - res[i].value) / t

    return res

# FOV for CameraObject
# We cannot directly animate the FOV. We will use the Focal Length instead
# Focal Length to FOV: 'FOV = 2 * atan(sensor Width / (2 * focal_length))'
# # https://www.nikonians.org/reviews/fov-tables
# # https://b3d.interplanety.org/en/how-to-get-camera- -in-degrees-from-focal-length-in-mm/
# These URLs were very helpful
def anim_fov(camera, sensor_width):
    if camera is None or camera.data is None:
        return None
    
    static_fov = 2 * math.atan(sensor_width / (2 * camera.data.lens))
    anim_data = camera.data.animation_data
    if anim_data is None or anim_data.action is None:
        return static_fov

    lens_anim = anim_data.action.fcurves.find("lens")
    if lens_anim is None:
        return static_fov

    res = []
    for pointv in lens_anim.keyframe_points:
        frame = int(pointv.co[0])
        focal_length = pointv.co[1]
        value = 2 * math.atan(sensor_width / (2 * focal_length))
        leftp = pointv.handle_left[1]
        rightp = pointv.handle_right[1]
        res.append(keys(frame, value, leftp, rightp))

    length = len(res)
    for i in range(length):
        if i == 0:
            res[i].in_t = 0.0
        else:
            t = res[i].frame - res[i-1].frame
            in_fov = 2 * math.atan(sensor_width / (2 * res[i].leftp))
            res[i].in_t = 3 * (res[i].value - in_fov) / t

        if i == length - 1:
            res[i].out_t = 0.0
        else:
            t = res[i+1].frame - res[i].frame
            out_fov = 2 * math.atan(sensor_width / (2 * res[i].rightp))
            res[i].out_t = 3 * (out_fov - res[i].value) / t

    return res

# JSON structure
def structure(obj_v):
    if obj_v == 0:
        return {"Type": "None"}
    elif isinstance(obj_v, float):
        return {"Type": "Static", "Value": obj_v}
    else:
        max_frame = max([i.frame for i in obj_v]) + 1
        return {
            "Type": "Hermite",
            "Max": max_frame,
            "Trans": [[i.frame, i.value, i.in_t, i.out_t] for i in obj_v]
        }

# Bear in mind to not modify the objs names
empty_camera = bpy.data.objects['CameraTrack']
empty_interest = bpy.data.objects['Interest']
camera = bpy.data.objects['Camera']
sensor_width = camera.data.sensor_width

# Transformation (x,y,z) of the ViewPoint
empty_camera_tx = anim_loc(empty_camera, 0)
empty_camera_ty = anim_loc(empty_camera, 1)
empty_camera_tz = anim_loc(empty_camera, 2)

# Transformation (x,y,z) of the Interest
empty_interest_tx = anim_loc(empty_interest, 0)
empty_interest_ty = anim_loc(empty_interest, 1)
empty_interest_tz = anim_loc(empty_interest, 2)

# Transformation (z) of the CameraObject
camera_rz = anim_rot(camera, 2)

# FOV of the CameraObject
camera_fov = anim_fov(camera, sensor_width)

# JSON based A3DA camera structure by Korekonder
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
            "X": structure(empty_interest_tx),
            "Y": structure(empty_interest_ty),
            "Z": structure(empty_interest_tz)
          },
          "Visibility": {
            "Type": "Static",
            "Value": 1
          }
        },
        "ViewPoint": {
          "Aspect": 1.77778005599976,
          "FOVIsHorizontal": True,
          "FOV": structure(camera_fov),
          "Roll": structure(camera_rz),
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
            "X": structure(empty_camera_tx),
            "Y": structure(empty_camera_ty),
            "Z": structure(empty_camera_tz)
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
