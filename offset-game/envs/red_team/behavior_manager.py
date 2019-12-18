import yaml
from pathlib import Path
import collections
import time

from scipy.spatial.distance import cdist

import numpy as np

from .strategy.patrol import Patrol
from .strategy.chase import ChaseIt


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


class BehaviourManager(object):
    def __init__(self, state_manager):
        self.config = state_manager.config
        self.state_manager = state_manager
        self.default_actions = collections.defaultdict(dict)

        # Behaviours
        self.chase = ChaseIt(self.state_manager.config)
        self.patrol = Patrol(self.state_manager.config)

        self._initial_default_actions()
        return None

    def _initial_default_actions(self):
        # Read fields for all the platoons
        read_path = Path(__file__).parents[0] / 'config.yml'
        config = yaml.load(open(str(read_path)), Loader=yaml.SafeLoader)

        # Setup the uav platoons
        for i in range(self.config['simulation']['n_uav_platoons']):
            uav_attributes = config['uav'].copy()
            key = 'uav_p_' + str(i + 1)
            uav_attributes['platoon_id'] = i + 1

            # Get the node position
            node_info = self.state_manager.node_info(
                config['uav_platoon']['initial_nodes_pos'][i])
            uav_attributes['target_pos'] = node_info['position']

            # Update the uav action
            self.default_actions['uav'][key] = uav_attributes

        # Setup the uav platoons
        for i in range(self.config['simulation']['n_ugv_platoons']):
            ugv_attributes = config['ugv'].copy()
            key = 'ugv_p_' + str(i + 1)
            ugv_attributes['platoon_id'] = i + 1

            # Get the node position
            node_info = self.state_manager.node_info(
                config['ugv_platoon']['initial_nodes_pos'][i])
            uav_attributes['target_pos'] = node_info['position']

            # Update the ugv action
            self.default_actions['ugv'][key] = ugv_attributes

    def get_default_actions(self):
        return self.default_actions['uav'], self.default_actions['ugv']

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
        distance = cdist(blue_team_pos, red_team_pos)
        threshold = self.config['experiment']['perimeter_distance']
        indices = np.argwhere(distance < threshold)
        return indices

    def choose_actions(self, red_team_attr, blue_team_attr):
        red_team_pos = list(findkeys(red_team_attr, 'centroid_pos'))
        blue_team_pos = list(findkeys(blue_team_attr, 'centroid_pos'))

        index = self.chase.chase([], red_team_pos, blue_team_pos)
