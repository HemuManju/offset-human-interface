import numpy as np
from scipy import spatial


class FormationControl(object):
    """ Formation control primitive using region based shape control.
    Coded by: Apurvakumar Jani, Date: 18/9/2019
    """
    def __init__(self):
        # Initialise the parameters
        return None

    def calculate_vel(self, vehicle, dt, distance_tree, all_drones_pos,
                      min_dis, centroid_pos, alpha, gamma, path_vel, vmax, a,
                      b, knn, formation_type):

        # Get the neighboor position
        curr_pos = vehicle.current_pos[0:2]
        if len(all_drones_pos) < 6:
            knn = len(all_drones_pos)
        peers_pos = all_drones_pos[distance_tree.query(curr_pos, k=knn)[1], :]

        # Calculate the velocity of each neighboor particle
        k = 1 / knn  # constant
        g_lij = (min_dis**2) - np.linalg.norm(
            curr_pos - peers_pos, axis=1, ord=2)
        del_g_ij = 2 * (peers_pos - curr_pos)
        P_ij = k * np.dot(np.maximum(0, g_lij / (min_dis**2))**2, del_g_ij)
        f_g_ij = np.linalg.norm(
            (curr_pos - centroid_pos) / np.array([a, b]), ord=2) - 1

        # Calculate path velocity
        kl = 1  # constant
        del_f_g_ij = 1 * (curr_pos - centroid_pos)
        del_zeta_ij = (kl * max(0, f_g_ij)) * del_f_g_ij
        vel = path_vel - (alpha * del_zeta_ij) - (gamma * P_ij)

        # Calculate the speed
        speed = np.linalg.norm(vel)
        # Normalize the velocity with respect to speed
        if speed > vmax:
            vel = (vel / speed) * vmax

        # New position
        vehicle.updated_pos[0:2] = vehicle.current_pos[0:2] + (vel) * dt

        return vehicle, speed

    def getFeasibleSpeed(self, vel, vel_max):
        """This function limit the velocity returned
        by get_vel function for the stability

        Parameters
        ----------
        vel : float
            Calculated velocity
        vel_max : float
            Maximum allowed velocity
        """
        if vel > 0:
            vel = min(vel_max, vel)
        else:
            vel = max(-vel_max, vel)

        return vel

    def get_parameters(self, n_vehicles):
        a = np.ceil(n_vehicles / 3)
        b = a
        return a, b

    def execute(self, vehicles, next_pos, centroid_pos, dt, formation_type):
        """Get the position of the formation control

        Parameters
        ----------
        vehicles : list
            A list containing UAV or UGV class
        centroid_pos : array
            An array containing the x, y, and z position
        dt : float
            Time step to be used for distance calculation
        """

        # Parameters
        a, b = self.get_parameters(len(vehicles))
        knn = 6
        vmax = vehicles[0].speed
        alpha = 0.5
        gamma = 0.5
        min_dis = 2

        all_drones_pos = np.asarray(
            [vehicle.current_pos[0:2] for vehicle in vehicles])

        # Construct a tree for distance query
        distance_tree = spatial.KDTree(all_drones_pos)

        # Path velocity
        path = np.array([next_pos[0], next_pos[1]]) - centroid_pos
        path_vel = (1 / dt) * path
        if np.linalg.norm(path_vel) > vmax:
            path_vel = (path_vel / np.linalg.norm(path_vel)) * vmax

        # Loop over each drone to calculate the velocity
        vehicles, speed = map(
            list,
            zip(*[
                self.calculate_vel(vehicle, dt, distance_tree, all_drones_pos,
                                   min_dis, centroid_pos, alpha, gamma,
                                   path_vel, vmax, a, b, knn, formation_type)
                for vehicle in vehicles
            ]))
        if np.max(speed) < 0.015 * len(all_drones_pos):
            formation_done = True
        else:
            formation_done = False

        return vehicles, formation_done
