import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import json

font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 26}
f_size = 26
matplotlib.rc('font', **font)

def extract_iperf_timing(filename):
    
    f = open(filename)
    data = json.loads(open(filename).read())

    duration = data['start']['test_start']['duration']
    throughput = []

    for i in range(0,duration):
        throughput.append(data['intervals'][i]['sum']['bits_per_second']/1e9)

    return throughput

tput_flow_1 = extract_iperf_timing('out1.json')
tput_flow_2 = extract_iperf_timing('out2.json')
tput_flow_3 = extract_iperf_timing('out3.json')
tput_flow_4 = extract_iperf_timing('out4.json')

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

size = 60
zeros_shift_1 = list(0 for _ in range(size))
zeros_shift_2 = list(0 for _ in range(2*size))
zeros_shift_3 = list(0 for _ in range(3*size))

t = range(0, len(tput_flow_1) )
print(len(tput_flow_2))
#Plotting the metrics as a time's function
plt.plot(t, tput_flow_1, '#95253B', linewidth=2, label='0.1ms')  #label='Fairness', marker ='o'
plt.plot(t, zeros_shift_1 + tput_flow_2, '#82AA45', linewidth=2, label='30ms')  #label='Fairness', marker ='o'
plt.plot(t, zeros_shift_2 + tput_flow_3, '#E5B245', linewidth=2, label='50ms')  #label='Fairness', marker ='o'
plt.plot(t, zeros_shift_3 + tput_flow_4, '#2D72B7', linewidth=2, label='70ms')  #label='Fairness', marker ='o'
print(tput_flow_4)
#Setting the y-axis labels and the x-axis label
plt.set_ylabel('Throughput [Gbps]', fontsize=f_size)
plt.set_xlabel('Time [seconds]', fontsize=f_size)

#Plot legends
#plt.legend(loc="lower right", fontsize=f_size)
plt.legend(loc="upper right", ncol=2, fontsize=21)

#Setting the position of the y-axis labels
plt.yaxis.set_label_coords(-0.12, 0.5)
#plt.xaxis.set_label_coords(-0.06, 0.5)

#Setting the x-axis labels font size
#plt.tick_params(axis='y', labelsize=f_size)
#plt.tick_params(axis='y', labelsize=f_size)
#plt.tick_params(axis='x', labelsize=f_size)

#Setting the y-axis limits
plt.set_ylim([0,12.5])#throughput
plt.set_xlim([-1,len(tput_flow_1)+1])#fairness

fig.savefig(f"tput_time.pdf", bbox_inches='tight')