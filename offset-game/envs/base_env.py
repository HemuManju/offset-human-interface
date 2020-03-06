from pathlib import Path

import numpy as np

import pybullet as p
import pybullet_data
from pybullet_utils import bullet_client


class BenningEnv(object):
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

        # Load the environment
        if self.config['simulation']['collision_free']:
            path = Path(__file__).parents[
                1] / 'envs/urdf/environment_collision_free.urdf'
        else:
            path = Path(__file__).parents[1] / 'envs/urdf/environment.urdf'

        self.p.loadURDF(str(path), [25, 140, 44],
                        self.p.getQuaternionFromEuler([
                            -0.45 * np.pi / 180, -24.5 * np.pi / 180,
                            -20.0 * np.pi / 180
                        ]),
                        flags=self.p.URDF_USE_MATERIAL_COLORS_FROM_MTL,
                        useFixedBase=True)

        # Setup ground
        # plane = self.p.loadURDF("plane.urdf", [0, 0, 0],
        #                         self.p.getQuaternionFromEuler(
        #                             [0, 0, math.pi / 2]),
        #                         useFixedBase=True,
        #                         globalScaling=2)
        # self.p.changeVisualShape(plane, -1)
        return None

    def _env_get_camera_image(self):
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

    def _step(self):
        self.p.stepSimulation()

    def _reset(self):
        self.p.resetSimulation()

    def get_physics_client(self):
        return self.p
