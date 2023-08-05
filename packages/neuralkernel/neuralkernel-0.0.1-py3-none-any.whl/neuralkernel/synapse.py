import numpy as np


class Synapse(object):

    def __init__(self, s_type: str, s_weight: float, s_delay: float) -> None:
        self.s_type = s_type
        self.s_weight = s_weight
        self.s_delay = s_delay


class SynapseList(object):

    def __init__(self, n_from: str, n_to: str, synapses: np.ndarray) -> None:
        self.n_from = n_from
        self.n_to = n_to
        self.synapses = synapses
