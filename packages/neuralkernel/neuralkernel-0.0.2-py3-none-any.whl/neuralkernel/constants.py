# time constants in ms
TO_MS = 1000
T_TO_POS = 10
T_MIN = 10
T_COD = 100
T_MAX = T_MIN + T_COD  # time range
T_SYN = 1
T_NEU = 0.1  # slightly modified from paper

# voltage constants in mV
TAU_M = 100 * TO_MS
TAU_F = 20
V_THRESHOLD = 10
V_RESET = 0  # voltage model params
W_E = V_THRESHOLD
W_I = -V_THRESHOLD  # std. voltage weights
G_MULT = V_THRESHOLD * TAU_M / TAU_F
W_ACC = V_THRESHOLD * TAU_M / T_MAX
W_BAR_ACC = V_THRESHOLD * TAU_M / T_COD
