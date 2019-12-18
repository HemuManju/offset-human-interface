import pygame

import ray

from .maps import Map
from .action_manager import ActionManager
from .interaction_manager import InteractionManager
from .strategy import Strategy
from .information import Information
from .fullmap import FullMap
from .user_input import UserInput

import time


@ray.remote
class MainGUI(pygame.sprite.Sprite):
    def __init__(self, config, screen_size, ps):
        # Initialize pygame
        pygame.init()
        pygame.sprite.Sprite.__init__(self)
        self.screen = pygame.display.set_mode(screen_size)
        self.screen.fill([255, 255, 255])

        # Modules of Game
        self.map = Map(self.screen, screen_size)
        self.action_manager = ActionManager(self.map, config)
        self.interaction_manager = InteractionManager(self.map)
        self.strategy = Strategy(self.screen, screen_size, ps)
        self.information = Information(self.screen, screen_size)
        self.fullmap = FullMap(self.screen, screen_size)
        self.user_input = UserInput()

        # Configuration
        self.config = config
        self.duration = self.config['experiment']['duration']

    def get_start_time(self):
        return self.start_time

    def run(self, ps):
        clock = pygame.time.Clock()
        self.start_time = time.time()
        while (time.time() - self.start_time) <= self.duration:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return

            # Get latest states and actions
            states_id = ps.get_states.remote()
            actions_id = ps.get_actions.remote()
            game_state_id = ps.get_game_state.remote()
            states, actions, game_state = ray.get(
                [states_id, actions_id, game_state_id])

            # Get latest red team states and actions
            states_id = ps.get_states.remote(complexity=True)
            actions_id = ps.get_actions.remote(complexity=True)
            complexity_states, complexity_actions, _ = ray.get(
                [states_id, actions_id, game_state_id])

            # Update all the modules
            self.user_input.update(actions, ps)
            self.action_manager.check_perimeter(states, complexity_states, ps)
            self.action_manager.update(states, complexity_states)
            self.interaction_manager.update(states, actions, game_state, ps)
            self.user_input.update(actions, ps)

            # # Update the strategy and full map
            self.strategy.update(event)
            self.fullmap.update()
            pygame.display.flip()
            clock.tick(60)
