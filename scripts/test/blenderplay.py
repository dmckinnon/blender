import bpy
import math
from math import sqrt, pi, sin, ceil

# Easy start to render a set of cubes

gridSize = 10
extents = 8.0

cubePadding = 0.05

cubeSize = (extents/gridSize) - cubePadding

# The height of each cube will be animated, so we'll specify the minimum and maximum scale.
sz = (extents / gridSize) - cubePadding
minsz = sz * 0.25
maxsz = sz * extents
diffsz = maxsz - minsz

# convert grid position to real world coords
iprc = 0.0
jprc = 0.0
kprc = 0.0
countf = 1.0 / (gridSize - 1)
diff = extents*2

# initial position of cubes
x = 0.0
y = 0.0
z = 0.0

centreX = 0.0
centreY = 0.0
centreZ = 0.0

# For animation, track current frame, specify desired number of key frames.
currframe = 0
fcount = 10
invfcount = 1.0 / (fcount - 1)

# If the default frame range is 0, then default to 1 .. 150.
frange = bpy.context.scene.frame_end - bpy.context.scene.frame_start
print("Default frange: " + str(frange))
if frange == 0:
    bpy.context.scene.frame_end = 150
    bpy.context.scene.frame_start = 0
    frange = 150
    
# Number of keyframes per frame.
fincr = ceil(frange * invfcount)

# For generating the wave.
offset = 0.0
angle = 0.0

# add a cube
bpy.ops.mesh.primitive_cube_add()
ob = bpy.context.object

# loop through Z
for i in range(0, gridSize, 1):
        
    # convert from index to percent in range 0-1
    # then convert from prc to real world coords
    # Equivalent to map(val, lb0, ub0, lb1, ub1)
    iprc = i*countf
    z= -extents + iprc*diff
    
    # loop through Y
    for j in range(0, gridSize, 1):
        jprc = j*countf
        y = -extents + jprc*diff
        
        # loop through x
        for k in range(0, gridSize):
            kprc = k * countf
            x = -extents + kprc*diff
            
            # add grid world position to cube local position
            # add cube to world?
            #bpy.ops.mesh.primitive_cube_add(size = cubeSize, location=(centreX + x, centreY + y, centreZ + z))
            copy = ob.copy()
            copy.data = ob.data.copy()
            copy.location.x = centreX + x
            copy.location.y = centreY + y
            copy.location.z = centreZ + z
            copy.dimensions[0] = cubeSize
            copy.dimensions[1] = cubeSize
            copy.dimensions[2] = cubeSize
            
            
            
            # keep a handle on current object
            #current = bpy.context.object
            
            # set object metadata
            copy.name = 'Cube ({0}, {1}, {2})'.format(k, j, i)
            copy.data.name = 'Mesh ({0}, {1}, {2})'.format(k, j, i)
            
            # create a material
            mat = bpy.data.materials.new(name='Material ({0}, {1}, {2}))'.format(k, j, i))
            
            # assign a diffuse colour
            mat.diffuse_color = (kprc, jprc, iprc, 1.0)
            copy.data.materials.append(mat)
            
            bpy.context.scene.collection.objects.link(copy)
            
# update scene after adding cubes
bpy.context.view_layer.update()          
            
# add a sun lamp above grid
# TODO: make it move and keyframe every few motions? How to do ... 
bpy.ops.object.light_add(type='SUN', radius = 1.0, location = (0.0, 0.0, extents*(2/3)))

# isometric camera above grid
# rotate 45 degrees in x, 135 degrees in z (45 from 180)
bpy.ops.object.camera_add(location=(extents*1.414, extents*1.414, extents*2.121), rotation=(0.785398, 0.0, 2.35619))
bpy.context.object.data.type = 'ORTHO'
bpy.context.object.data.ortho_scale = extents*7.0

# Track the current key frame.
# Loop over all cubes

# TODO
# how to get all cubes from the scene?
"""
            # why are keyframes per cube?
            currframe = bpy.context.scene.frame_start
            zOffset = current.location[2]
            for f in range(0, fcount, 1):

                # Convert the keyframe into an angle.
                fprc = f * invfcount
                angle = 2*pi * fprc

                # Set the scene to the current frame.
                bpy.context.scene.frame_set(currframe)

                # Change the location.
                # sin returns a value in the range -1 .. 1. abs changes the range to 0 .. 1. 
                # The values are remapped to the desired scale with min + percent * (max - min).
                current.location[2] = zOffset + minsz + abs(sin(offset + angle)) * diffsz

                # Insert the key frame for the location property.
                current.keyframe_insert(data_path='location', index=2)

                # Advance by the keyframe increment to the next keyframe.
                currframe += fincr"""