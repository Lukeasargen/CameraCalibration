import time
import sys
import os
import io  # Converting to imagetk without saving
import argparse
from picamera import PiCamera
import tkinter as tk
from PIL import ImageTk, Image
from threading import Thread

CURRENT_DIR_PATH = os.path.dirname(os.path.realpath(__file__))  # Current file directory


class PicamApp():
    def __init__(self, args):
        print("App init.")
        
        # Make directories
        self.saveFolderPath = os.path.join(CURRENT_DIR_PATH, 'images')  # Append the sample folder name
        if not os.path.exists(self.saveFolderPath):  # Create the folder if it doesn't exsist
            os.mkdir(self.saveFolderPath)
        saveDir = "{}_picam_{}x{}".format(args.dir, args.width, args.height)
        self.saveFolderPath = os.path.join(self.saveFolderPath, saveDir)
        if not os.path.exists(self.saveFolderPath):  # Create the folder if it doesn't exsist
            os.mkdir(self.saveFolderPath)

        self.width = args.width        # Full capture width
        self.height = args.height      # Full capture height

        # Calculate resize shape, we don't need to live preview at full resolution
        ratio = args.height / args.width
        self.preview_width = 320
        self.preview_height = int(self.preview_width * ratio)
        print(f"Preview resized to {self.preview_width} by {self.preview_height}")

        self.take_capture = False
        self.quit = False

        self.window = tk.Tk()
        self.window.title("Camera")

        # Make the preview window
        self.preview = tk.Toplevel(self.window)
        self.preview.title('Preview')
        size_str = f"{self.preview_width}x{self.preview_height}"
        self.preview.geometry(size_str)
        self.preview = tk.Label(self.preview)
        self.preview.pack(side = "bottom", fill = "both", expand = "yes")

        # Make the capture button
        self.button_capture = tk.Button(
            self.window, text="Capture", command=self.capture)
        self.button_capture.pack()

        # Make the capture button
        self.button_quit = tk.Button(
            self.window, text="Quit", command=self.end)
        self.button_quit.pack()

    def capture(self):
        self.take_capture = True

    def cam_handler(self):
        # Start camera
        camera = PiCamera()
        # Settings
        camera.resolution = (self.preview_width, self.preview_height)
        print("Opening camera stream.")

        # Live view loop
        live_img = None
        count = 15
        while not self.quit:
            if self.take_capture:
                print("Taking picture.")
                try:
                    camera.resolution = (self.width, self.height)
                    filename = "out_{:03d}.jpg".format(count)
                    print("Saving image : ", filename)
                    imgPath = os.path.join(self.saveFolderPath, filename)
                    camera.capture(
                        output=imgPath,
                        format='jpeg',
                        resize=None,
                        quality=75)
                    count += 1
                except:
                    print("Error saving image.") 
                self.take_capture = False
                camera.resolution = (self.preview_width, self.preview_height)
            else:
                print("Streaming.")
                try:
                    stream = io.BytesIO()
                    camera.capture(stream, format='jpeg')
                    stream.seek(0)
                    temp = Image.open(stream)
                    print("size : ", temp.resolution)
                    temp = ImageTk.PhotoImage(temp)
                    live_img = temp
                except:
                    print("Error Streaming. Ignored.")
                if live_img != None:
                    self.preview.configure(image=live_img) 
                print("Updated preview.")
                # time.sleep(0.1)

    def start_cam(self):
        print("Starting Camera Thread.")
        cam_thread = Thread(target=self.cam_handler)
        cam_thread.start()

    def run(self):
        print("Running app.")
        self.start_cam()
        self.window.mainloop()

    def end(self):
        print("Quitting.")
        self.quit = True
        self.window.destroy()


def main():

    # ----------- PARSE THE INPUTS -----------------
    parser = argparse.ArgumentParser(description="Saves images to dir. \n esc to quit \n spacebar to save the snapshot")
    parser.add_argument("--dir", required=True, default='out', help="folder name to store images")
    parser.add_argument("--width", default=640, type=int, help="width pixels")
    parser.add_argument("--height", default=480, type=int, help="height pixles")
    parser.add_argument("-rpi", "--raspi", default=False, type=bool, help="using raspberry pi")
    args = parser.parse_args()

    app = PicamApp(args)

    app.run()

    print("End main.")

if __name__ == "__main__":
    main()