import collections

import ray

from default_actions.default_actions import red_team_actions, blue_team_actions


@ray.remote
class ParameterServer(object):
    def __init__(self, config, team_type):
        self.uav = []
        self.ugv = []
        self.grid_map = []
        self.user_input = []
        self.map_pos = []

        self.config = config
        # Blue team behavior
        self.blue_actions = collections.defaultdict(dict)
        self.blue_states = collections.defaultdict(dict)

        # Red team behavior
        self.red_actions = collections.defaultdict(dict)
        self.red_states = collections.defaultdict(dict)

        # Goal parameters
        self.goal = False
        self.indoorgoal = False

        # Parameters for pausing and resuming the game
        self.pause = False
        self.resume = True
        self.baseline = False

        # Score Parameters
        self.score = 10000

        # Default red team type is None
        self._initial_setup(team_type)
        return None

    def _initial_setup(self, team_type):
        red_actions = red_team_actions(self.config, team_type)
        self.red_actions['uav'] = red_actions['uav']
        self.red_actions['ugv'] = red_actions['ugv']

        # Set blue actions
        blue_actions = blue_team_actions(self.config)
        self.blue_actions['uav'] = blue_actions['uav']
        self.blue_actions['ugv'] = blue_actions['ugv']
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

    def set_baseline(self, state):
        self.baseline = state

    def get_baseline(self):
        return self.baseline

    def get_action(self, complexity=False):
        if complexity:
            return self.red_actions
        else:
            return self.blue_actions

    def set_action(self, action, complexity=False):
        vehicle_type = action['vehicles_type']
        key = vehicle_type + '_p_' + str(action['platoon_id'])
        if complexity:
            self.red_actions[vehicle_type][key] = action
        else:
            self.blue_actions[vehicle_type][key] = action
        return None

    def update_actions(self, actions_uav, actions_ugv):
        self.blue_actions['uav'].update(actions_uav)
        self.blue_actions['ugv'].update(actions_ugv)
        return None

    def set_state(self, state, complexity=False):
        vehicle_type = state['vehicles_type']
        key = vehicle_type + '_p_' + str(state['platoon_id'])
        if complexity:
            self.red_states[vehicle_type][key] = state
        else:
            self.blue_states[vehicle_type][key] = state
        return None

    def get_state(self, complexity=False):
        if complexity:
            return self.red_states
        else:
            return self.blue_states

    def set_user_input(self, data):
        self.user_input = data
        return None

    def get_user_input(self):
        return self.user_input

    def set_goal_status(self):
        self.goal = True
        return

    def get_goal_status(self):
        return self.goal

    def get_indoor_goal_status(self):
        return self.indoorgoal

    def set_indoor_goal_status(self):
        self.indoorgoal = True
        return

    def get_score(self):
        return self.score

    def set_score(self, penalty):
        self.score = self.score - penalty
        return

    def set_goal_node(self, node):
        self.node = node

    def get_goal_node(self):
        return self.node

    def get_map_pos(self):
        return self.map_pos

    def set_map_pos(self, map_pos):
        self.map_pos = map_pos
