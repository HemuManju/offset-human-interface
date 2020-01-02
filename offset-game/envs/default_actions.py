import yaml
from pathlib import Path
import collections


def blue_team_actions(state_manager, config):
    # Variables
    default_actions = collections.defaultdict(dict)

    # Read fields for all the platoons
    read_path = Path(__file__).parents[0] / 'blue_team_config.yml'
    attr = yaml.load(open(str(read_path)), Loader=yaml.SafeLoader)

    # Setup the uav platoons
    ids = 0
    for i in range(config['simulation']['n_uav_platoons']):
        actions_uav = attr['uav'].copy()
        key = 'uav_p_' + str(i + 1)
        actions_uav['platoon_id'] = i + 1
        actions_uav['n_vehicles'] = attr['uav_platoon']['n_vehicles'][i]

        # Assign the ids
        n_vehicles = actions_uav['n_vehicles']
        vehicles_id = list(range(ids, ids + n_vehicles))
        ids = ids + n_vehicles
        actions_uav[key]['vehicles_id'] = vehicles_id

        # Get the node position
        node_id = attr['uav_platoon']['initial_nodes_pos'][i]
        node_info = state_manager.node_info(node_id)
        actions_uav['target_pos'] = node_info['position']

        # Update the uav action
        default_actions['uav'][key] = actions_uav

    # Setup the uav platoons
    ids = 0
    for i in range(config['simulation']['n_ugv_platoons']):
        actions_ugv = attr['ugv'].copy()
        key = 'ugv_p_' + str(i + 1)
        actions_ugv['platoon_id'] = i + 1
        actions_ugv['n_vehicles'] = attr['ugv_platoon']['n_vehicles'][i]

        # Assign the ids
        n_vehicles = actions_ugv['n_vehicles']
        vehicles_id = list(range(ids, ids + n_vehicles))
        ids = ids + n_vehicles
        actions_ugv[key]['vehicles_id'] = vehicles_id

        # Get the node position
        node_id = attr['uav_platoon']['initial_nodes_pos'][i]
        node_info = state_manager.node_info(node_id)
        actions_uav['target_pos'] = node_info['position']

        # Update the ugv action
        default_actions['ugv'][key] = actions_ugv
    return default_actions


def red_team_actions(state_manager, config):
    # Variables
    default_actions = collections.defaultdict(dict)

    # Read fields for all the platoons
    read_path = Path(__file__).parents[0] / 'red_team_config.yml'
    attr = yaml.load(open(str(read_path)), Loader=yaml.SafeLoader)

    # Setup the uav platoons
    ids = 0
    for i in range(config['simulation']['n_uav_platoons']):
        actions_uav = attr['uav'].copy()
        key = 'uav_p_' + str(i + 1)
        actions_uav['platoon_id'] = i + 1
        actions_uav['n_vehicles'] = attr['uav_platoon']['n_vehicles'][i]

        # Assign the ids
        n_vehicles = actions_uav['n_vehicles']
        vehicles_id = list(range(ids, ids + n_vehicles))
        ids = ids + n_vehicles
        actions_uav[key]['vehicles_id'] = vehicles_id

        # Get the node position
        node_id = attr['uav_platoon']['initial_nodes_pos'][i]
        node_info = state_manager.node_info(node_id)
        actions_uav['target_pos'] = node_info['position']

        # Update the uav action
        default_actions['uav'][key] = actions_uav

    # Setup the uav platoons
    ids = 0
    for i in range(config['simulation']['n_ugv_platoons']):
        actions_ugv = attr['ugv'].copy()
        key = 'ugv_p_' + str(i + 1)
        actions_ugv['platoon_id'] = i + 1
        actions_ugv['n_vehicles'] = attr['ugv_platoon']['n_vehicles'][i]

        # Assign the ids
        n_vehicles = actions_ugv['n_vehicles']
        vehicles_id = list(range(ids, ids + n_vehicles))
        ids = ids + n_vehicles
        actions_ugv[key]['vehicles_id'] = vehicles_id

        # Get the node position
        node_id = attr['uav_platoon']['initial_nodes_pos'][i]
        node_info = state_manager.node_info(node_id)
        actions_uav['target_pos'] = node_info['position']

        # Update the ugv action
        default_actions['ugv'][key] = actions_ugv
    return default_actions
