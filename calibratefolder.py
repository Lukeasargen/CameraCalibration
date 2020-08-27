"""https://docs.opencv.org/master/dc/dbb/tutorial_py_calibration.html"""

import os
import time
import argparse
import numpy as np
import cv2
import multiprocessing

from common import saveCalibration, loadCalibration

CURRENT_DIR_PATH = os.path.dirname(os.path.realpath(__file__))  # Current file directory

def process_image(filename, width, height):
    img = cv2.imread(filename)

    if img is None:  # Check if the file could be opened
        print("Image failed to load :", filename)
        return None

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (width, height), None)

    # If found, add object points, image points (after refining them)
    if ret:
        # Termination criteria for finding the sub pixel coordinates of corners (cornerSubPix)
        criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 40, 0.001)

        # Increase the pixel location accuracy
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        return corners2

    print("No chessboard : ", filename)
    return None


def calibrateFromFolder(folderName, width, height, squareSize, num_threads=1):
    """ Apply camera calibration operation for images in the given array.\n
        param: squareSize = actual checker board square dimensions in meters\n
        param: cornersWidth, cornersHeight = number of internal corners\n
        (ie. chess board is cornersWidth=7, cornersHeight=7)\n
        return: [ret, mtx, dist, rvecs, tvecs]"""

    t0 = time.time()

    # Load the image file paths
    samplesPath = os.path.join(CURRENT_DIR_PATH, 'images', folderName)  # Append the sample folder name
    imageFilePaths = []  # Holds the path to the images
    validImageTypes = [".jpg", ".jpeg", ".JPG", ".JPEG", ".png",".PNG"]  # Types of images to check for

    # Append valid sample images to the array
    for f in os.listdir(samplesPath):  # Look through every file in the sample folder
        ext = os.path.splitext(f)[1]  # Get extension
        if ext.lower() in validImageTypes:  # Check for valid image types
            imagePath = os.path.join(samplesPath, f)
            imageFilePaths.append(imagePath)

    # We need a matrix that represents 3d coordinates of a checkerboard pattern
    # We assume the checker pattern is kept in the Z=0 plane and the camera is moved and rotated
    # Prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((height*width, 3), np.float32)
    objp[:, :2] = np.mgrid[0:width, 0:height].T.reshape(-1, 2)

    # Scale the 3d points to the actual dimensinos
    objp = objp*squareSize

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in  world space
    imgpoints = []  # 2d points in image plane
    
    t1 = time.time()

    if num_threads > multiprocessing.cpu_count():
        num_threads = multiprocessing.cpu_count()
    num_threads = int(num_threads)
    print("Threads :", num_threads)

    if num_threads <= 1:
        pixel_points = [process_image(f, width, height) for f in imageFilePaths]
    else:
        pool = multiprocessing.Pool(num_threads)

        from functools import partial
        target = partial(process_image, width=width, height=height)

        pixel_points = pool.map(target, imageFilePaths)

    imgpoints = [p for p in pixel_points if p is not None]

    if len(imgpoints) < 9:
        print("Calibration Failed")
        print("Less than 9 good images.")
        print("Check the dimensions of your checkerboard")
        return None, None, None, None, None

    print("Using {} images to calibrate".format(len(imgpoints)))

    [objpoints.append(objp) for i in range(len(imgpoints))]

    print("Calculate Image Points : {:.4f} seconds.".format(time.time() - t1))

    t2 = time.time()
    # ------------ Calibrate ------------
    # ret = RMS re-projection error
    # mtx = (3, 3) camera matrix (focal lengths and optic center)
    # dist = (1, 5) distortion coefficients (column vector [k1 k2 p1 p2 k3])
    # rvecs = rotation matrix estimate for each pattern
    # tvecs = translation matrix for each pattern
    img = cv2.imread(imageFilePaths[0])
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, img.shape[1::-1], None, None)
    print("Calculate Intrinsics : {:.4f} seconds.".format(time.time() - t2))

    print("\nCalibration Complete")
    print("RMS:", ret)
    print("Camera Matrix:\n", mtx)
    print("Distortion Coefficients:\n", dist.ravel())

    # Re-projection error
    mean_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
        mean_error += error
    print("Mean reprojection error: {}".format(mean_error/len(objpoints)) )

    print("Total Duration : {:.4f} seconds.".format(time.time() - t0))

    return [ret, mtx, dist, rvecs, tvecs]


