import matplotlib.pyplot as plt
import numpy as np

from .adjmatrix import AdjMatrix
from .neuron import Neuron
from .predefined_models import neural_functions
from .constants import TO_MS


# TODO: remove warning when running this
def plot_output_neurons(output_neurons: list, outputs: list) -> None:
    output_neurons = np.take(output_neurons, outputs)

    fig = plt.figure(1, figsize=(15, 10), facecolor='white')

    big_ax = fig.add_subplot(111)  # overarching subplot

    # Turn off axis lines and ticks of the big subplot
    big_ax.spines['top'].set_color('none')
    big_ax.spines['bottom'].set_color('none')
    big_ax.spines['left'].set_color('none')
    big_ax.spines['right'].set_color('none')
    big_ax.tick_params(labelcolor='w', top='off', bottom='off', left='off', right='off')

    big_ax.set_xlabel('time (ms)')
    big_ax.set_ylabel('voltage (mV)')

    for i in range(output_neurons.size):
        num = int(str(output_neurons.size) + "1" + str(i + 1))

        ax = fig.add_subplot(num)
        ax.plot(output_neurons[i].t, output_neurons[i].v)
        ax.set_title('voltage for ' + output_neurons[i].name)
        start, end = ax.get_xlim()
        ax.xaxis.set_ticks(np.arange(start, end, 100))
        ax.grid(True)

    plt.show()


def simulate_neurons(data: dict) -> (list, list):
    """implementation of a neuralkernel model"""

    neural_function = neural_functions[data['function']]
    t = np.multiply(TO_MS, np.arange(0, neural_function["t"], 1e-4))  # time in MS

    # neurons and synapses
    neurons = [Neuron(neuron_name, t) for neuron_name in neural_function["neuron_names"]]
    for neuron_name, spike_indices in data['initial_values'].items():
        neurons[neural_function["neuron_names"].index(neuron_name)].populate_spikes_from_data(spike_indices)
    synapses = neural_function["synapses"]

    adj_matrix = AdjMatrix(neurons, synapses)
    adj_matrix.simulate()

    return neural_function["output_idx"], adj_matrix.neurons
