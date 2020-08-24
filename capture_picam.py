import time
import sys
import os
import argparse

import keyboard  # pip install keyboard
from picamera import PiCamera


CURRENT_DIR_PATH = os.path.dirname(os.path.realpath(__file__))  # Current file directory

def save_live(args):

    # Start camera
    camera = PiCamera()

    # Set resolution
    camera.resolution = (args.width, args.height)

    # Make directories
    saveFolderPath = os.path.join(CURRENT_DIR_PATH, 'images')  # Append the sample folder name
    
    if not os.path.exists(saveFolderPath):  # Create the folder if it doesn't exsist
        os.mkdir(saveFolderPath)

    saveDir = "{}_picam_{}x{}".format(args.dir, width, height)

    saveFolderPath = os.path.join(saveFolderPath, saveDir)

    if not os.path.exists(saveFolderPath):  # Create the folder if it doesn't exsist
        os.mkdir(saveFolderPath)

     # Live view loop
    count = 0
    camera.start_preview()
    while True:
        if keyboard.is_pressed('q'):  # esc
            print("q pressed. Quitting.")
            break
        if keyboard.is_pressed('c'):
            try:
                filename = "out_{:03d}.jpg".format(count)
                print("Saving image : ", filename)
                imgPath = os.path.join(saveFolderPath, filename)
                camera.capture(
                    output=imgPath,
                    format='jpeg',
                    resize=None,
                    quality=75)
                count += 1
            except:
                print("Error saving image.")

    camera.stop_preview()


def main():

    # ----------- PARSE THE INPUTS -----------------
    parser = argparse.ArgumentParser(description="Saves images to dir. \n esc to quit \n spacebar to save the snapshot")
    parser.add_argument("--dir", required=True, default='out', help="folder name to store images")
    parser.add_argument("--width", default=640, type=int, help="width pixels")
    parser.add_argument("--height", default=480, type=int, help="height pixles")
    parser.add_argument("-rpi", "--raspi", default=False, type=bool, help="using raspberry pi")
    args = parser.parse_args()

    save_live(args)

    print("End main.")

if __name__ == "__main__":
    main()