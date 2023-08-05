import numpy as np

from .synapse import Synapse
from .constants import T_TO_POS, T_NEU, V_THRESHOLD


class AdjMatrix(object):

    def __init__(self, neurons: list, synapses: np.ndarray) -> None:
        self.neurons = neurons
        self.synapse_matrix = np.empty((len(self.neurons), len(self.neurons)), dtype=object)
        neuron_names = [neuron.name for neuron in self.neurons]
        for synapse_list in synapses:
            i = neuron_names.index(synapse_list.n_from)
            j = neuron_names.index(synapse_list.n_to)
            self.synapse_matrix[i][j] = synapse_list

    def simulate(self) -> None:
        """update voltages for neurons"""

        t = self.neurons[0].t  # retrieve time window
        for tj in range(1, t.size):
            for ni in range(len(self.neurons)):
                self.neurons[ni].next_v(tj)
                if self.neurons[ni].v[tj] >= V_THRESHOLD:
                    # check adjacency matrix for synapses to send out
                    for n_to in range(0, len(self.neurons)):
                        if self.synapse_matrix[ni][n_to] is not None:
                            for syn in self.synapse_matrix[ni][n_to].synapses:
                                self.synapse_prop(syn, n_to, tj)

    def synapse_prop(self, syn: Synapse, n_to: int, tj: float) -> None:
        """propagate the synapse through the adjacency matrix"""

        t_delay = tj + int(T_TO_POS * (syn.s_delay + T_NEU))
        if syn.s_type is "V":
            self.neurons[n_to].v[t_delay] += syn.s_weight
        elif syn.s_type is "g_e":
            self.neurons[n_to].g_e[t_delay] += syn.s_weight
        elif syn.s_type is "g_f":
            self.neurons[n_to].g_f[t_delay] += syn.s_weight
        elif syn.s_type is "gate":  # gate synapse
            self.neurons[n_to].gate[t_delay] = {1: 1, -1: 0}[syn.s_weight]
