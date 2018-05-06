#!/usr/bin/python3
import bpy
import json
import shutil
import time
import socket
import os
import cv2
import glob
import numpy as np
from random import *



banner = """

           ████                              ██
          ░██░                              ░██
         ██████ ██████  █████  ███████      ░██  █████  ██████
        ░░░██░ ░░██░░█ ██░░░██░░██░░░██  ██████ ██░░░██░░██░░█
          ░██   ░██ ░ ░███████ ░██  ░██ ██░░░██░███████ ░██ ░
          ░██   ░██   ░██░░░░  ░██  ░██░██  ░██░██░░░░  ░██
          ░██  ░███   ░░██████ ███  ░██░░██████░░██████░███
          ░░   ░░░     ░░░░░░ ░░░   ░░  ░░░░░░  ░░░░░░ ░░░
          ____________________________________________________
          (f)rame (render) -- the poor mans network renderer


"""




def get_hostname():
    """ returns the machine's name """
    return socket.gethostname()

def get_local_ip():
    """ this should only run if there is no
        existing node config ie. hostname.json """

    return ([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
        if not ip.startswith("127.")][:1],
            [[(s.connect(('8.8.8.8', 53)),
            s.getsockname()[0],
            s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])


def update_config(obj):
    """ replaces the previous config JSON """
    filename = obj['filename']
    with open(filename, 'w') as f:
        json.dump(obj, f)


def get_config():
    """ get or create the config file """
    obj = None
    hostname = socket.gethostname()
    pathname = "./render/" + hostname
    filename = "%s/config.json" % (pathname)

    if os.path.exists(filename):
        print ("opening the config: %s" % ( filename ))
        with open(filename, 'r') as f:
            obj = json.load(f)

    else:
        print ("creating the config: %s" % ( filename ))

        # Initial values need to come from stdio
        print ("Collect manditory render arguments")
        os.makedirs(pathname, exist_ok=True)

        # Initial config object
        obj = {
            "iteration": [0,0],
            "current": None,
            "seed": None,
            "samples": 10,
            "range": [0,0],
            "ipaddr": get_local_ip(),
            "hostname": hostname,
            "filename": filename,
            "scene_name": None,
            "width": 1920,
            "height": 1080,
            "scale": 100,
            "continue": True
        }


        # Manditory user input variables
        obj['range'][0] = get_question("Start frame")
        obj['range'][1] = get_question("End frame")

        obj['iteration'][0] = 0
        obj['iteration'][1] = get_question("Render iterations")

        obj['samples'] = get_question("Render samples")
        obj['scene_name'] = get_question("Blender scene name ", False)
        obj['output'] = get_question("Output folder ", False)



        # Derived initilization values
        obj['current'] = obj['range'][0] - 1
        obj["seed"]= (obj['iteration'][0] * 100) + randint(10,99)

        # Persist user config
        update_config(obj)


    return obj


def get_question (text, is_int=True, width=38):

    before = " ".lust(10, " ")
    padding = text.ljust(width, ".")
    question = input("%s%s? " % (before, padding))

    if is_int: return int(question)
    return question

def collate(src, dst):
    ''' merge the images together then delete the src folder
        the RGB data is blended (aka addWeighted of 50%) each
        then the alpha channel is extracted from the source image
        and injected into the final image.

        To do this the images need to be split, and re-merged to RGBA
    '''


    for image_path in glob.glob(dst + "/*"):
        
        filename = image_path.split("/")[-1]
        print (">> FILENAME: %s %s" % (image_path, filename))

        # extract the alpha channel from the render
        img_src = cv2.imread(src + "/" + filename, cv2.IMREAD_UNCHANGED) # includes alpha
        img_dst = cv2.imread(dst + "/" + filename, cv2.IMREAD_UNCHANGED) # includes alpha

        # extract source alpha channel
        B, G, R, A = cv2.split(img_src)

        # blend the images
        print ("Blend")
        img_blend = cv2.addWeighted(img_src, 0.5, img_dst, 0.5, 0, 2)

        # extract NEW splitcolor registers
        print ("Seperate color registers")
        B = img_blend[:,:,0]
        G = img_blend[:,:,1]
        R = img_blend[:,:,2]

        print ("Examine the register dtypes")
        print ("B", B.shape, B.size, B.dtype)
        print ("G", G.shape, G.size, G.dtype)
        print ("R", R.shape, R.size, R.dtype)
        print ("A", A.shape, A.size, A.dtype)

        # inject the alpha, and save to output
        print ("Merge - inject source alpha into processed RGB")
        RGBA = cv2.merge((B, G, R, A))

        print ("Save - Blended image: %s" % filename)
        cv2.imwrite(dst + "/" + filename, RGBA)


    shutil.rmtree(src, ignore_errors=True)
    print ("Delete source folder: %s" % src)
    return True







print (banner)
time.sleep(2)

# Initialize ...
config = get_config()
current = config['current']
# Blender scene object 
Scenename = config["scene_name"]
Scene = bpy.data.scenes[Scenename]


# Quality and dimensions
Scene.render.resolution_percentage = config['scale']
Scene.render.resolution_x = config['width']
Scene.render.resolution_y = config['height']
Scene.render.use_antialiasing = True
Scene.render.use_placeholder = True
Scene.render.use_overwrite = False

# image format
Scene.render.image_settings.color_mode = 'RGBA'
Scene.render.image_settings.file_format = 'PNG'
Scene.render.image_settings.color_depth = "16"
Scene.render.image_settings.compression = 100


contd = config['continue'] and (config['iteration'][0] <= config['iteration'][1])
while contd:


    scene_path = "./render/%s/%s/" % (config['hostname'], Scenename)
    frame_folder = "e%s_s%s" % (str(config['seed']).rjust(4,"0"), str(config['samples']).rjust(4,"0"))


    if current + 1 > config['range'][1]:

        # collate the iteration into the output folder
        # eg: //render/aluminium/Scene/v1/f0001.png ..... f0260.png
        dst = scene_path + config['output']
        src = scene_path + frame_folder

        if not os.path.exists(dst):

            # if the folder does not exists then rename the current folder
            os.rename(src, dst)

        else:

            # if the output folder exists ... 
            # iterate over the filenames, and blend their values
            if (os.path.exists(src)):
                collate(src, dst)
                shutil.rmtree(src, ignore_errors=True)


        # After each iteration refresh the config
        # incase it was updated externally
        config = get_config()
        config['current'] = config['range'][0] - 1
        config['iteration'][0] += 1
        config["seed"] = (config['iteration'][0] * 100) + randint(10,99)



    # Frame output settings
    frame_folder = "e%s_s%s" % (str(config['seed']).rjust(4,"0"), str(config['samples']).rjust(4,"0"))
    render_path = "//render/%s/%s/%s/f" % (config['hostname'], Scenename, frame_folder)
    Scene.render.filepath = render_path


    # Integrity check the iterations
    stop = not config['continue'] or (config['iteration'][0] >= config['iteration'][1])
    if stop:
        print ("Exting:f%s n%s i%s" % (render_path, current, config['iteration'][0]))
        update_config(config)
        break;

    # Set the current frame to be rendered
    current = config['current']  + 1
    bpy.data.scenes[Scenename].frame_start = current
    bpy.data.scenes[Scenename].frame_end = current

    # Cycles sampling
    Scene.cycles.samples = config["samples"]
    Scene.cycles.seed = config['seed']

    # Execute with Blender
    bpy.ops.render.render(animation=True,scene=Scenename)
    print ("Rendered: f%s n%s i%s" % (render_path, current, config['iteration'][0]))
    time.sleep(2) # let blender finish moving the file

    # update the config file
    config = get_config()
    config['current'] = current
    update_config(config)

