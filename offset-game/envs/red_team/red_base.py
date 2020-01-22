import time
from pathlib import Path
import yaml

import numpy as np

import ray

from .primitive_manager import PrimitiveManager

from ..base_env import BaseEnv
from ..state_manager import StateManager
from ..action_manager import ActionManager
from ..agents import UaV, UgV


@ray.remote
class RedTeam(BaseEnv):
    def __init__(self, config):

        # Initialise the base environment
        super().__init__(config)

        # Environment parameters
        self.current_time = config['simulation']['current_time']
        self.done = False
        self.config = config

        # Load the environment
        if self.config['simulation']['collision_free']:
            path = Path(
                __file__).parents[1] / 'urdf/environment_collision_free.urdf'
        else:
            path = Path(__file__).parents[1] / 'urdf/environment.urdf'

        self.p.loadURDF(str(path), [25, 140, 44],
                        self.p.getQuaternionFromEuler([
                            -0.45 * np.pi / 180, -24.5 * np.pi / 180,
                            -20.0 * np.pi / 180
                        ]),
                        flags=self.p.URDF_USE_MATERIAL_COLORS_FROM_MTL,
                        useFixedBase=True)

        # Initialize the state and action components
        self.state_manager = StateManager(self.current_time, self.config)
        self.uav, self.ugv = self._initial_uxv_setup(
            state_manager=self.state_manager, team_type='red')
        self.action_manager = ActionManager(self.uav,
                                            self.ugv,
                                            self.p,
                                            self.config,
                                            team_type='red')
        # Setup groups
        self._uxv_group_setup()

    def _get_initial_positions(self, init_pos, r, n):
        positions = []
        t = np.linspace(0, 2 * np.pi, n)
        x = init_pos[0] + r * np.cos(t)
        y = init_pos[1] + r * np.sin(t)
        positions = np.asarray([x, y, x * 0 + 5]).T.tolist()
        return positions

    def _initial_uxv_setup(self, state_manager, team_type):
        # Read the configuration of platoons
        read_path = Path(
            __file__).parents[2] / 'config/red_team_config_baseline.yml'
        config = yaml.load(open(str(read_path)), Loader=yaml.SafeLoader)

        # Containers
        ugv, uav = [], []
        init_orient = self.p.getQuaternionFromEuler([np.pi / 2, 0, 0])

        idx = 0
        for i, node in enumerate(config['ugv_platoon']['initial_nodes_pos']):
            init_pos = self.state_manager.node_info(node)['position']
            n_vehicles = config['ugv_platoon']['n_vehicles'][i]
            positions = self._get_initial_positions(init_pos, 4, n_vehicles)
            for position in positions:
                ugv.append(
                    UgV(self.p, position, init_orient, idx, self.config,
                        team_type))
                idx += 1

        idx = 0
        for i, node in enumerate(config['uav_platoon']['initial_nodes_pos']):
            init_pos = self.state_manager.node_info(node)['position']
            n_vehicles = config['uav_platoon']['n_vehicles'][i]
            positions = self._get_initial_positions(init_pos, 4, n_vehicles)
            for position in positions:
                uav.append(
                    UaV(self.p, position, init_orient, idx, self.config,
                        team_type))
                idx += 1
        return uav, ugv

    def _uxv_group_setup(self):
        """Initial setup of platoons with primitive execution class.
            Each platoon name is given as uxv_p_* where * is the platoon number
            and x is either 'a' or 'g' depending on platoon type.
            The containers used for platoons are dict where key is uxv_p_*

            As an example one of the keys is 'uav_p_1'
            which is platoon 1 of type uav
        """
        self.uav_group = {}  # A container for platoons
        for i in range(self.config['simulation']['n_uav_platoons']):
            key = 'uav_p_' + str(i + 1)
            self.uav_group[key] = PrimitiveManager(self.state_manager,
                                                   self.uav, self.ugv)

        self.ugv_group = {}
        for i in range(self.config['simulation']['n_ugv_platoons']):
            key = 'ugv_p_' + str(i + 1)
            self.ugv_group[key] = PrimitiveManager(self.state_manager,
                                                   self.uav, self.ugv)
        return None

    def reset(self):
        """
        Resets the position of all the robots
        """
        self._reset()
        return True

    def get_attributes(self, attributes):
        return self.action_manager.platoon_attributes(attributes)

    def step(self, ps):
        """Execute the actions of uav and ugv
        """
        # Roll the primitives
        start_time = time.time()
        current_time = 0
        duration = self.config['experiment']['duration']

        # Get latest actions
        actions = ray.get(ps.get_action.remote(complexity=True))

        # Perform action allocation

        self.action_manager.perform_action_allocation(actions['uav'],
                                                      actions['ugv'],
                                                      self.uav_group,
                                                      self.ugv_group)
        while current_time <= duration:
            self.action_manager.roll_actions(ps)
            current_time = time.time() - start_time

        return None
