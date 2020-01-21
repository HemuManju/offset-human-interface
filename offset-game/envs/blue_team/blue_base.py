from pathlib import Path
import numpy as np

import ray

from .primitive_manager import PrimitiveManager

from ..base_env import BaseEnv
from ..state_manager import StateManager
from ..action_manager import ActionManager


@ray.remote
class BlueTeam(BaseEnv):
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
        uav, ugv = super()._initial_uxv_setup(team_type='blue')
        self.state_manager._initial_uxv(uav, ugv)  # Append the UxV
        self.action_manager = ActionManager(self.state_manager,
                                            PrimitiveManager,
                                            team_type='blue')

    def reset(self):
        """
        Resets the position of all the robots
        """
        for vehicle in self.state_manager.uav:
            vehicle.reset()

        for vehicle in self.state_manager.ugv:
            vehicle.reset()

        done = False
        return done

    def get_attributes(self, attributes):
        return self.action_manager.platoon_attributes(attributes)

    def step(self, ps):
        """Execute the actions of uav and ugv
        """
        # Perform the action
        self.action_manager.primitive_execution(self.p, ps)
        return None
