import time
import math
from pathlib import Path

from .agents import UaV, UgV
from .base_env import BaseEnv

from .blue_team.blue_base import BlueTeam
from .red_team.red_base import RedTeam


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
        self.p.loadURDF(str(path), [58.487, 23.655, 0.1],
                        self.p.getQuaternionFromEuler([0, 0, math.pi / 2]),
                        useFixedBase=True)

        # Initial step of blue and red team
        self._initial_team_setup()
        return None

    def _initial_team_setup(self):
        # Red team
        uav_red, ugv_red = self._initial_uxv_setup(team_type='red')
        self.red_team = RedTeam(self.config, uav_red, ugv_red)

        # Blue team
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

    def step(self, actions_uav, actions_ugv):
        # Roll the actions
        done_rolling_actions = False
        simulation_count = 0
        start_time = time.time()
        current_time = 0
        duration = self.config['experiment']['duration']

        while not done_rolling_actions and current_time <= duration:
            simulation_count += 1
            current_time = time.time() - start_time
            t = time.time()
            # Run the blue team (these can be made parallel)
            self.blue_team.execute(actions_uav, actions_ugv)
            blue_team_attr = self.blue_team.get_attributes(['centroid_pos'])

            # Run the red team (these can be made parallel)
            # self.red_team.execute(blue_team_attr)
            # print(time.time() - t)
            self.base_env_step()

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
