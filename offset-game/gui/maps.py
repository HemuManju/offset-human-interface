import pygame


def get_window_size(screen_size):
    size = (int(0.6 * screen_size[0]), int(0.75 * screen_size[1]))
    return size


def get_position(screen_size):
    position = (5 + 0 * screen_size[0], 5 + 0 * screen_size[1])
    return position


class Map(pygame.sprite.Sprite):
    def __init__(self, screen, screen_size):
        self.screen_size = screen_size
        self.position = get_position(screen_size)
        self.size = get_window_size(screen_size)

        self.surface = pygame.Surface(self.size)
        self.init_surface = self.surface.copy()

        self.screen = screen  # overall screen
        self.screen.blit(self.surface, self.position)

        self.env_surface = self.get_env_surface()
        self.env_surface = pygame.transform.scale(
            self.env_surface, (screen_size[0], screen_size[1]))
        self.init_env_surface = self.env_surface.copy()
        self.map_pos = self.env_surface.get_rect()
        return None

    def image_processing(self, image):
        return None

    def get_env_surface(self):
        image_path = 'offset-game/gui/images/Benning_nodes.png'
        image = pygame.image.load(image_path).convert()
        return image
