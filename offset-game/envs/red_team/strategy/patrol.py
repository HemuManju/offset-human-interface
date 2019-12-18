from numpy import genfromtxt
import numpy as np


class Patrol(object):
    """This Class is to perform the chasing behaviour in the red team
    """
    def __init__(self, config):
        self.status = 'INVALID'
        self.location = 'Start'
        self.config = config
        self._initial_nodes_setup()
        self._initial_buildings_setup()

        return None

    def _initial_nodes_setup(self):
        """Performs initial nodes setup
        """
        # Nodes setup
        self.nodes = []
        path = self.config['map_data_path'] + 'nodes.csv'
        position_data = genfromtxt(path, delimiter=',')
        for i in range(self.config['simulation']['n_nodes']):
            info = {}
            info['position'] = [
                position_data[i][1] * 1.125, position_data[i][0] / 1.125
            ]
            info['importance'] = 0
            self.nodes.append(info)
        return None

    def _initial_buildings_setup(self):
        """Perfrom initial building setup.
        """
        # Buildings setup (probably we might need to read it from a file)
        self.buildings = []
        path = self.config['map_data_path'] + 'buildings.csv'
        data = genfromtxt(path, delimiter=',')
        for i in range(self.config['simulation']['n_buildings']):
            info = {}
            info['target_id'] = data[i][0]

            # Node info (a building is also a node)
            node_info = self.node_info(int(info['target_id']))
            info['position'] = node_info['position']
            info['area'] = data[i][1]
            info['perimeter'] = data[i][2]
            info['n_floors'] = data[i][3]
            self.buildings.append(info)
        return None

    def node_info(self, id):
        """Get the information about a node.

            Parameters
            ----------
            id : int
                Node ID

            Returns
            -------
            dict
                A dictionary containing all the information about the node.
            """
        return self.nodes[id]

    def update(self, complexity_states, complexity_actions, ps, count):
        """[This function set target position of the uav platoon
        according to nearest green team centroid]

        Parameters
        ----------
        ps : [object]
            [Parameter Server]
        platoon_id : [integer]
            [Number of platoon]

        Returns
        -------
        [type]
            [None]
        """
        key_main = 'uav_p_1'

        Node_1 = np.array(self.node_info(19)['position'])
        Node_2 = np.array(self.node_info(29)['position'])
        # print(Node_1)
        # print(Node_2)

        flag = np.array(complexity_actions['uav'][key_main]['centroid_pos'])
        # print(flag)
        if np.linalg.norm(flag - Node_1) < 0.1:
            self.location = 'Node_1'
            # print('111')
            # Set the target pos
            complexity_actions['uav'][key_main]['target_pos'] = Node_2

            # Set the primitive to planning
            complexity_actions['uav'][key_main]['primitive'] = 'planning'
            # Update the parameter server
            ps.set_complexity_actions.remote(
                complexity_actions['uav'][key_main])
        elif np.linalg.norm(flag - Node_2) < 0.1:
            # print('222')
            complexity_actions['uav'][key_main]['target_pos'] = Node_1
            # # Set the primitive to planning
            complexity_actions['uav'][key_main]['primitive'] = 'planning'
            # Update the parameter server
            ps.set_complexity_actions.remote(
                complexity_actions['uav'][key_main])
        elif count <= 20:
            complexity_actions['uav'][key_main]['target_pos'] = Node_1
            # # Set the primitive to planning
            complexity_actions['uav'][key_main]['primitive'] = 'planning'
            # Update the parameter server
            ps.set_complexity_actions.remote(
                complexity_actions['uav'][key_main])
