import yaml
from pathlib import Path
import collections

import ray


@ray.remote
class ParameterServer(object):
    def __init__(self, config):
        self.config = config
        # Blue team behavior
        self.actions = collections.defaultdict(dict)
        self.states = collections.defaultdict(dict)

        # Red team behavior
        self.complexity_actions = collections.defaultdict(dict)
        self.complexity_states = collections.defaultdict(dict)

        # Parameters for pausing and resuming the game
        self.pause = False
        self.resume = True

        # Perforn initial setup
        self._initial_setup()
        self._initial_complexity_setup()
        return None

    def _initial_setup(self):
        # Read fields for all the platoons
        read_path = Path(__file__).parents[0] / 'parameters.yml'
        parameters = yaml.load(open(str(read_path)), Loader=yaml.SafeLoader)

        # Setup the uav platoons
        for i in range(self.config['simulation']['n_uav_platoons']):
            uav_parameters = parameters['uav'].copy()
            key = 'uav_p_' + str(i + 1)
            uav_parameters['platoon_id'] = i + 1
            self.actions['uav'][key] = uav_parameters
            self.states['uav'][key] = uav_parameters

        # Setup the uav platoons
        for i in range(self.config['simulation']['n_ugv_platoons']):
            ugv_parameters = parameters['ugv'].copy()
            key = 'ugv_p_' + str(i + 1)
            ugv_parameters['platoon_id'] = i + 1
            self.actions['ugv'][key] = ugv_parameters
            self.states['ugv'][key] = ugv_parameters
        return None

    def _initial_complexity_setup(self):
        # Read fields for all the platoons
        read_path = Path(__file__).parents[0] / 'complexity.yml'
        parameters = yaml.load(open(str(read_path)), Loader=yaml.SafeLoader)

        # Setup the uav platoons
        for i in range(self.config['simulation']['n_uav_platoons']):
            uav_parameters = parameters['uav'].copy()
            key = 'uav_p_' + str(i + 1)
            uav_parameters['platoon_id'] = i + 1
            self.complexity_actions['uav'][key] = uav_parameters
            self.complexity_states['uav'][key] = uav_parameters

        # Setup the uav platoons
        for i in range(self.config['simulation']['n_ugv_platoons']):
            ugv_parameters = parameters['ugv'].copy()
            key = 'ugv_p_' + str(i + 1)
            ugv_parameters['platoon_id'] = i + 1
            self.complexity_actions['ugv'][key] = ugv_parameters
            self.complexity_states['ugv'][key] = ugv_parameters
        return None

    def set_game_state(self, state):
        if state == 'pause':
            self.pause = True
            self.resume = False
        else:
            self.pause = False
            self.resume = True
        return None

    def get_game_state(self):
        game_state = {'pause': self.pause, 'resume': self.resume}
        return game_state

    def get_actions(self, complexity=False):
        if complexity:
            return self.complexity_actions
        else:
            return self.actions

    def set_action(self, action, complexity=False):
        vehicle_type = action['vehicles_type']
        key = vehicle_type + '_p_' + str(action['platoon_id'])
        if complexity:
            self.complexity_actions[vehicle_type][key] = action
        else:
            self.actions[vehicle_type][key] = action
        return None

    def update_actions(self, actions_uav, actions_ugv):
        self.actions['uav'].update(actions_uav)
        self.actions['ugv'].update(actions_ugv)
        return None

    def set_state(self, state, complexity=False):
        vehicle_type = state['vehicles_type']
        key = vehicle_type + '_p_' + str(state['platoon_id'])
        if complexity:
            self.complexity_states[vehicle_type][key] = state
        else:
            self.states[vehicle_type][key] = state
        return None

    def get_states(self, complexity=False):
        if complexity:
            return self.complexity_states
        else:
            return self.states