def undistortFolder(folderName, mtx, dist, alpha):
    """ Undistort and save the images in the given folder.\n
        param: folderName = folder in the same directory as this file\n
        param: mtx and dist from calibrate\n
        param: alpha is the amount of unwatned pixels kept"""

    # Load the image file paths
    samplesPath = os.path.join(CURRENT_DIR_PATH, folderName)  # Append the sample folder name
    undistoredFilePaths = []  # Where the image will be saved
    imageFilePaths = []  # Holds the path to the images
    validImageTypes = [".jpg", ".jpeg", ".JPG", ".JPEG", ".png",".PNG"]  # Types of images to check for

    # Create the undistorted folder
    newFolderName = samplesPath + "_undistorted"
    saveFolderPath = os.path.join(CURRENT_DIR_PATH, newFolderName)  # Append the sample folder name
    
    if not os.path.exists(saveFolderPath):  # Create the folder if it doesn't exsist
        os.mkdir(saveFolderPath)
    print("\nSave folder path : ", saveFolderPath)

    # Append valid sample images to the array
    for f in os.listdir(samplesPath):  # Look through every file in the sample folder
        fileNameSplit = os.path.splitext(f)  # Get extension
        if fileNameSplit[1].lower() in validImageTypes:  # Check extension for valid image types
            imagePath = os.path.join(samplesPath, f)
            imageFilePaths.append(imagePath)
            # Create the undistorted file path
            newFileName = fileNameSplit[0] + "_undistorted" + fileNameSplit[1]
            newImagePath = os.path.join(saveFolderPath, newFileName)
            undistoredFilePaths.append(newImagePath)
    
    # Use the first image to redefine the matrix and define roi
    img = cv2.imread(imageFilePaths[0])
    h,  w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix=mtx,
                                                    distCoeffs=dist,
                                                    imageSize=(w, h),
                                                    alpha=alpha,
                                                    newImgSize=(w, h))

    print("\nNew Camera Matrix")
    print("Camera Matrix:\n", newcameramtx)
    print("Original Shape: ", img.shape[:2])
    print("roi:", roi)

    for i in range(len(imageFilePaths)):
        # Load the current image
        img = cv2.imread(imageFilePaths[i])

        if img is None:  # Check if the file could be opened
            print("Image failed to load :", imageFilePaths[i])
            continue

        # Undistort
        dst = cv2.undistort(img, mtx, dist, None)  # newcameramtx
        # mapx, mapy = cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtx,(w,h),5)
        # dst = cv2.remap(img,mapx,mapy,cv2.INTER_LINEAR)

        # Crop the image using undistorted
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]
        cv2.imwrite(undistoredFilePaths[i], dst)
        # cv2.imshow('img', dst)
        # cv2.waitKey(100)

    print("Undistortion Complete")


def main():

    parser = argparse.ArgumentParser(description='Camera calibration')
    parser.add_argument('-c', action="store_true", help='use the images from img_folder to do camera calibration')
    parser.add_argument('-u', action="store_true", help='undistort the images from img_folder')
    parser.add_argument('--dir', type=str, required=True, help='image directory path and config save name, default is "samples"')
    parser.add_argument('--size', type=float, default=1,  help='square side length in meters, deafult is 1')
    parser.add_argument('--ncols', type=int, default=9, help='number of internal corners of the long side, default is 7')
    parser.add_argument('--nrows',type=int, default=6, help='number of internal corners of the short side, default is 6')
    parser.add_argument('--threads', type=float, default=1, help='use more cores')
    parser.add_argument('--alpha', type=float, default=0, help='alpha is the amount of unwanted pixels kept, range:[0,1], default is 0 keeps all pixels')
    args = parser.parse_args()

    inputFolderPath = os.path.join(CURRENT_DIR_PATH, 'images', args.dir)
    
    if not os.path.exists(inputFolderPath):
        print("Folder does no exsist : {}".format(inputFolderPath))
        print("Folder format : --dir={name}_['picam', 'cv2']_{width}x{height}")
        return

    if args.c:
        print("Calibrating images in '{}'".format(args.dir))
        ret, camMtx, distcoef, rvecs, tvecs = calibrateFromFolder(inputFolderPath, args.ncols, args.nrows, args.size, args.threads)
        if ret:
            saveCalibration(args.dir, camMtx, distcoef)
    elif args.u:
        print("Undistorting images in '{}'".format(args.dir))
        ok, camMtx, distcoef = loadCalibration(args.dir)
        if ok:
            print("\nLoaded Values")
            print("Camera Matrix:\n", camMtx)
            print("Distortion Coefficients:\n", distcoef.ravel())
            undistortFolder(inputFolderPath, camMtx, distcoef, args.alpha)
        else:
            print("Failed to undistort folder.")
            print("Could not load the Camera Matrix and Distortion Coefficients")
            print("Check your spelling")
    else:
        print("Select -c to calibrate or -u to undistort.")


if __name__ == "__main__":
    main()