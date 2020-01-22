import numpy as np
import random

import ray

from ..primitives.planning.planners import SkeletonPlanning
from ..primitives.formation.control import FormationControl
from ..primitives.engaging.shooting import Shooting


class PrimitiveManager(object):
    def __init__(self, state_manager, uav, ugv):
        """A base class to perform different primitives.

        Parameters
        ----------
        state_manager : instance
            An instance of state manager
        """
        self.state_manager = state_manager
        self.uav = uav
        self.ugv = ugv
        self.dt = self.state_manager.config['simulation']['time_step']

        # Instance of primitives
        self.planning = SkeletonPlanning(self.state_manager.config,
                                         self.state_manager.grid_map)
        self.formation = FormationControl()
        self.shooting = Shooting()
        self.path_points = []
        self.patrol_poins = []
        return None

    def assign_vehicles(self):
        # Allocate vehicles
        self.vehicles = []
        if self.action['vehicles_type'] == 'uav':
            for j in self.action['vehicles_id']:
                vehicle = self.uav[j]
                if vehicle.functional:
                    self.vehicles.append(vehicle)
        else:
            for j in self.action['vehicles_id']:
                vehicle = self.ugv[j]
                if vehicle.functional:
                    self.vehicles.append(vehicle)
        return None

    def get_vehicles_info(self):
        vehicles_info = [vehicle.get_info() for vehicle in self.vehicles]
        return vehicles_info

    def allocate_action(self, action):
        self.action = action
        self.key = action['vehicles_type'] + '_p_' + str(action['platoon_id'])
        self.assign_vehicles()
        return None

    def execute_primitive(self, ps):
        """Perform primitive execution
        """
        primitives = {
            'planning': self.planning_primitive,
            'formation': self.formation_primitive,
            'shooting': self.shooting_primitive
        }

        # Get the latest actions
        actions = ray.get(ps.get_action.remote())
        key = self.action['vehicles_type'] + '_p_' + str(
            self.action['platoon_id'])
        self.action = actions[self.action['vehicles_type']][key]

        # Get the required vehicles state
        self.assign_vehicles()

        game_state = ray.get(ps.get_game_state.remote())

        if self.action['execute'] and not game_state['pause']:
            primitives[self.action['primitive']]()

            # Set the actions
            self.action['centroid_pos'] = self.get_centroid()
            self.action['vehicles_info'] = self.get_vehicles_info()
            ps.set_action.remote(self.action)

        return self.action

    def get_centroid(self):
        """Get the centroid of the vehicles
        """
        centroid = []
        for vehicle in self.vehicles:
            centroid.append(vehicle.current_pos)
        centroid = np.mean(np.asarray(centroid), axis=0)
        return centroid[0:2]  # only x and y

    def convert_pixel_ordinate(self, point, ispixel):
        """Convert the given point from pixel to cartesian co-ordinate or vice-versa.

        Parameters
        ----------
        point : list
            A list containing x and y position in pixel or cartesian space.
        ispixel : bool
            If True, the given input 'point' is in pixel space
            else it is in cartesian space.

        Returns
        -------
        list
            A converted point to pixel or cartesian space
        """
        if not ispixel:
            converted = [point[0] / 0.42871 + 145, point[1] / 0.42871 + 115]
        else:
            converted = [(point[0] - 145) * 0.42871,
                         (point[1] - 115) * 0.42871]
        return converted

    def get_spline_points(self):
        """Get the spline fit of path from start to end

        Returns
        -------
        list
            A list of points which are the fitted spline.
        """
        # Perform planning and fit a spline
        self.action['start_pos'] = self.action['centroid_pos']
        pixel_start = self.convert_pixel_ordinate(self.action['start_pos'],
                                                  ispixel=False)
        pixel_end = self.convert_pixel_ordinate(self.action['target_pos'],
                                                ispixel=False)
        path = self.planning.find_path(pixel_start, pixel_end, spline=False)

        # Convert to cartesian co-ordinates
        points = [
            self.convert_pixel_ordinate(point, ispixel=True) for point in path
        ]
        # As of now don't fit any splines
        if self.action['vehicles_type'] == 'uav':
            path_points = np.array(points[-1])
        else:
            path_points = np.array(points)
            path_points = path_points[0::4, :]
        return path_points, points

    def planning_primitive(self):
        """Performs path planning primitive
        """
        # Make vehicles non idle
        done_rolling = False

        # Initial formation
        if self.action['initial_formation']:
            # First point of formation
            self.action['centroid_pos'] = self.get_centroid()
            self.action['next_pos'] = self.action['centroid_pos']
            done = self.formation_primitive()
            if done:
                self.action['initial_formation'] = False
                self.path_points, points = self.get_spline_points()
        else:
            self.action['centroid_pos'] = self.get_centroid()
            distance = np.linalg.norm(self.action['centroid_pos'] -
                                      self.action['target_pos'])

            if len(self.path_points) > 2:
                self.action['next_pos'] = self.path_points[0]
                self.path_points = np.delete(self.path_points, 0, 0)
            else:
                self.action['next_pos'] = self.action['target_pos']
            self.formation_primitive()
            if distance < 1:
                done_rolling = True

        if done_rolling:
            ()
        return done_rolling

    def formation_primitive(self):
        """Performs formation primitive
        """
        if self.action['primitive'] == 'formation':
            self.action['centroid_pos'] = self.get_centroid()
            self.action['next_pos'] = self.get_centroid()

        self.vehicles, done_rolling = self.formation.execute(
            self.vehicles, self.action['next_pos'],
            self.action['centroid_pos'], self.dt, 'solid')

        for vehicle in self.vehicles:
            vehicle.set_position(vehicle.updated_pos)
        return done_rolling

    def shooting_primitive(self):
        """Perform shooting primitive
        """

        # First point of formation
        self.action['centroid_pos'] = self.get_centroid()
        self.action['next_pos'] = self.action['centroid_pos']

        n_blue_team = self.action['n_blue_team']
        n_red_team = self.action['n_red_team']
        distance = self.action['distance']

        p = self.shooting.shoot(n_blue_team, n_red_team, distance, type='blue')

        if p > 0.95 and random.random() > 0.90:
            # Remove 10% of the drones
            n_vehicles = len(self.action['vehicles_id'])
            n_remove = int(np.ceil(0.1 * n_vehicles))
            if n_vehicles > 2:
                # Sort is needed to remove the highest index first
                ids_to_remove = random.choices(range(n_vehicles - 1),
                                               k=n_remove)
                ids_to_remove.sort(reverse=True)
                for idx in ids_to_remove:
                    self.vehicles[idx].remove_self()
                    self.vehicles[idx].functional = False
                    self.vehicles.pop(idx)

                    # Update the action also
                    self.action['vehicles_id'].pop(idx)

                    # Update number of casualities
                    self.action['casualities'].append(1)

                # Perform formation control
                self.formation_primitive()
            else:
                self.action['execute'] = False
