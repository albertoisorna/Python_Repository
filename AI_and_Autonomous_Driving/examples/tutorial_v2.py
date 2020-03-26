#!/usr/bin/env python

# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

import glob
import os
import sys

IM_WIDTH = 800
IM_HEIGHT = 600
IM_WIDTH = 640
IM_HEIGHT = 480

sys.path.append("D:\CARLA_0.9.5")

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

import random
import time
import numpy as np
import cv2

import matplotlib.pyplot as plt


import PySimpleGUI as sg            # Uncomment 1 to run on that framework
# import PySimpleGUIQt as sg        # runs on Qt with no other changes
# import PySimpleGUIWeb as sg       # has a known flicker problem that's being worked
import cv2



def process_img(image,window):
    i = np.array(image.raw_data)
    i2 = i.reshape((IM_HEIGHT, IM_WIDTH, 4))
    i3 = i2[:, :, :3]
    #cv2.imshow("",i3)
    #event, values = window.Read(timeout=20, timeout_key='timeout')
    i3=cv2.imencode('.png', i3)[1].tobytes()     # Convert the image to PNG Bytes
    window.FindElement('_IMAGE_').Update(data=i3)   # Change the Image Element to show the new image
    #plt.imshow(i3)
    #plt.show()
    #cv2.waitKey(1)
    #return (i3/255.0)

def process2(image):
    array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
    array = np.reshape(array, (image.height, image.width, 4))
    array = array[:, :, :3]
    array = array[:, :, ::-1]
    pygame.surfarray.make_surface(array.swapaxes(0, 1))

actor_list = []

def main():
    

    # In this tutorial script, we are going to add a vehicle to the simulation
    # and let it drive in autopilot. We will also create a camera attached to
    # that vehicle, and save all the images generated by the camera to disk.

    try:
        # First of all, we need to create the client that will send the requests
        # to the simulator. Here we'll assume the simulator is accepting
        # requests in the localhost at port 2000.
        # define the window layout
        #layout = [[sg.Image(filename='', key='_IMAGE_')]]
        
        # create the window and show it without the plot
        #window = sg.Window('Demo Application - OpenCV Integration', layout, location=(IM_WIDTH,IM_HEIGHT))
        time.sleep(2)
        event, values = window.Read(timeout=20, timeout_key='timeout')
        if event is None:
            return
    
        

        
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)

        # Once we have a client we can retrieve the world that is currently
        # running.
        world = client.get_world()

        # The world contains the list blueprints that we can use for adding new
        # actors into the simulation.
        blueprint_library = world.get_blueprint_library()

        # Now let's filter all the blueprints of type 'vehicle' and choose one
        # at random.
        bp = random.choice(blueprint_library.filter('vehicle.tesla.*'))

        # A blueprint contains the list of attributes that define a vehicle's
        # instance, we can read them and modify some of them. For instance,
        # let's randomize its color.
        if bp.has_attribute('color'):
            color = random.choice(bp.get_attribute('color').recommended_values)
            bp.set_attribute('color', color)
        
        # establecemos posicion
        mx,my,mz = (50,-140,10)
        transform = carla.Transform(carla.Location(x=mx, y=my, z=mz), carla.Rotation(yaw=180))
        
        # So let's tell the world to spawn the vehicle.
        vehicle = world.try_spawn_actor(bp, transform)
        vehicle.apply_control(carla.VehicleControl(throttle=0.05, steer=0.0))
        
        if vehicle == None: 
            print("error")
        
        print(transform)

        # It is important to note that the actors we create won't be destroyed
        # unless we call their "destroy" function. If we fail to call "destroy"
        # they will stay in the simulation even after we quit the Python script.
        # For that reason, we are storing all the actors we create so we can
        # destroy them afterwards.
        actor_list.append(vehicle)
        print('created %s' % vehicle.type_id)

        # Let's put the vehicle to drive around.
        vehicle.set_autopilot(True)
        vehicle.apply_control(carla.VehicleControl(throttle=0.1, steer=0.0))        
        # Let's add now a "depth" camera attached to the vehicle. Note that the
        # transform we give here is now relative to the vehicle.
        
        # creamos
        #camera_bp = blueprint_library.find('sensor.camera.depth')
        #camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
        # establecemos dimension
        camera_bp.set_attribute('image_size_x', f'{IM_WIDTH}')
        camera_bp.set_attribute('image_size_y', f'{IM_HEIGHT}')
        camera_bp.set_attribute('fov', '120')
        camera_bp.set_attribute('sensor_tick', '0.3')
        # ajustamos posicion
        camera_transform = carla.Transform(carla.Location(x=-0.05,y=-0.4, z=1.2), carla.Rotation())
        #camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
        
        # lo anadimos
        actor_list.append(camera)
        print('created %s' % camera.type_id)

        # do something with this sensor
        time.sleep(2)
        camera.listen(lambda data: process2(data))
        
        time.sleep(12)

    finally:
        
        print('destroying actors')
        for actor in actor_list:             
            actor.destroy()
        print('done.')
        cv2.destroyAllWindows()

if __name__ == '__main__':

    main()
