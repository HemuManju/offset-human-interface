import collections

import pyxdf
import ujson

import numpy as np


def read_xdf_data(config):
    # read_path = config
    streams, fileheader = pyxdf.load_xdf('block_T1.xdf')
    grouped_data = collections.defaultdict(dict)

    for ix, stream in enumerate(streams):
        name = stream['info']['name'][0]
        stream_type = stream['info']['type'][0]
        avg_sfreq = np.mean(1 / np.diff(stream['time_stamps']))
        data = ujson.loads(stream['time_series'][ix][0])
        time_stamps = stream['time_stamps']
        start_time = stream['info']['start_time'][0]
        duration = stream['time_stamps'][-1] - stream['time_stamps'][0]

        # Meta data
        meta_info = {
            'type': stream_type,
            'sfreq': avg_sfreq,
            'duration': duration,
            'start_time': start_time
        }

        # Data dictionary
        grouped_data[name]['info'] = meta_info
        grouped_data[name]['data'] = data
        grouped_data[name]['time_stamps'] = time_stamps

    return grouped_data
