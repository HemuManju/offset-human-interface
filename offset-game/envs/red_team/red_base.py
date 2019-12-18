from .state_manager import StateManager
from .action_manager import ActionManager
from .behavior_manager import BehaviourManager


class RedTeam(object):
    def __init__(self, config, uav, ugv):

        # Environment parameters
        self.current_time = config['simulation']['current_time']
        self.done = False
        self.config = config
        # Initialize the state and action components
        self.state_manager = StateManager(uav, ugv, self.current_time,
                                          self.config)
        self.action_manager = ActionManager(self.state_manager)
        self.behavior_manager = BehaviourManager(self.state_manager)

        # Default action
        actions_uav, actions_ugv = self.behavior_manager.get_default_actions()
        self.action_manager.primitive_execution(actions_uav, actions_ugv)

    def reset(self):
        """
        Resets the position of all the robots
        """
        for vehicle in self.state_manager.uav:
            vehicle.reset()

        for vehicle in self.state_manager.ugv:
            vehicle.reset()

        done = False
        return done

    def get_attributes(self, attributes):
        return self.action_manager.platoon_attributes(attributes)

    def execute(self, blue_team_attr):
        """Take a step in the environement
        """
        # Behavior of red team
        red_team_attr = self.get_attributes(['centroid_pos'])
        self.behavior_manager.choose_actions(red_team_attr, blue_team_attr)
        actions_uav, actions_ugv = self.behavior_manager.get_default_actions()

        # Execute the actions
        self.action_manager.primitive_execution(actions_uav, actions_ugv)
        return None
