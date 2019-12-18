import numpy as np
from scipy.spatial.distance import cdist


def findkeys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findkeys(j, kv):
                yield x


class ChaseIt():
    """This Class is to perform the chasing behaviour in the red team
    """
    def __init__(self, config):
        self.config = config

        return None

    def check_perimeter(self, red_team_pos, blue_team_pos):
        """This function checks if the blue team are near red teams using the centroid

        Parameters
        ----------
        red_team_pos : list
            A dictionary containing the states of the red team
        blue_team_pos : list
            A dictionary containing the states of the blue team

        Returns
        -------
        array
            A array mask containing which blue teams are near to red team
        """
        distance = cdist(red_team_pos, blue_team_pos)
        threshold = self.config['experiment']['perimeter_distance']
        indices = np.argwhere(distance < threshold)
        return indices

    def chase(self, red_team_actions, red_team_pos, blue_team_pos):
        """This function sets the red team actions according to the
        red and blue team state

        Parameters
        ----------
        red_team_actions : list
            A dictionary containing all the states of the red team
        red_team_pos : list
            A dictionary containing the centroids of the red team
        blue_team_pos : dict
            A dictionary containing the centroids of the blue team

        Returns
        -------
        dict
            A dictionary of updated actions for the red team
        """
        indices = self.check_perimeter(red_team_pos, blue_team_pos)
        selected = {}
        for index in indices:
            if index[0] <= 2:
                red_team_key = 'uav_p_' + str(index[0] % 3 + 1)
                blue_team_key = 'uav_p_' + str(index[1] % 3 + 1)
                selected[red_team_key] = blue_team_key
            else:
                red_team_key = 'ugv_p_' + str(index[0] % 3 + 1)
                blue_team_key = 'ugv_p_' + str(index[1] % 3 + 1)
                selected[red_team_key] = blue_team_key
        # print(selected)
        return None
