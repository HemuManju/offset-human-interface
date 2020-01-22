import ray


class ActionManager(object):
    def __init__(self, uav, ugv, physics_client, config, team_type):

        self._p = physics_client

        self.uav = uav
        self.ugv = ugv
        self.config = config

        if team_type == 'red':
            self.complexity = True
        else:
            self.complexity = False
        return None

    def platoon_attributes(self, attributes):
        """Returns the attributes of the primitive manager such as actions or
        specific attricutes such as centroid of platoons or target postiion

        Parameters
        ----------
        attributes : list
            A list of attributes to extract from the primitive manager.
            If this is empyt all the member variables
            from the primitive instance will be returned

        Returns
        -------
        dict
            A dictionary of all the attributes
            as specified by the 'attributes' input parameter
        """

        attribute = {'uav': {}, 'ugv': {}}
        for i in range(self.config['simulation']['n_uav_platoons']):
            platoon_key = 'uav_p_' + str(i + 1)
            if attributes:
                attribute['uav'][platoon_key] = {
                    attr: vars(self.uav_platoons[platoon_key])['action'][attr]
                    for attr in attributes
                }
            else:
                attribute['uav'][platoon_key] = vars(
                    self.uav_platoons[platoon_key])['action']
        for i in range(self.config['simulation']['n_uav_platoons']):
            platoon_key = 'ugv_p_' + str(i + 1)
            if attributes:
                attribute['ugv'][platoon_key] = {
                    attr: vars(self.ugv_platoons[platoon_key])['action'][attr]
                    for attr in attributes
                }
            else:
                attribute['ugv'][platoon_key] = vars(
                    self.ugv_platoons[platoon_key])['action']
        return attribute

    def get_allocated_vehicle(self, n_vehicles, vehicles_type):
        """Allocated the vehicles to the platoons as required

        Parameters
        ----------
        n_vehicles : int
            Number of vehicles in the platoon
        vehicles_type : str
            Type of vehicles 'uav' or 'ugv'

        Returns
        -------
        vehicles_id: list
            A list of vehicles_id assigned to a platoon
        vehicles: list
            A list of vehicle instance of uav or ugv
        """
        vehicles_id = []
        if vehicles_type == 'uav':
            for uav in self.uav:
                if uav.idle and uav.functional:
                    vehicles_id.append(uav.vehicle_id)
                    uav.idle = False  # Once allocated they are non-idles

                if len(vehicles_id) == n_vehicles:
                    break
        else:
            for ugv in self.ugv:
                if ugv.idle and ugv.functional:
                    vehicles_id.append(ugv.vehicle_id)
                    ugv.idle = False  # Once allocated they are non-idles

                if len(vehicles_id) == n_vehicles:
                    break

        return vehicles_id

    def get_image(self, platoon_id, platoon_type, vehicle_id, image_type):
        """Get the image of the agent

        Parameters
        ----------
        platoon_id : int
            The platoon ID to vehicle belongs to.
        platoon_type : str
            Platoon type 'uav' or 'ugv'
        vehicle_id : int
            Vehicle ID from which image is acquired
        image_type : str
            Type of image to return rgb, seg, depth

        Returns
        -------
        array
            A image from the vehicle of required type
        """
        if platoon_type == 'uav':
            platoon_key = 'uav_p_' + str(platoon_id)
            image = self.uav_platoons[platoon_key].get_camera_image(
                vehicle_id, image_type)
        else:
            platoon_key = 'ugv_p_' + str(platoon_id)
            image = self.ugv_platoons[platoon_key].get_camera_image(
                vehicle_id, image_type)
        return image

    def perform_action_allocation(self, actions_uav, actions_ugv, uav_group,
                                  ugv_group):
        """Perfroms action allocation and

            Parameters
            ----------
            actions_uav : dict
                UAV decoded actions
            actions_ugv : dict
                UGV decoded actions
            """

        self.uav_platoons = uav_group
        self.ugv_platoons = ugv_group

        # UAV Actions
        for key in actions_uav:
            n_vehicles = actions_uav[key]['n_vehicles']

            # Allocate only when there are more than 0 vehicles
            if n_vehicles < 1:
                actions_uav[key]['execute'] = False
            else:
                # Perform vehicle allocation
                vehicles_id = self.get_allocated_vehicle(n_vehicles,
                                                         vehicles_type='uav')
                # Update actions
                actions_uav[key]['vehicles_id'] = vehicles_id
                actions_uav[key]['vehicles_type'] = 'uav'

            # Allocate
            self.uav_platoons[key].allocate_action(actions_uav[key])

        # UGV actions
        for key in actions_ugv:
            n_vehicles = actions_ugv[key]['n_vehicles']

            # Allocate only when there are more than 0 vehicles
            if n_vehicles < 1:
                actions_ugv[key]['execute'] = False
            else:
                # Perform vehicle allocation
                vehicles_id = self.get_allocated_vehicle(n_vehicles,
                                                         vehicles_type='ugv')
                # Update actions
                actions_ugv[key]['vehicles_id'] = vehicles_id
                actions_ugv[key]['vehicles_type'] = 'ugv'

            # Allocate
            self.ugv_platoons[key].allocate_action(actions_ugv[key])
        return None

    def make_vehicles_idle(self):
        for uav in self.uav:
            uav.idle = True
        for ugv in self.ugv:
            ugv.idle = True
        return None

    def roll_actions(self, ps):
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

        for key in self.uav_platoons:
            self.uav_platoons[key].execute_primitive(ps)
            self._p.stepSimulation()

        # Update all the ugv vehicles and write to parameter server
        for key in self.ugv_platoons:
            self.ugv_platoons[key].execute_primitive(ps)
            self._p.stepSimulation()

        return None
