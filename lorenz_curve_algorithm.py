import bpy
import math
import random
import numpy as np
from mathutils import Vector


# open an external python file from Blender console
# filename = "/Users/bruce/Desktop/Lorenz Curve/blender_curve.py"
# exec(compile(open(filename).read(), filename, 'exec'))






uid = 0 # Blender Object unique ID serial number


def random_vector_array(min=5, max=25):
  """
  create an arrary for random depth populated by random xyz coord
  :param min: minimum array dimension
  :param max: maximum array dimension

  :return: array OR list of coordinates
  """
  ubound = random.randint(min, max)
  seq = []
  for n in range(0, ubound):
      xyz = (random.randint(0,5), random.randint(0,5), random.randint(0,5))
      seq.append(xyz)
  return seq


def get_aizawa_cord (x, y, z):
    a = 0.95
    b = 0.7
    c = 0.6
    d = 3.5
    e = 0.25
    f = 0.1
    dx = ((z-b)*x) - (d*y)
    dy = d * x + ((z-b)*y)
    dz = c+(a*z)-(math.pow(z,3.0)/3.0)-(math.pow(x,2.0)+math.pow(y,2.0)*(1+(e*z)))+(f*z*math.pow(x,3.0))
    return dx, dy, dz


def get_rossler_cord(x, y, z, a=0.2, b=0.2, c=5.7):
  """
  Return the xyz velocities of a point at xyz
  :param x: x coord
  :param y: y coord
  :param z: z coord
  :param s: sigma
  :param r: tho
  :param b: beta
  :return: tuple of xyz coords
  """
  x_dot = -(y + z)
  y_dot = x + a * y
  z_dot = b + z * (x - c)
  return x_dot, y_dot, z_dot

def get_lorenz_cord(x, y, z, s=10, r=28, b=2.667):
  """
  Return the xyz velocities of a point at xyz
  :param x: x coord
  :param y: y coord
  :param z: z coord
  :param s: sigma
  :param r: tho
  :param b: beta
  :return: tuple of xyz coords
  """
  x_dot = s*(y - x)
  y_dot = r*x - y - x*z
  z_dot = x*y - b*z
  return x_dot, y_dot, z_dot


def get_position_array(f, dt = 0.01, xyz = (0.0, 1.0, 1.05), step_count = 10000, step_by = 1):
  # Setting initial values
  xs = np.empty((step_count + 1,))
  ys = np.empty((step_count + 1,))
  zs = np.empty((step_count + 1,))
  xs[0], ys[0], zs[0] = (xyz)
  # Stepping through "time".
  seq = []
  for i in range(0, step_count, step_by):
      # Derivatives of the X, Y, Z state
      x_dot, y_dot, z_dot = f(xs[i], ys[i], zs[i])
      xs[i + 1] = xs[i] + (x_dot * dt)
      ys[i + 1] = ys[i] + (y_dot * dt)
      zs[i + 1] = zs[i] + (z_dot * dt)
      seq.append((xs[i] + (xs[i + 1]), (ys[i + 1]), (zs[i + 1])))
  return seq


def makePolyLine(curvename, cList, step_count = 10000.0):
  global uid
  uid += 1
  w = 1  # weight
  obj_name = curvename + "%s" % uid
  curve_data = bpy.data.curves.new(name=curvename, type='CURVE')
  curve_data.dimensions = '3D'
  # Create a new scene Object
  object_data = bpy.data.objects.new(obj_name, curve_data)
  object_data.location = (0,0,0)
  # Link the scene to the new Object
  bpy.context.scene.objects.link(object_data)
  # create the blender line Object as a NURB
  polyline = curve_data.splines.new('NURBS')
  polyline.points.add(len(cList)-1)
  # Iterate over the xyz coord list and append vert to the line
  for num in range(len(cList)):
      polyline.points[num].co = (cList[num])+(w,)
  polyline.order_u = len(polyline.points)-1
  polyline.use_endpoint_u = True



# makePolyLine("lorenz", get_position_array(get_lorenz_cord))
# makePolyLine("rossler", get_position_array(get_rossler_cord))
# makePolyLine("aizawa", get_position_array(get_aizawa_cord))
