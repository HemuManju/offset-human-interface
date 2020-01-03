import time
import math
from pathlib import Path

from .agents import UaV, UgV
from .base_env import BaseEnv

from .blue_team.blue_base import BlueTeam
from .red_team.red_base import RedTeam

from .interaction_manager import InteractionManager


class BenningEnv(BaseEnv):
    def __init__(self, config):
        # Initialise the base environment
        super().__init__(config)

        # Load the environment
        if self.config['simulation']['collision_free']:
            path = Path(
                __file__).parents[0] / 'urdf/environment_collision_free.urdf'
        else:
            path = Path(__file__).parents[0] / 'urdf/environment.urdf'

        self.p.loadURDF(str(path), [25, 140, 44],
                        self.p.getQuaternionFromEuler([
                            -0.45 * math.pi / 180, -24.5 * math.pi / 180,
                            -20.0 * math.pi / 180
                        ]),
                        flags=self.p.URDF_USE_MATERIAL_COLORS_FROM_MTL,
                        useFixedBase=True)
        # self.p.loadURDF(str(path), [58.487, 23.655, 0.1],
        #                 self.p.getQuaternionFromEuler([0, 0, math.pi / 2]),
        #                 useFixedBase=True)

        # Initial step of blue and red team
        self._initial_team_setup()

        self.images = []

        # Initialize interaction manager
        self.interaction_manager = InteractionManager(config)
        return None

    def _initial_team_setup(self):
        # Red team
        uav_red, ugv_red = self._initial_uxv_setup(team_type='red')
        self.red_team = RedTeam(self.config, uav_red, ugv_red)

        # # Blue team
        uav_blue, ugv_blue = self._initial_uxv_setup(team_type='blue')
        self.blue_team = BlueTeam(self.config, uav_blue, ugv_blue)
        return None

    def _initial_uxv_setup(self, team_type):
        # Number of UGV and UAV
        self.n_ugv = self.config['simulation']['n_ugv']
        self.n_uav = self.config['simulation']['n_uav']

        ugv, uav = [], []
        test = []
        # Initialise the UGV and UAV
        init_orientation = self.p.getQuaternionFromEuler([math.pi / 2, 0, 0])
        for i, item in enumerate(range(self.n_ugv)):
            position = self.base_env_get_initial_position(item, self.n_ugv)
            init_pos = [position[0] * 0.25 + 2.5, position[1] * 0.25, 5]
            test.append(init_pos)
            ugv.append(
                UgV(self.p, init_pos, init_orientation, i, self.config,
                    team_type))

        for i, item in enumerate(range(self.n_uav)):
            position = self.base_env_get_initial_position(item, self.n_uav)
            init_pos = [position[0] * 0.25 + 2.5, position[1] * 0.25 - 1.5, 5]
            uav.append(
                UaV(self.p, init_pos, init_orientation, i, self.config,
                    team_type))
        return uav, ugv

    def reset(self):
        for i in range(50):
            time.sleep(1 / 240)
            self.p.stepSimulation()

    def step(self, actions_uav_b, actions_ugv_b, actions_uav_r, actions_ugv_r):
        # Roll the actions
        done_rolling_actions = False
        simulation_count = 0
        start_time = time.time()
        current_time = 0
        duration = self.config['experiment']['duration']

        # Perform action allocation for blue and red team respectively
        self.blue_team.action_manager.perform_action_allocation(
            actions_uav_b, actions_ugv_b)

        self.red_team.action_manager.perform_action_allocation(
            actions_uav_r, actions_ugv_r)

        # Run the simulation
        while not done_rolling_actions and current_time <= duration:

            simulation_count += 1
            current_time = time.time() - start_time

            # Interaction Manager (this over-rides the given actions)
            self.interaction_manager.update_actions(self.blue_team,
                                                    self.red_team)

            # Run the blue team (these can be made parallel)
            self.blue_team.execute()

            image = self.red_team.action_manager.get_image(1, 'uav', 0, 'all')
            self.images.append(image)

            # Run the red team (these can be made parallel)
            self.red_team.execute()

            # Perform a step in simulation to update
            self.base_env_step()
            # print(time.time() - t)
            # print('--------------')

    def get_reward(self):
        """Update reward of all the agents
        """
        # Calculate the reward
        total_reward = self.reward.mission_reward(self.state_manager.ugv,
                                                  self.state_manager.uav,
                                                  self.config)
        for vehicle in self.state_manager.uav:
            vehicle.reward = total_reward

        for vehicle in self.state_manager.ugv:
            vehicle.reward = total_reward
        return total_reward

    def check_episode_done(self):
        done = False
        if self.current_time >= self.config['simulation']['total_time']:
            done = True
        if self.state_manager.found_goal:
            done = True
        return done
