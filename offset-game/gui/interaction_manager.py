import pygame

from .gif import GIFImage
from .task_allocation import TaskAllocation
from .utils import (get_rectangle_param, MousePosition)


class PanZoom(pygame.sprite.Sprite):
    """For panning and zooming
    """
    def __init__(self, map_instance):
        pygame.sprite.Sprite.__init__(self)
        self.map = map_instance
        self.map_pos = self.map.env_surface.get_rect()
        self.screen_width = self.map.screen_size[0]
        self.screen_height = self.map.screen_size[1]
        return None

    def check_map_pos(self, width, height):
        if self.map_pos[0] > 0:
            self.map_pos[0] = 0
        if self.map_pos[1] > 0:
            self.map_pos[1] = 0
        if abs(self.map_pos[0]) > width - self.screen_width + 600:
            self.map_pos[0] = -width + self.screen_width - 600
        if abs(self.map_pos[1]) > height - self.screen_height + 170:
            self.map_pos[1] = -height + self.screen_height - 170
        return None

    def get_current_map_pos(self):
        return [self.map_pos[0], self.map_pos[1]]

    def pan(self, mouse_pos):
        # Calculate the width and height
        width = self.map.env_surface.get_rect().width
        height = self.map.env_surface.get_rect().height

        if len(mouse_pos) > 1:
            intial_mouse = mouse_pos[-2]
            final_mouse = mouse_pos[-1]
            dx_mouse = final_mouse[0] - intial_mouse[0]
            dy_mouse = final_mouse[1] - intial_mouse[1]
        else:
            dx_mouse = 0
            dy_mouse = 0

        # Update the map pose
        self.map_pos[0] = dx_mouse + self.map_pos[0]
        self.map_pos[1] = dy_mouse + self.map_pos[1]

        # Check is the map of out of boundary
        self.check_map_pos(width, height)
        self.map.surface.blit(self.map.env_surface, self.map_pos)
        return None


class InteractionManager(pygame.sprite.Sprite):
    def __init__(self, map_instance):
        pygame.sprite.Sprite.__init__(self)
        self.map = map_instance
        self.pan_zoom = PanZoom(map_instance)
        self.mouse_0 = MousePosition(0)
        self.mouse_2 = MousePosition(2)
        self.allocate = TaskAllocation()
        self.smoke = GIFImage('offset-game/gui/images/smoke.gif')
        self.rect = []
        return None

    def mouse_draw(self, mouse_pos, surface):
        if mouse_pos:
            width, height = get_rectangle_param(mouse_pos[0], mouse_pos[-1])
            pygame.draw.rect(surface, (0, 0, 255),
                             (mouse_pos[0][0], mouse_pos[0][1], width, height),
                             2)
            mouse_parameters = [
                mouse_pos[-1][0], mouse_pos[-1][1], width, height
            ]
        else:
            mouse_parameters = []
        return mouse_parameters

    def update(self, states, actions, game_state, ps):
        self.pan_zoom.pan(self.mouse_2.position())

        # Task allocation
        self.mouse_draw(self.mouse_0.position(), self.map.env_surface)

        # Current map poisition
        map_pos = self.pan_zoom.get_current_map_pos()

        # Selection of platoons
        mouse_button = pygame.mouse.get_pressed()
        if mouse_button[0]:
            self.rect.append(
                self.mouse_draw(self.mouse_0.position(), self.map.surface))
        elif not mouse_button[0]:
            if self.rect:
                temp = self.rect[-1]
                temp[0] = temp[0] - map_pos[0]
                temp[1] = temp[1] - map_pos[1]
                self.allocate.select_platoon(states, actions, temp, ps)
                self.rect = []

        # Providing the target position
        if mouse_button[1]:
            x, y = pygame.mouse.get_pos()
            target_pos = [x - map_pos[0], y - map_pos[1]]
            self.allocate.assign_target(actions, states, target_pos, ps)
            pygame.draw.circle(self.map.surface, (0, 0, 0), [x - 6, y - 6], 10)

        # Draw smoke
        self.smoke.render(self.map.surface,
                          [400 + map_pos[0], 100 + map_pos[1]])

        # Pause and resume game
        if game_state['pause']:
            pygame.gfxdraw.filled_circle(self.map.surface, 25, 25, 15,
                                         (255, 0, 0))
            pygame.draw.circle(self.map.surface, (0, 0, 0), [25, 25], 16, 3)

        # Blit the final surface to screen
        self.map.screen.blit(self.map.surface, self.map.position)
