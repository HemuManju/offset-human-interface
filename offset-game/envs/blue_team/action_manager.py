from .primitive_manager import PrimitiveManager


class ActionManager(object):
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.config = state_manager.config

        # Setup the platoons
        self._init_platoons_setup()
        return None

    def _init_platoons_setup(self):
        """Initial setup of platoons with primitive execution class.
            Each platoon name is given as uxv_p_* where * is the platoon number
            and x is either 'a' or 'g' depending on platoon type.
            The containers used for platoons are dict where key is uxv_p_*

            As an example one of the keys is 'uav_p_1'
            which is platoon 1 of type uav

        """
        self.uav_platoons = {}  # A container for platoons
        for i in range(self.config['simulation']['n_uav_platoons']):
            key = 'uav_p_' + str(i + 1)
            self.uav_platoons[key] = PrimitiveManager(self.state_manager)

        self.ugv_platoons = {}
        for i in range(self.config['simulation']['n_ugv_platoons']):
            key = 'ugv_p_' + str(i + 1)
            self.ugv_platoons[key] = PrimitiveManager(self.state_manager)
        return None

    def perform_task_allocation(self, actions_uav, actions_ugv):
        """Perfroms task allocation

        Parameters
        ----------
        actions_uav : array
            UAV decoded actions
        actions_ugv : array
            UGV decoded actions
        """
        ids = 0
        target_pos = [[20, 100], [50, 150], [20, 150]]
        for i, key in enumerate(self.uav_platoons):
            n_vehicles = actions_uav[key]['n_vehicles']
            # Execute only when there are more than 0 vehicles
            if n_vehicles < 1:
                actions_uav[key]['execute'] = False

            vehicles_id = list(range(ids, ids + n_vehicles))
            ids = ids + n_vehicles
            actions_uav[key]['vehicles_id'] = vehicles_id
            actions_uav[key]['target_pos'] = target_pos[i]
            self.uav_platoons[key].set_action(actions_uav[key])

        ids = 0
        for i, key in enumerate(self.ugv_platoons):
            n_vehicles = actions_ugv[key]['n_vehicles']
            # Execute only when there are more than 0 vehicles
            if n_vehicles < 1:
                actions_ugv[key]['execute'] = False

            # Set number of vehicles
            vehicles_id = list(range(ids, ids + n_vehicles))
            ids = ids + n_vehicles
            actions_ugv[key]['vehicles_id'] = vehicles_id
            self.ugv_platoons[key].set_action(actions_ugv[key])
        return None

    def platoon_attributes(self, attributes):
        attribute = {}
        for i in range(self.config['simulation']['n_uav_platoons']):
            platoon_key = 'uav_p_' + str(i + 1)
            if attributes:
                attribute[platoon_key] = {
                    attr: vars(self.uav_platoons[platoon_key])['action'][attr]
                    for attr in attributes
                }
            else:
                attribute[platoon_key] = vars(
                    self.uav_platoons[platoon_key])['action']
        for i in range(self.config['simulation']['n_uav_platoons']):
            platoon_key = 'ugv_p_' + str(i + 1)
            if attributes:
                attribute[platoon_key] = {
                    attr: vars(self.ugv_platoons[platoon_key])['action'][attr]
                    for attr in attributes
                }
            else:
                attribute[platoon_key] = vars(
                    self.ugv_platoons[platoon_key])['action']
        return attribute

    def primitive_execution(self, actions_uav, actions_ugv, hand_coded=True):
        """Performs task execution

        Parameters
        ----------
        actions_uav : array
            UAV decoded actions
        actions_ugv : array
            UAV decoded actions
        hand_coded : bool
            Whether hand coded tactics are being used or not
        """

        self.perform_task_allocation(actions_uav, actions_ugv)

        primitives_done = []
        # Update all the uav vehicles
        for key in self.uav_platoons:
            primitives_done.append(self.uav_platoons[key].execute_primitive())

        # Update all the ugv vehicles
        for key in self.ugv_platoons:
            primitives_done.append(self.ugv_platoons[key].execute_primitive())

        if all(item for item in primitives_done):
            done_rolling = True
        else:
            done_rolling = False

        return done_rolling
