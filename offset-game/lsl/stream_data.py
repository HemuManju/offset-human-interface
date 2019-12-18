import time
from datetime import date

import ujson

from pylsl import StreamInfo, StreamOutlet

import ray


@ray.remote
def states_packets(ps):

    # Create stream info
    today = date.today()
    info = StreamInfo('parameter_server_states', 'parameters', 1, 0, 'string',
                      'states-' + str(today))

    # Add meta data
    info.desc().append_child_value('start_time', "%.6f" % time.time())

    # next make an outlet
    outlet = StreamOutlet(info)

    print("Now sending states data...")
    while True:
        # Read the latest states and stream them
        states = ray.get(ps.get_states.remote())

        # Serialise the states
        sample = [ujson.dumps(states)]

        # now send it and wait for a bit
        outlet.push_sample(sample)
        time.sleep(0.01)
