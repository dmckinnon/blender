import bpy
from math import pi, sin, cos, ceil
from mathutils import Vector, Quaternion
import colorsys
from random import random
from random import TWOPI

# So this is an exploration of metaballs
# The hopeful final result, if this is possible, is to have a metamaterial
# where blobs are created at the top, fall to the bottom whilst repelling,
# and then reform at the bottom, very water-like (high reynolds number fluid)

# I'll try this for a bit longer, before just copying their approach and modifying

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
numMetaballs = 2
gravity = 9.8
center = Vector((0.0, 0.0, 0.0))

# metaball element types
elemtypes = ['BALL', 'CAPSULE', 'PLANE', 'ELLIPSOID', 'CUBE']

# Create metaball data, then assign it to a metaball object.
mbdata = bpy.data.metaballs.new('SphereData')
mbdata.render_resolution = 0.075
mbdata.resolution = 0.02
#mbdata.update_method = UPDATE_ALWAYS
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

print("total time is " + str(total_time))

# Loop over each metaball element

# Firstly, I want to loop over total number of elements
# secondly, I want to loop over time, each with a time offset
# Within some range of 0,0,1, I randomly create a metaball element
# with a time offset, and have gravity apply, along with negative cohesion
# and that's the keyframes
# and then when it hits 0,0,0, gravity stops applying and cohesion is positive again

# Do we need to set a camera up here?
# and lighting?

# Add a sun lamp above the grid.
bpy.ops.object.light_add(type='SUN', radius=1.0, location=(0.5, 0.5, 0.5))

# Add an isometric camera above the grid.
# Rotate 45 degrees on the x-axis, 180 - 45 (135) degrees on the z-axis.
bpy.ops.object.camera_add(location=(0, 1, 0.5), rotation=(-1.5, 0.0, 0))
bpy.context.object.data.type = 'ORTHO'
bpy.context.object.data.ortho_scale = 3


for i in range(0, numMetaballs, 1):
    time_offset = 0#random() * 100
    width_offset = random() - 0.5
    size_multiplier = random();
    pt = Vector((width_offset, 0.0, 1.0))
    initial_height = 1
    
    # Add a metaelement to the metaball.
    # See elemtypes array above for possible shapes.
    mbelm = mbdata.elements.new(type=elemtypes[3])
    mbelm.co = pt
    mbelm.radius = 0.15 +  size_multiplier * 0.1
    # Stiffness of blob, in a range of 1 .. 10.
    mbelm.stiffness = 1

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
    apply_gravity = True
    for f in range(0, total_time-1, 1):
        if f < time_offset:
            continue
        
        if pt.z < (1/total_time):
            #print("removing gravity for element " + str(i))
            mbelm.use_negative = False
            apply_gravity = False
        
        # now apply gravity
        if apply_gravity:
            #print("applying gravity - height is " + str(pt))
            pt.z = initial_height - f*(1/240)
            #mbelm.co[2] = mbelm.co[2] - (1/frange)# = -0.5*gravity*(f-time_offset)*(f-time_offset) # might need to scale this down
            
        mbelm.co = pt
        #print("position for " + str(i) + " is " + str(mbelm.co))
        bpy.context.scene.frame_set(currframe)

        print("creating keyframe for element " + str(i))
        mbelm.keyframe_insert(data_path='co')

        currframe += 1