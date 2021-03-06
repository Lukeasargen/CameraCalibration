
Based off the OpenCV-Python tutorial here : [https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html)

### Capturing
```
# Arducam 5MP M12 lens
python3 capture_picam_app.py --dir arducam --width 2592 --height 1944

# picam v2.1 8MP Pinhole lens
python3 capture_picam_app.py --dir picamv21 --width 3280 --height 2464

# Opencv VideoCapture (idk what crop of the sensor it uses so you should calibrate on the cropped images to get better results in opencv scripts)
python3 capture_opencv.py --dir picamv21 --width 640 --height 480
```

##### Use the `-rpi` argument when runing capture on raspberry pi. Does the following:
the script runs `sudo modprobe bcm2835-v4l2` which 
installs the driver found here: [https://github.com/raspberrypi/linux/tree/rpi-4.14.y/drivers/staging/vc04_services/bcm2835-camera](https://github.com/raspberrypi/linux/tree/rpi-4.14.y/drivers/staging/vc04_services/bcm2835-camera)


_you may have to edit `/etc/modules` to add the line `bcm2835-v4l2`_

This driver is for the video capture.

#### X11 Forwarding over ssh

##### Windows Client : 
Run [Xming app](https://sourceforge.net/projects/xming/) in background. I use XLaunch, selecting multiple windows, Display number 0, Start no client, check Clipboard, then finish to start the service.

Use PuTTY for the rest unless you want to deal with default windows ssh. Enable x11 : Connection > SSH > X11 > Enable X11 forwarding.

##### Linux Server :

Test for x11 by installing xauth and xll-apps : `sudo apt-get install xauth x11-apps`

Run `xclock` to test the install and forwarding. If it works then you're done.

On the server edit `/etc/ssh/sshd_config` to include these lines:
```
X11Forwarding yes
X11DisplayOffset 10
X11UseLocalhost no
```
Restart ssh (ubuntu, debian) : `sudo systemctl restart ssh.service`

<!-- Export the display to client :

`$ export DISPLAY=client_ip:0.0`
```
DISPLAY=":0
export DISPLAY
``` -->


### Calibration
```
python3 calibratefolder.py --dir=picamv21_cv2_640x480 -c
python calibratefolder.py --dir=picamv21_picam_3280x2464 -c --threads 4
```

### Undistort
```
python calibratefolder.py --dir=arducam_cv2_2592x1944 -u
```
