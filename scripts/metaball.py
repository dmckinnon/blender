import bpy
from math import pi, sin, cos, ceil
from mathutils import Vector, Quaternion
import colorsys
import random
from random import TWOPI

# So this is an exploration of metaballs
# The hopeful final result, if this is possible, is to have a metamaterial
# where blobs are created at the top, fall to the bottom whilst repelling,
# and then reform at the bottom, very water-like (high reynolds number fluid)

# Some of this code is boilerplate and/or copied from https://medium.com/@behreajj/creative-coding-in-blender-a-primer-53e79ff71e

# Some vector operations
def vecrotate(angle, axis, vin, vout):
    # Assume axis is a unit vector.
    # Find squares of each axis component.
    xsq = axis.x * axis.x
    ysq = axis.y * axis.y
    zsq = axis.z * axis.z

    cosa = cos(angle)
    sina = sin(angle)

    complcos = 1.0 - cosa
    complxy = complcos * axis.x * axis.y
    complxz = complcos * axis.x * axis.z
    complyz = complcos * axis.y * axis.z

    sinx = sina * axis.x
    siny = sina * axis.y
    sinz = sina * axis.z

    # Construct the x-axis (i).
    ix = complcos * xsq + cosa
    iy = complxy + sinz
    iz = complxz - siny

    # Construct the y-axis (j).
    jx = complxy - sinz
    jy = complcos * ysq + cosa
    jz = complyz + sinx

    # Construct the z-axis (k).
    kx = complxz + siny
    ky = complyz - sinx
    kz = complcos * zsq + cosa

    vout.x = ix * vin.x + jx * vin.y + kx * vin.z
    vout.y = iy * vin.x + jy * vin.y + ky * vin.z
    vout.z = iz * vin.x + jz * vin.y + kz * vin.z
    return vout


def vecrotatex(angle, vin, vout):
    cosa = cos(angle)
    sina = sin(angle)
    vout.x = vin.x
    vout.y = cosa * vin.y - sina * vin.z
    vout.z = cosa * vin.z + sina * vin.y
    return vout

# Some base variables
diameter = 8.0
sz = 2.125 / diameter
numMetaballs = 20
iprc = 0.0
jprc = 0.0
phi = 0.0
theta = 0.0
center = Vector((0.0, 0.0, 0.0))

# metaball element types
elemtypes = ['BALL', 'CAPSULE', 'PLANE', 'ELLIPSOID', 'CUBE']

# Create metaball data, then assign it to a metaball object.
mbdata = bpy.data.metaballs.new('SphereData')
mbdata.render_resolution = 0.075
mbdata.resolution = 0.2
mbobj = bpy.data.objects.new("Sphere", mbdata)
bpy.context.scene.collection.objects.link(mbobj)

# Add a material to the metaball.
mat = bpy.data.materials.new(name='SphereMaterial')
mat.diffuse_color = (0.0, 0.5, 1.0, 0.5)

# I'm adding some extra material parameters for fun
mat.specular_intensity = 0.7
mat.specular_color = (0.0, 0.8, 0.9)
mat.metallic = 0.3

mbobj.data.materials.append(mat)

# update scene after adding cubes
bpy.context.view_layer.update()    

# Animation variables.
currframe = 0
fcount = 10
invfcount = 1.0 / (fcount - 1)
frange = bpy.context.scene.frame_end - bpy.context.scene.frame_start

if frange == 0:
    bpy.context.scene.frame_end = 150
    bpy.context.scene.frame_start = 0
    frange = 150
fincr = ceil(frange * invfcount)
total_time = frange

# Loop over each metaball element

# Firstly, I want to loop over total number of elements
# secondly, I want to loop over time, each with a time offset
# Within some range of 0,0,1, I randomly create a metaball element
# with a time offset, and have gravity apply, along with negative cohesion
# and that's the keyframes
# and then when it hits 0,0,0, gravity stops applying and cohesion is positive again

# Do we need to set a camera up here?
# and lighting?
"""
# Add a sun lamp above the grid.
bpy.ops.object.lamp_add(type='SUN', radius=1.0, location=(0.0, 0.0, extents * 0.667))

# Add an isometric camera above the grid.
# Rotate 45 degrees on the x-axis, 180 - 45 (135) degrees on the z-axis.
bpy.ops.object.camera_add(location=(extents * 1.414, extents * 1.414, extents * 2.121), rotation=(0.785398, 0.0, 2.35619))
bpy.context.object.data.type = 'ORTHO'
bpy.context.object.data.ortho_scale = extents * 7.0
"""

for i in range(0, numMetaballs, 1):
    time_offset = rand(100)
    size_multiplier = rand(100)/100;
    pt = Vector((0.0, 0.0, 1.0))
    
    # Add a metaelement to the metaball.
    # See elemtypes array above for possible shapes.
    mbelm = mbdata.elements.new(type=elemtypes[0])
    mbelm.co = pt
    mbelm.radius = 0.15 + sz * size_multiplier * 1.85
    # Stiffness of blob, in a range of 1 .. 10.
    mbelm.stiffness = 0.8

    # Set metaelement to have a repulsive, rather than attractive force.
    mbelm.use_negative = True
    
    # update scene after adding cubes
    bpy.context.view_layer.update()    
    """
    iprc = i * invlatitude
    phi = pi * (i + 1) * invlatitude

    sinphi = sin(phi)
    cosphi = cos(phi)

    rad = 0.01 + sz * abs(sinphi) * 0.99
    pt.z = cosphi * diameter

    for j in range(0, longitude, 1):
        jprc = j * invlongitude
        theta = TWOPI * j / longitude

        sintheta = sin(theta)
        costheta = cos(theta)

        pt.y = center.y + sinphi * sintheta * diameter
        pt.x = center.x + sinphi * costheta * diameter

        

        vecrotatex(theta, baseaxis, axis)
"""
    currframe = bpy.context.scene.frame_start
    #currot = startrot
    #center = startcenter
    for f in range(0, fcount, 1):
        if f < time_offset:
            continue
        
        if mbelm.co[2] < 0.01:
            mbelm.use_negative = False
        
        # now apply gravity
        
        fprc = f * invfcount
        osc = abs(sin(TWOPI * fprc))
        bpy.context.scene.frame_set(currframe)

        # Animate location.
        vecrotate(TWOPI * fprc, axis, pt, rotpt)
        center = startcenter.lerp(stopcenter, osc)
        rotpt = rotpt + center
        current.location = rotpt
        current.keyframe_insert(data_path='location')

        # Animate rotation.
        currot = startrot.slerp(stoprot, jprc * fprc)
        current.rotation_euler = currot.to_euler()
        current.keyframe_insert(data_path='rotation_euler')

        # Animate color.
        mat.diffuse_color = colorsys.hsv_to_rgb(jprc, osc, 1.0)
        mat.keyframe_insert(data_path='diffuse_color')

        currframe += fincr