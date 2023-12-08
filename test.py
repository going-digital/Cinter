import math
import matplotlib.pyplot as plt
import numpy as np

# Plot target for quarter circle sine wave
target = np.array([math.floor(16384*math.sin((i+0.5) * math.pi/8192)) for i in range(4096)])
plt.plot(target)

# Plot for polynomial sine wave approximation from Cinter
cinter = [None] * 4096
for d7 in range(4096):
    d1 = math.floor(d7*d7/256)
    d0 = 2373
    d0 = math.floor(d0 * -d1/65536)
    d0 = d0 + 21073
    d0 = math.floor(d0 * -d1/65536)
    d0 = d0 + 51469
    d0 = math.floor(d0 * d7/8192)
    cinter[d7] = d0
plt.plot(cinter)

# Cinter error compared to target
cinter_error = np.array(cinter) - np.array(target)
plt.plot(cinter_error)
plt.title("Cinter error")

# Modified coupled form sine wave
def sin_gen_mcf(j_scaler, init_j=0, init_s=0, init_c=0x4000000):
    osc = np.zeros(4096)
    s, c = init_s, init_c
    i = 0
    j = init_j
    while i < 4096:
        j += j_scaler
        if j > 255:
            # Carry is set from above addition
            j -= 256
            osc[i] = s/4096
            i += 1
        s = s + np.floor(c/4096) # Shift right 12
        c = c - np.floor(s/4096) # Shift right 12
    return osc

max_err = 1000
best_j = 0
for init_j in range(0, 255):
    osc = sin_gen_mcf(j_scaler=163, init_j=init_j)
    err = np.abs(
            np.array(osc)-np.array(target)
    )
    if max(err) < max_err:
        max_err, best_j = max(err), init_j
        print(best_j, max_err)

print("Best value for initial j is {}".format(best_j))

# This gives the best_j as 46.

# Calculate MCF table, and graph error compared to ideal result.
osc = sin_gen_mcf(163, best_j)
err = osc-target
plt.plot(osc)
plt.plot(target)
plt.title("Table output")
plt.show()
plt.plot(err)
plt.title("MCF error")

# Simulate 68000 code
#
num_phase_loops = 0
num_outer_loops = 0
CINTER_DEGREES = 16384
osc = np.zeros(CINTER_DEGREES)
osc[:] = -10000 # Dummy value to spot any missing table entries later
a0 = 0
a1 = CINTER_DEGREES//2 # In simulation, a0-a1 are word addresses, not byte.
d0 = 0
d1 = 1<<(32-6)  # 1 ror 6
d3 = 46         # Found from code above
d7 = CINTER_DEGREES//4-1
while True:
    num_phase_loops += 1
    d2 = d1
    d2 = d2 >> 12 # Divide by 4096
    d0 += d2
    d2 = d0
    d2 = d2 >> 12
    d1 -= d2
    d3 += 163 # Trim out some values to reduce 6433 down to 4096
    if d3 < 256:
        continue
    num_outer_loops += 1
    d3 -= 256
    d2 -= 2
    d4 = d2
    d4 = -d4
    osc[CINTER_DEGREES//2+a0] = d4
    osc[a0] = d2
    a0 += 1
    a1 -= 1
    osc[a1] = d2
    osc[CINTER_DEGREES//2+a1] = d4
    d2 = -d2
    d7 -= 1
    if d7 < 0:
        break
print(num_phase_loops, num_outer_loops)
plt.plot(osc)

target = np.array([math.floor(16384*math.sin((i+0.5) * math.pi/8192)) for i in range(16384)])
plt.plot(osc-target)

