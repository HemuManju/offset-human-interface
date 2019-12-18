import math

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def interpcurve(N, pX, pY):
    """Interpolate evenly spaced points on a spline

    Parameters
    ----------
    N : int
        Number of evenly spaced points
    pX : array
        An array of x co-ordinates
    pY : array
        An array of y co-ordinates

    Returns
    -------
    array
        A array with evenly spaced points on the spline.
    """
    # Equally spaced in arclength
    N = np.transpose(np.linspace(0, 1, N))

    # How many points will be uniformly interpolated?
    nt = N.size

    # Number of points on the curve
    n = pX.size
    pxy = np.array((pX, pY)).T
    p1 = pxy[0, :]
    pend = pxy[-1, :]
    last_segment = np.linalg.norm(np.subtract(p1, pend))
    epsilon = 10 * np.finfo(float).eps

    # If the two end points are not close enough lets close the curve
    if last_segment > epsilon * np.linalg.norm(np.amax(abs(pxy), axis=0)):
        pxy = np.vstack((pxy, p1))
        nt = nt + 1
    else:
        print('Contour already closed')
    pt = np.zeros((nt, 2))

    # Compute the chordal arclength of each segment.
    chordlen = (np.sum(np.diff(pxy, axis=0)**2, axis=1))**(1 / 2)
    # Normalize the arclengths to a unit total
    chordlen = chordlen / np.sum(chordlen)
    # Cumulative arclength
    cumarc = np.append(0, np.cumsum(chordlen))
    tbins = np.digitize(N, cumarc)  # bin index in which each N is in

    # Catch any problems at the ends
    tbins[np.where(tbins <= 0 | (N <= 0))] = 1
    tbins[np.where(tbins >= n | (N >= 1))] = n - 1

    s = np.divide((N - cumarc[tbins]), chordlen[tbins - 1])
    pt = pxy[tbins, :] + np.multiply((pxy[tbins, :] - pxy[tbins - 1, :]),
                                     (np.vstack([s] * 2)).T)

    return pt


def haversine_dist(init_point, final_point):
    """Gives the Haversine distance between the initial and final point

    Parameters
    ----------
    init_point : array
        The initial point
    final_point : array
        The final point

    Returns
    -------
    float
        The Haversine distance
    """

    # Assuming the input is in degrees
    init_rad = init_point * math.pi / 180
    final_rad = final_point * math.pi / 180

    d_latitude = final_rad[0] - init_rad[0]
    d_longitude = final_rad[1] - init_rad[1]
    x = (d_longitude) * math.cos((final_rad[0] - init_rad[0]) / 2)
    y = d_latitude

    return [x * 6356.752e3, y * 6356.752e3]


def get_xy_position(config):
    """Get the x and y position of all the buildings
    """
    read_path = config['map_data_path'] + 'latitude_longitude.csv'
    data = np.genfromtxt(read_path, delimiter=',', skip_header=True)

    init_point = data[0]
    xy_pos = np.ones((data.shape[0], 3))
    for i, item in enumerate(data):
        temp_x = item.copy()
        xy_pos[i, 0:2] = haversine_dist(init_point, temp_x)

    # Rotation angle
    t = math.pi / 2 + math.atan2(114.2746 - 184.137, -67.67721 + 82.2549)
    rot = np.asarray([[math.cos(t), -math.sin(t), 0],
                      [math.sin(t), math.cos(t), 0], [0, 0, 1]])
    xy_pos = np.matmul(xy_pos, rot)

    plt.scatter(xy_pos[:, 0], xy_pos[:, 1])
    plt.show()
    df = pd.DataFrame(xy_pos, columns=['x', 'y'])
    filepath = config['map_save_path'] + 'co_ordinates.xlsx'
    df.to_excel(filepath, index=False)

    return None
