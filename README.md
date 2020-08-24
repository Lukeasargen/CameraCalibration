
### Capturing cli examples
```
# Arducam 5MP M12 lens
python3 capture_picam.py --dir picamv21 --width 2592 --height 1944
# picam v2.1 8MP Pinhole lens
python3 capture_picam.py --dir arducam --width 3280 --height 2464
# Opencv VideoCapture (idk what crop of the sensor it uses so you should calibrate with opencv captures to get better results in opencv scripts)
python3 capture_opencv.py --dir picamv21 --width 640 --height 480
```

##### add `-rpi` when runing capture on raspberry pi, does the following:
installs the driver found here: [https://github.com/raspberrypi/linux/tree/rpi-4.14.y/drivers/staging/vc04_services/bcm2835-camera](https://github.com/raspberrypi/linux/tree/rpi-4.14.y/drivers/staging/vc04_services/bcm2835-camera)

the script runs `sudo modprobe bcm2835-v4l2`

_you may have to use `sudo nano /etc/ modules` then add the line `bcm2835-v4l2`_

This driver helps with the live view and videoX

### Calibration cli example
```
python calibratefolder.py --dir=picamv21_picam_3280x2464 --size 1 -c
```

### Undistort cli example
```
python calibratefolder.py --dir=arducam_opencv_2592x1944 -u
```
