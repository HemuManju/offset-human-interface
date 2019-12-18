import pygame
import pygame.gfxdraw


class PrimitiveManager(pygame.sprite.Sprite):
    """A primitive manager for each platoon
    """
    def __init__(self, map_instance, platoon_id, vehicle_type):
        pygame.sprite.Sprite.__init__(self)
        self.platoon_id = platoon_id
        self.vehicle_type = vehicle_type
        self.map = map_instance
        self.key = self.vehicle_type + '_p_' + str(self.platoon_id)
        return None

    def get_centroid(self):
        return self.state['centroid_pos']

    def get_vehicles(self, states):
        self.state = states[self.vehicle_type][self.key]
        vehicles = self.state['vehicles']
        return vehicles

    def convert_to_pixel(self, points):
        pos = [int(points[1] / .2 + 420), int(points[0] / .2 + 340)]
        return pos

    def update(self, states):
        self.vehicles = self.get_vehicles(states)
        # Execute only if the number of vehicles are > 0
        # if self.state['n_vehicles'] > 0:
        if self.vehicle_type == 'uav':
            color = (0, 153, 76)
            for vehicle in self.vehicles:
                pos = self.convert_to_pixel(vehicle.current_pos)
                # Draw a circle
                pygame.draw.circle(self.map.env_surface, color, pos, 3)
                # pygame.gfxdraw.filled_circle(self.map.env_surface, pos[0],
                #                              pos[1], 3, color)
                # pygame.gfxdraw.aacircle(self.map.env_surface, pos[0], pos[1],
                #                         3, color)
        else:
            color = (0, 0, 255)
            for vehicle in self.vehicles:
                pos = self.convert_to_pixel(vehicle.current_pos)
                # Draw a rectangle
                pygame.draw.rect(self.map.env_surface, color,
                                 pygame.Rect(pos, [5, 5]))

        # Draw a black circle around the platoons if it is selected
        if self.state['selected']:
            color = (0, 0, 0)
            cent_pos = self.convert_to_pixel(self.get_centroid())
            pygame.draw.circle(self.map.env_surface, color, cent_pos, 25, 3)
            # pygame.draw.aacircle(self.map.env_surface, cent_pos[0],
            #                         cent_pos[1], 20, (0, 0, 1))

        self.map.surface.blit(self.map.env_surface, self.map.position)

        return None


class ComplexPrimitiveManager(pygame.sprite.Sprite):
    """A primitive manager for each platoon
    """
    def __init__(self, map_instance, platoon_id, vehicle_type):
        pygame.sprite.Sprite.__init__(self)
        self.platoon_id = platoon_id
        self.vehicle_type = vehicle_type
        self.map = map_instance
        self.key = self.vehicle_type + '_p_' + str(self.platoon_id)
        return None

    def get_centroid(self):
        return self.state['centroid_pos']

    def get_vehicles(self, states):
        self.state = states[self.vehicle_type][self.key]
        vehicles = self.state['vehicles']
        return vehicles

    def convert_to_pixel(self, points):
        pos = [int(points[1] / .2 + 420), int(points[0] / .2 + 340)]
        return pos

    def update(self, states):
        self.vehicles = self.get_vehicles(states)
        # Execute only if the number of vehicles are > 0
        # if self.state['n_vehicles'] > 0:
        if self.vehicle_type == 'uav':
            if self.state['with_in_perimeter']:
                color = (204, 0, 0)
                for vehicle in self.vehicles:
                    pos = self.convert_to_pixel(vehicle.current_pos)
                    # Draw a circle
                    pygame.draw.circle(self.map.env_surface, color, pos, 3)
        else:
            if self.state['with_in_perimeter']:
                color = (204, 0, 0)
                for vehicle in self.vehicles:
                    pos = self.convert_to_pixel(vehicle.current_pos)
                    # Draw a rectangle
                    pygame.draw.rect(self.map.env_surface, color,
                                     pygame.Rect(pos, [5, 5]))

        # Draw a black circle around the platoons if it is selected
        if self.state['selected']:
            color = (0, 0, 0)
            cent_pos = self.convert_to_pixel(self.get_centroid())
            pygame.draw.circle(self.map.env_surface, color, cent_pos, 25, 3)

        self.map.surface.blit(self.map.env_surface, self.map.position)

        return None
