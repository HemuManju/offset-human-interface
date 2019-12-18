import yaml
from pathlib import Path
import time
import collections

import ray

from lsl.stream_data import states_packets
from server.parameters import ParameterServer
from gui.main import MainGUI
from envs.benning_env import BenningEnv

from utils import skip_run

config_path = Path(__file__).parents[1] / 'offset-game/config.yml'
config = yaml.load(open(str(config_path)), Loader=yaml.SafeLoader)

with skip_run('skip', 'Game Test') as check, check():

    # Initiate ray
    if not ray.is_initialized():
        ray.init(num_cpus=5)

    # Instantiate parameter server
    ps = ParameterServer.remote(config)

    # Instantiate environment
    env = BenningEnv.remote(config)

    # Instantiate GUI
    gui = MainGUI.remote(config, (1500, 750), ps)

    gui_run_id = gui.run.remote(ps)
    env_run_id = env.step.remote(ps)
    ray.wait([env_run_id, gui_run_id])
    print(time.time() - ray.get(gui.get_start_time.remote()))

    # Shutdown ray
    ray.shutdown()

with skip_run('skip', 'Complexity Test') as check, check():

    # Initiate ray
    if not ray.is_initialized():
        ray.init(num_cpus=4)

    # Instantiate parameter server
    ps = ParameterServer.remote(config)

    # Instantiate complex environment

    # Instantiate environment
    env = BenningEnv.remote(config)

    # Instantiate GUI
    gui = MainGUI.remote(config, (1500, 750), ps)

    # Get the remote IDs of simulations
    gui_run_id = gui.run.remote(ps)
    env_run_id = env.step.remote(ps)

    # Get the labstreaming data
    lsl_state_id = states_packets.remote(ps)

    # Run the simulation
    ray.wait([env_run_id, gui_run_id, lsl_state_id])
    print(time.time() - ray.get(gui.get_start_time.remote()))

    # Shutdown ray
    ray.shutdown()

with skip_run('run', 'Test New Framework') as check, check():
    read_path = Path(__file__).parents[0] / 'test.yml'
    parameters = yaml.load(open(str(read_path)), Loader=yaml.SafeLoader)

    actions_uav = collections.defaultdict(dict)
    actions_ugv = collections.defaultdict(dict)
    actions_uav_b = collections.defaultdict(dict)
    actions_ugv_b = collections.defaultdict(dict)

    for i in range(config['simulation']['n_uav_platoons']):
        uav_parameters = parameters['uav'].copy()
        key = 'uav_p_' + str(i + 1)
        uav_parameters['platoon_id'] = i + 1
        actions_uav[key] = uav_parameters
        actions_uav_b[key] = uav_parameters.copy()  # Strange

    # Setup the uav platoons
    for i in range(config['simulation']['n_ugv_platoons']):
        ugv_parameters = parameters['ugv'].copy()
        key = 'ugv_p_' + str(i + 1)
        ugv_parameters['platoon_id'] = i + 1
        actions_ugv[key] = ugv_parameters
        actions_ugv_b[key] = ugv_parameters.copy()

    env = BenningEnv(config)
    env.step(actions_uav, actions_ugv)
