from .state_manager import StateManager
from .action_manager import ActionManager


class BlueTeam(object):
    def __init__(self, config, uav, ugv):

        # Environment parameters
        self.current_time = config['simulation']['current_time']
        self.done = False
        self.config = config
        # Initialize the state and action components
        self.state_manager = StateManager(uav, ugv, self.current_time,
                                          self.config)
        self.action_manager = ActionManager(self.state_manager)

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

    def execute(self, actions_uav, actions_ugv):
        """Take a step in the environement
        """
        # Execute the actions
        self.action_manager.primitive_execution(actions_uav, actions_ugv)
        return None
