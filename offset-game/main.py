import yaml
from pathlib import Path

import ray

from server.parameter_server import ParameterServer

from envs.red_team.red_base import RedTeam
from envs.blue_team.blue_base import BlueTeam

# from interaction.interaction_manager import InteractionManager
# from gui.main import MainGUI
# from lsl.mainlsl import Mainlsl

from utils import skip_run

config_path = Path(__file__).parents[0] / 'config/simulation_config.yml'
config = yaml.load(open(str(config_path)), Loader=yaml.SafeLoader)

with skip_run('run', 'Test Framework') as check, check():

    # Initiate ray
    if not ray.is_initialized():
        ray.init(num_cpus=10)

    # Instantiate parameter server
    ps = ParameterServer.remote(config, team_type='dynamic')

    # Instantiate red and blue teams
    red_team = RedTeam.remote(config)
    blue_team = BlueTeam.remote(config)

    # # Interaction Manager
    # interaction_manager = InteractionManager.remote(config)

    # # GUI
    # gui = MainGUI.remote(config, (1500, 750), ps)

    # Get the run ids
    blue_run_id = blue_team.step.remote(ps)
    red_run_id = red_team.step.remote(ps)
    # int_run_id = interaction_manager.step.remote(ps)
    # gui_run_id = gui.run.remote(ps)

    # Run all the clients in parallel
    ray.get([red_run_id, blue_run_id])

    # Shutdown ray
    ray.shutdown()