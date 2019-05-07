import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps
import time
import sys
import os
import time
import logging
import boto3
from botocore.exceptions import ClientError

detected = False
processing = False
takePicture = False

def upload_file(file_name, bucket, object_name=None):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def on_new_camera_image(evt, **kwargs):
    global processing
    global takePicture
    global detected
    if takePicture:
        if not processing:
            print('takepicture is true')
            if detected:
                print('Taking a picture of it...')
                processing = True            
                #print('Invoke OpenWhisk at ...')
                #print(datetime.datetime.now().time())
                #print(kwargs['image'].image_number)
                pilImage = kwargs['image'].raw_image
                pilImage.save("pictures/fromcozmo.jpg", "JPEG")  
                time.sleep(2)
                print('Waiting for image...')
                if upload_file('pictures/fromcozmo.jpg','ctec280'):
                    print('File uploaded successfully!') 


def on_new_pet_detected(evt, **kwargs):
    #for key, value in kwargs.items():
    #     print("{0} = {1}".format(key, value))
    print('I see a',kwargs['pet'].pet_type)
    global detected
    global processing
    global takePicture
    detected = True
    takePicture = True


def cozmo_program(robot: cozmo.robot.Robot):
    robot.set_head_angle(degrees(10.0)).wait_for_completed()
    robot.set_lift_height(0.0).wait_for_completed()
    global directory
    # directory = sys.argv[1]
    if not os.path.exists('pictures'):
        os.makedirs('pictures')

    robot.add_event_handler(cozmo.pets.EvtPetAppeared, on_new_pet_detected)
    robot.add_event_handler(cozmo.world.EvtNewCameraImage, on_new_camera_image)

    while not detected:
    #  robot.turn_in_place(degrees(45))
       time.sleep(5)

    if detected == True:    
        robot.drive_straight(distance_mm(250), speed_mmps(150)).wait_for_completed()


cozmo.run_program(cozmo_program, use_viewer=True, force_viewer_on_top=True)
