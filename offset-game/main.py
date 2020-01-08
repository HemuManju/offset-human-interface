import yaml
from pathlib import Path
import time

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
    # Initiate ray
    if not ray.is_initialized():
        ray.init(num_cpus=4)

    # Instantiate parameter server
    ps = ParameterServer.remote(config)

    # Instantiate environment
    env = BenningEnv.remote(config)

    # # Instantiate GUI
    # gui = MainGUI.remote(config, (1500, 750), ps)

    # Get the remote IDs of simulations
    # gui_run_id = gui.run.remote(ps)
    env_run_id = env.main_loop.remote()

    # Run the simulation
    ray.wait([env_run_id])

    # Shutdown ray
    ray.shutdown()
