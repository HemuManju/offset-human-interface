import time
import math
from pathlib import Path

from .base_env import BaseEnv

from .default_actions import blue_team_actions, red_team_actions

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

        # Initial step of blue and red team
        self._initial_team_setup()

        # Initialize interaction manager
        self.interaction_manager = InteractionManager(config)
        return None

    def _initial_team_setup(self):
        # Red team
        self.red_team = RedTeam(self.p, self.config)

        # Blue team
        self.blue_team = BlueTeam(self.p, self.config)
        return None

    def reset(self):
        for i in range(50):
            time.sleep(1 / 240)
            self.p.stepSimulation()

    def step(self, actions_uav_b, actions_ugv_b, actions_uav_r, actions_ugv_r):

        # Roll the actions
        simulation_count = 0
        step_frames = self.config['experiment']['step_frames']

        # Perform action allocation for blue and red team respectively
        self.blue_team.action_manager.perform_action_allocation(
            actions_uav_b, actions_ugv_b)

        self.red_team.action_manager.perform_action_allocation(
            actions_uav_r, actions_ugv_r)

        # # # Run the simulation
        while simulation_count <= step_frames:
            simulation_count += 1
            self.base_env_step()  # Call this more frequenctly

            # Run the blue team (these can be made parallel)
            self.blue_team.execute()

            # Run the red team (these can be made parallel)
            self.red_team.execute()

            # # Interaction Manager (this over-rides the given actions)
            self.interaction_manager.update_actions(self.blue_team,
                                                    self.red_team)

            # Perform a step in simulation to update
            self.base_env_step()

        # Once the loop is dones make all the vehicles idle
        self.blue_team.action_manager.make_vehicles_idle()
        self.red_team.action_manager.make_vehicles_idle()

        # Get the latest attributes/actions
        blue_actions = self.blue_team.get_attributes([])
        red_actions = self.red_team.get_attributes([])
        return blue_actions, red_actions

    def main_loop(self):
        # Roll the actions
        start_time = time.time()
        current_time = 0
        duration = self.config['experiment']['duration']

        # Initial setup of parameter server
        blue_actions = blue_team_actions(self.config)
        red_actions = red_team_actions(self.config)

        while current_time <= duration:
            current_time = time.time() - start_time
            # Run the simulation
            self.step(blue_actions['uav'], blue_actions['ugv'],
                      red_actions['uav'], red_actions['ugv'])
        return None

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
