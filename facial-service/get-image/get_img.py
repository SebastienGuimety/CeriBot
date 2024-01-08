#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Get an image. Display it and save it using PIL."""
import signal
import qi
import argparse
import sys
import time
from PIL import Image
from naoqi import ALProxy
import os


IP = "192.168.13.90"

def get_image(video_service, videoClient, image_name):
    naoImage = video_service.getImageRemote(videoClient)
    imageWidth = naoImage[0]
    imageHeight = naoImage[1]
    array = naoImage[6]
    image_string = str(bytearray(array))

    # Create a PIL Image from our pixel array.
    im = Image.frombytes("RGB", (imageWidth, imageHeight), image_string)

    # Save the image.
    if os.path.exists('{}.png'.format(image_name)):
        os.remove('{}.png'.format(image_name))
    im.save(image_name, "PNG")

def wakeup():
    motion = ALProxy("ALMotion", IP, 9559)
    motion.wakeUp()

    print("wake up")

def main(session):
    """
    First get an image, then show it on the screen with PIL.
    """
    # Get the service ALVideoDevice.

    video_service = session.service("ALVideoDevice")
    resolution = 2    # VGA
    colorSpace = 11   # RGB

    videoClient = video_service.subscribe("python_client1", resolution, colorSpace, 5)
    t0 = time.time()


    t1 = time.time()

    # Time the image transfer.
    print("acquisition delay ", t1 - t0)

    i = 0
    while True:
        i += 1
        time.sleep(0.01)
        get_image(video_service, videoClient, image_name="img/currentImg.png")


if __name__ == "__main__":
    # wakeup()

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default=IP,
                        help='Robot IP address. On robot or Local Naoqi: use {}.'.format(IP))
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        print("try to connect")
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    print("done")
    # def kill(signum, frame):
    #     global kill_now
    #     kill_now = True
    #
    # kill_now = False
    # signal.signal(signal.SIGTERM, kill)
    # while not kill_now:
    #     time.sleep(1)
    # print("done")
    # motion.rest()
    main(session)
