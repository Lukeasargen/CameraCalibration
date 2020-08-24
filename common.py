import os
import numpy as np


def saveCalibration(name, camMtx, distCoef, path=None):
    mtx_path = name + '_camMtx.txt'
    dist_path = name + '_distCoef.txt'

    if path:
        mtx_path = os.path.join(path, mtx_path)
        dist_path = os.path.join(path, dist_path)
    else:
        if not os.path.exists('output'):  # Create the folder if it doesn't exsist
            os.mkdir('output')

        mtx_path = os.path.join('output', mtx_path)
        dist_path = os.path.join('output', dist_path)

    np.savetxt(mtx_path, camMtx, delimiter=',')
    np.savetxt(dist_path, distCoef, delimiter=',')


def loadCalibration(name, path=None):
    """param: name will only look for files in deafult 'output' folder
        param: path is the folder that has the files that match name"""
    mtx_path = name + '_camMtx.txt'
    dist_path = name + '_distCoef.txt'

    if path:
        mtx_path = os.path.join(path, mtx_path)
        dist_path = os.path.join(path, dist_path)
    else:
        mtx_path = os.path.join('output', mtx_path)
        dist_path = os.path.join('output', dist_path)

    camMtx   = np.loadtxt(mtx_path, delimiter=',')
    distCoef   = np.loadtxt(dist_path, delimiter=',')
    if camMtx.size != 0 and distCoef.size != 0:
        return True, camMtx, distCoef
    return False, None, None

