from scipy.spatial import cKDTree


class KDDict(dict):

    def __init__(self, source_dict, target_dict):
