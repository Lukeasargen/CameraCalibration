import time
import sys
import os
import argparse

import cv2

CURRENT_DIR_PATH = os.path.dirname(os.path.realpath(__file__))  # Current file directory

def save_live(args):

    if args.raspi:
        os.system('sudo modprobe bcm2835-v4l2')  # make an X window

    # Start camera
    cap = cv2.VideoCapture(0)

    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    # Make directories
    saveFolderPath = os.path.join(CURRENT_DIR_PATH, 'images')  # Append the sample folder name
    
    if not os.path.exists(saveFolderPath):  # Create the folder if it doesn't exsist
        os.mkdir(saveFolderPath)

    saveDir = "{}_cv2_{}x{}".format(args.dir, width, height)

    saveFolderPath = os.path.join(saveFolderPath, saveDir)

    if not os.path.exists(saveFolderPath):  # Create the folder if it doesn't exsist
        os.mkdir(saveFolderPath)

    # Live view loop
    count = 0
    while True:
        ret, frame = cap.read()

        cv2.imshow('camera', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # esc
            break
        if key == ord(' '):
            try:
                filename = "out_{:03d}.jpg".format(count)
                print("Saving image : ", filename)
                imgPath = os.path.join(saveFolderPath, filename)
                cv2.imwrite(imgPath, frame)
                count += 1
            except:
                print("Error saving image.")

    cap.release()
    cv2.destroyAllWindows()


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