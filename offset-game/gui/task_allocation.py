import pygame
import numpy as np
from matplotlib.path import Path


def get_window_size(screen_size):
    size = (int(0.6 * screen_size[0]), int(0.75 * screen_size[1]))
    return size


def get_position(screen_size):
    position = (5 + 0 * screen_size[0], 5 + 0 * screen_size[1])
    return position


class TaskAllocation(pygame.sprite.Sprite):
    def __init__(self):
        self.selected_platoon = []
        return None

    def get_enclosed_centorid(self, rectangle, actions):
        actions_uav, actions_ugv = actions['uav'], actions['ugv']
        centroid = {}
        for key in actions_uav:
            centroid[key] = actions_uav[key]['centroid_pos']
        for key in actions_ugv:
            centroid[key] = actions_ugv[key]['centroid_pos']

        centroid_values = np.asarray(list(centroid.values()))
        centroid_values_pixel = np.zeros(centroid_values.shape)
        centroid_values_pixel[:, 0] = centroid_values[:, 0] / .2 + 340
        centroid_values_pixel[:, 1] = centroid_values[:, 1] / .2 + 420

        # Get the point with in the rectangle
        selected_platoon = {}
        selected_platoon['uav'] = []
        selected_platoon['ugv'] = []

        mask = rectangle.contains_points(centroid_values_pixel)
        for i, keys in enumerate(centroid):
            if mask[i]:
                if keys[0:3] == 'uav':
                    selected_platoon['uav'].append(keys)
                else:
                    selected_platoon['ugv'].append(keys)
        return selected_platoon

    def convert_points_path(self, points):
        x, y = points[1], points[0]
        w, h = -points[2], -points[3]
        vertices = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
        rectangle = Path(vertices)  # make a polygon
        return rectangle

    def select_platoon(self, states, actions, rectangle, ps):
        rectangle_pixel = self.convert_points_path(rectangle)
        self.selected_platoon = self.get_enclosed_centorid(
            rectangle_pixel, actions)
        for platoon_type in self.selected_platoon:
            if self.selected_platoon[platoon_type]:
                platoons = self.selected_platoon[platoon_type]
                for platoon in platoons:
                    # Convert to catesian form
                    states[platoon_type][platoon]['selected'] = True
                    ps.set_state.remote(states[platoon_type][platoon])
        return None

    def assign_target(self, actions, states, target_pos, ps):
        for platoon_type in self.selected_platoon:
            if self.selected_platoon[platoon_type]:
                platoons = self.selected_platoon[platoon_type]
                for platoon in platoons:
                    # Convert to catesian form
                    target_pos = [(target_pos[1] - 340) * 0.2,
                                  (target_pos[0] - 420) * 0.2]
                    actions[platoon_type][platoon]['target_pos'] = target_pos
                    ps.set_action.remote(actions[platoon_type][platoon])
                    # Set the selection to False
                    states[platoon_type][platoon]['selected'] = False
                    ps.set_state.remote(states[platoon_type][platoon])
        return None
