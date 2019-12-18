class Action(object):
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.current_time = state_manager.current_time
        self.config = state_manager.config
        return None

    def get_idle_vehicles(self, vehicles):
        """Returns non idle vehicles

        Parameters
        ----------
        vehicles : list
            A list of UAV or UGV vehilces class
        """
        vehicles = list(filter(lambda vehicle: vehicle.idle, vehicles))
        return vehicles

    def get_action(self, uav_actions, ugv_actions):
        decoded_actions_uav = {}

        decoded_actions_ugv = {}

        return decoded_actions_uav, decoded_actions_ugv
