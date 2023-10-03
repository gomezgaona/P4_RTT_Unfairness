import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import json

font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 36}
f_size = 36
matplotlib.rc('font', **font)

def extract_iperf_timing(filename):
    
    f = open(filename)
    data = json.loads(open(filename).read())

    duration = data['start']['test_start']['duration']
    throughput = []

    for i in range(0,duration):
        throughput.append(data['intervals'][i]['sum']['bits_per_second']/1e9)

    return throughput

tput_flow_1 = extract_iperf_timing('jenks_tests/results/out1.json')
tput_flow_2 = extract_iperf_timing('jenks_tests/results/out2.json')

fig, plt = plt.subplots(1, 1, sharex=True,figsize=(10.5,6.75))
fig.subplots_adjust(hspace=0.1)

#Plot grids
plt.grid(True, which="both", lw=0.3, linestyle=(0,(1,10)), color='black')
plt.grid(True, which="both", lw=0.3, linestyle=(0,(1,10)), color='black')

#Colors
#Gold: #E5B245
#Blue: #2D72B7 
#Green: #82AA45
#Garnet: #95253B
#Orange: #FFA500

n_zeros = 31
zeros_shift = list(0 for _ in range(n_zeros))

t = range(0, len(tput_flow_1) )

#Plotting the metrics as a time's function
plt.plot(t[0:118], tput_flow_1[0:118], '#95253B', linewidth=2, label='1ms')  #label='Fairness', marker ='o'
plt.plot(t[0:118], zeros_shift + tput_flow_2[0:87], '#82AA45', linewidth=2, label='80ms')  #label='Fairness', marker ='o'

#Setting the y-axis labels and the x-axis label
plt.set_ylabel('Throughput [Gbps]', fontsize=f_size)
plt.set_xlabel('Time [seconds]', fontsize=f_size)

#Plot legends
#plt.legend(loc="lower right", fontsize=f_size)
plt.legend(loc="upper right", ncol=2, fontsize=f_size)

#Setting the position of the y-axis labels
plt.yaxis.set_label_coords(-0.09, 0.5)
#plt.xaxis.set_label_coords(-0.06, 0.5)
plt.set_xticks([0, 40, 80, 120], ['0', '40', '80', '120'])
#Setting the x-axis labels font size
#plt.tick_params(axis='y', labelsize=f_size)
#plt.tick_params(axis='y', labelsize=f_size)
#plt.tick_params(axis='x', labelsize=f_size)

#Setting the y-axis limits
plt.set_ylim([0,13.9])
plt.set_xlim([-1,121])

fig.savefig(f"bbr_wo_separation.pdf", bbox_inches='tight')