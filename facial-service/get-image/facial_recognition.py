import qi
import argparse
import sys
import time
import vision_definitions
import naoqi


def main(session):
    """
    This is just an example script that shows how images can be accessed
    through ALVideoDevice in Python.
    Nothing interesting is done with the images in this example.
    """
    # Get the service ALVideoDevice.

    video_service = session.service("ALVideoDevice")

    # Register a Generic Video Module
    resolution = vision_definitions.kQQVGA
    colorSpace = vision_definitions.kYUVColorSpace
    print(colorSpace)
    fps = 20

    nameId = video_service.subscribe("python_GVM", resolution, colorSpace, fps)

    print('getting images in remote')
    for i in range(0, 20):
        print("getting image " + str(i))
        img = video_service.getImageRemote(nameId)
        print(img)
        time.sleep(0.05)

    video_service.unsubscribe(nameId)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="169.254.161.107",
                        help="Robot IP address. On robot or Local Naoqi: use '169.254.161.107'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    print("done")
    print(vision_definitions)
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session)