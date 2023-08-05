import numpy as np

from .synapse import Synapse, SynapseList
from .constants import W_E, W_ACC, W_BAR_ACC, W_I, G_MULT, T_SYN, T_MIN, T_NEU

neural_functions = {
    "logarithm": {
        "t": 0.5,
        "neuron_names": ["input", "first", "last", "acc", "output"],
        "synapses": np.asarray([
            SynapseList("input", "first", np.asarray([
                Synapse("V", W_E, T_SYN)
            ])),
            SynapseList("first", "first", np.asarray([
                Synapse("V", W_I, T_SYN)
            ])),
            SynapseList("input", "last", np.asarray([
                Synapse("V", 0.5 * W_E, T_SYN)
            ])),
            SynapseList("first", "acc", np.asarray([
                Synapse("g_e", W_BAR_ACC, T_SYN + T_MIN)
            ])),
            SynapseList("last", "acc", np.asarray([
                Synapse("g_e", -W_BAR_ACC, T_SYN),
                Synapse("g_f", G_MULT, T_SYN),
                Synapse("gate", 1, T_SYN)
            ])),
            SynapseList("last", "output", np.asarray([
                Synapse("V", W_E, 2 * T_SYN)
            ])),
            SynapseList("acc", "output", np.asarray([
                Synapse("V", W_E, T_SYN + T_MIN)
            ]))
        ]),
        "output_idx": [4]
    },
    "maximum": {
        "t": 1,
        "neuron_names": ["input", "inputtwo", "larger", "largertwo", "output"],
        "synapses": np.asarray([
            SynapseList("input", "largertwo", np.asarray([
                Synapse("V", 0.5 * W_E, T_SYN)
            ])),
            SynapseList("input", "output", np.asarray([
                Synapse("V", 0.5 * W_E, T_SYN)
            ])),
            SynapseList("inputtwo", "output", np.asarray([
                Synapse("V", 0.5 * W_E, T_SYN)
            ])),
            SynapseList("inputtwo", "larger", np.asarray([
                Synapse("V", 0.5 * W_E, T_SYN + T_MIN)
            ])),
            SynapseList("larger", "largertwo", np.asarray([
                Synapse("V", W_I, T_SYN),
            ])),
            SynapseList("largertwo", "larger", np.asarray([
                Synapse("V", W_I, T_SYN)
            ]))
        ]),
        "output_idx": [4]
    },
    "inverting_memory": {
        "t": 0.8,
        "neuron_names": ["input", "first", "last", "acc",
                         "recall", "output"],
        "synapses": np.asarray([
            SynapseList("input", "first", np.asarray([
                Synapse("V", W_E, T_SYN)
            ])),
            SynapseList("first", "first", np.asarray([
                Synapse("V", W_I, T_SYN)
            ])),
            SynapseList("input", "last", np.asarray([
                Synapse("V", 0.5 * W_E, T_SYN)
            ])),
            SynapseList("first", "acc", np.asarray([
                Synapse("g_e", W_ACC, T_SYN + T_MIN)
            ])),
            SynapseList("last", "acc", np.asarray([
                Synapse("g_e", -W_ACC, T_SYN),
            ])),
            SynapseList("acc", "output", np.asarray([
                Synapse("V", W_E, T_SYN)
            ])),
            SynapseList("recall", "acc", np.asarray([
                Synapse("g_e", W_ACC, T_SYN)
            ])),
            SynapseList("recall", "output", np.asarray([
                Synapse("V", W_E, 2 * T_SYN)
            ]))
        ]),
        "output_idx": [5]
    },
    "non_inverting_memory": {
        "t": 0.8,
        "neuron_names": ["input", "first", "last", "acc", "acctwo",
                         "recall", "ready", "output"],
        "synapses": np.asarray([
            SynapseList("input", "first", np.asarray([
                Synapse("V", W_E, T_SYN)
            ])),
            SynapseList("first", "first", np.asarray([
                Synapse("V", W_I, T_SYN)
            ])),
            SynapseList("input", "last", np.asarray([
                Synapse("V", 0.5 * W_E, T_SYN)
            ])),
            SynapseList("first", "acc", np.asarray([
                Synapse("g_e", W_ACC, T_SYN)
            ])),
            SynapseList("acc", "acctwo", np.asarray([
                Synapse("g_e", -W_ACC, T_SYN)
            ])),
            SynapseList("last", "acctwo", np.asarray([
                Synapse("g_e", W_ACC, T_SYN)
            ])),
            SynapseList("acc", "ready", np.asarray([
                Synapse("V", W_E, T_SYN)
            ])),
            SynapseList("recall", "acctwo", np.asarray([
                Synapse("g_e", W_ACC, T_SYN)
            ])),
            SynapseList("recall", "output", np.asarray([
                Synapse("V", W_E, T_SYN)
            ])),
            SynapseList("acctwo", "output", np.asarray([
                Synapse("V", W_E, T_SYN)
            ]))
        ]),
        "output_idx": [7]
    },
    "full_subtractor": {
        "t": 1,
        "neuron_names": ["inputone", "inputtwo", "syncone",
                         "synctwo", "inbone", "inbtwo", "output+", "output-", "zero"],
        "output_idx": [6, 7],
        "synapses": np.asarray([
            SynapseList("inputone", "syncone", np.asarray([
                Synapse("V", 0.5 * W_E, T_SYN)
            ])),
            SynapseList("inputtwo", "synctwo", np.asarray([
                Synapse("V", 0.5 * W_E, T_SYN)
            ])),
            SynapseList("syncone", "output+", np.asarray([
                Synapse("V", W_E, T_MIN + 3 * T_SYN + 2 * T_NEU)
            ])),
            SynapseList("syncone", "inbone", np.asarray([
                Synapse("V", W_E, T_SYN)
            ])),
            SynapseList("syncone", "output-", np.asarray([
                Synapse("V", W_E, 3 * T_SYN + 2 * T_NEU)
            ])),
            SynapseList("syncone", "inbtwo", np.asarray([
                Synapse("V", W_I, T_SYN)
            ])),
            SynapseList("synctwo", "inbone", np.asarray([
                Synapse("V", W_I, T_SYN)
            ])),
            SynapseList("synctwo", "output+", np.asarray([
                Synapse("V", W_E, 3 * T_SYN + 2 * T_NEU)
            ])),
            SynapseList("synctwo", "inbtwo", np.asarray([
                Synapse("V", W_E, T_SYN)
            ])),
            SynapseList("synctwo", "output-", np.asarray([
                Synapse("V", W_E, T_MIN + 3 * T_SYN + 2 * T_NEU)
            ])),
            SynapseList("inbone", "output+", np.asarray([
                Synapse("V", 2 * W_I, T_SYN)
            ])),
            SynapseList("inbtwo", "output-", np.asarray([
                Synapse("V", 2 * W_I, T_SYN)
            ])),
            SynapseList("output+", "inbtwo", np.asarray([
                Synapse("V", 0.5 * W_E, T_SYN)
            ])),
            SynapseList("output-", "inbone", np.asarray([
                Synapse("V", 0.5 * W_E, T_SYN)
            ])),
            SynapseList("zero", "zero", np.asarray([
                Synapse("V", W_E, T_NEU)
            ])),
            SynapseList("synctwo", "zero", np.asarray([
                Synapse("V", 0.5 * W_E, T_NEU),
                Synapse("V", 0.5 * W_I, 2 * T_NEU)
            ])),
            SynapseList("syncone", "zero", np.asarray([
                Synapse("V", 0.5 * W_E, T_NEU),
                Synapse("V", 0.5 * W_I, 2 * T_NEU)
            ])),
            SynapseList("zero", "inbtwo", np.asarray([
                Synapse("V", W_I, T_NEU),
            ])),
            SynapseList("zero", "output-", np.asarray([
                Synapse("V", 2 * W_I, T_NEU),
            ]))
        ])
    }
}
