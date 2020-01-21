import math
import yaml
from pathlib import Path

import numpy as np

import pybullet as p
import pybullet_data
from pybullet_utils import bullet_client

from .agents import UaV, UgV


def get_initial_positions(init_pos, r, n):
    positions = []
    t = np.linspace(0, 2 * np.pi, n)
    x = init_pos[0] + r * np.cos(t)
    y = init_pos[1] + r * np.sin(t)
    positions = np.asarray([x, y, x * 0 + 5]).T.tolist()
    return positions


class BaseEnv(object):
    def __init__(self, config):
        self.config = config
        # Usage mode
        if config['simulation']['headless']:
            self.p = bullet_client.BulletClient(connection_mode=p.DIRECT)
        else:
            self.p = bullet_client.BulletClient(connection_mode=p.GUI)
            self.p.resetDebugVisualizerCamera(cameraDistance=150,
                                              cameraYaw=0,
                                              cameraPitch=-89.999,
                                              cameraTargetPosition=[0, 80, 0])
        # Set gravity
        self.p.setGravity(0, 0, -9.81)
        self.p.setAdditionalSearchPath(pybullet_data.getDataPath())  # optional

        # Whether to use real time or not
        if self.config['simulation']['use_real_time']:
            self.p.setRealTimeSimulation(1)

        # Set parameters for simulation
        self.p.setPhysicsEngineParameter(
            fixedTimeStep=config['simulation']['time_step'] / 10,
            numSubSteps=1,
            numSolverIterations=5)

        self.p.configureDebugVisualizer(self.p.COV_ENABLE_GUI, 0)

        # Setup ground
        plane = self.p.loadURDF("plane.urdf", [0, 0, 0],
                                self.p.getQuaternionFromEuler(
                                    [0, 0, math.pi / 2]),
                                useFixedBase=True,
                                globalScaling=20)
        self.p.changeVisualShape(plane, -1)
        return None

    def base_env_get_camera_image(self):
        """Get the camera image of the scene

        Returns
        -------
        tuple
            Three arrays corresponding to rgb, depth, and segmentation image.
        """
        upAxisIndex = 2
        camDistance = 500
        pixelWidth = 350
        pixelHeight = 700
        camTargetPos = [0, 80, 0]

        far = camDistance
        near = -far
        view_matrix = self.p.computeViewMatrixFromYawPitchRoll(
            camTargetPos, camDistance, 0, 90, 0, upAxisIndex)
        projection_matrix = self.p.computeProjectionMatrix(
            -90, 60, 150, -150, near, far)
        # Get depth values using the OpenGL renderer
        width, height, rgbImg, depthImg, segImg = self.p.getCameraImage(
            pixelWidth,
            pixelHeight,
            view_matrix,
            projection_matrix,
            renderer=self.p.ER_BULLET_HARDWARE_OPENGL)
        return rgbImg, depthImg, segImg

    def _initial_uxv_setup(self, team_type):
        # Read the configuration of platoons
        if team_type == 'red':
            read_path = Path(
                __file__).parents[1] / 'config/red_team_config_baseline.yml'
        else:
            read_path = Path(
                __file__).parents[1] / 'config/blue_team_config.yml'
        config = yaml.load(open(str(read_path)), Loader=yaml.SafeLoader)

        # Containers
        ugv, uav = [], []
        init_orient = self.p.getQuaternionFromEuler([np.pi / 2, 0, 0])

        idx = 0
        for i, node in enumerate(config['ugv_platoon']['initial_nodes_pos']):
            init_pos = self.state_manager.node_info(node)['position']
            n_vehicles = config['ugv_platoon']['n_vehicles'][i]
            positions = get_initial_positions(init_pos, 4, n_vehicles)
            for position in positions:
                ugv.append(
                    UgV(self.p, position, init_orient, idx, self.config,
                        team_type))
                idx += 1

        idx = 0
        for i, node in enumerate(config['uav_platoon']['initial_nodes_pos']):
            init_pos = self.state_manager.node_info(node)['position']
            n_vehicles = config['uav_platoon']['n_vehicles'][i]
            positions = get_initial_positions(init_pos, 4, n_vehicles)
            for position in positions:
                uav.append(
                    UaV(self.p, position, init_orient, idx, self.config,
                        team_type))
                idx += 1
        return uav, ugv

    def base_env_get_initial_position(self, agent, n_agents):
        grid = np.arange(n_agents).reshape(n_agents // 5, 5)
        pos_xy = np.where(grid == agent)
        return [pos_xy[0][0] * 20 + 10, pos_xy[1][0] * 20]

    def base_env_step(self):
        self.p.stepSimulation()

    def base_env_simulation_reset(self):
        self.p.resetSimulation()
