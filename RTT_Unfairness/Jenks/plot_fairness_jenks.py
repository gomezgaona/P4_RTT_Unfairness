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

rows = 10
cols = 120
throughput = [[0] * cols for _ in range(rows)]

for i in range(0, rows):
    print(f'jenks_results/out{i+1}.json')
    tmp = extract_iperf_timing(f'jenks_results/out{i+1}.json')
    for j in range(1, cols):
        throughput[i][j-1] = tmp[j]
        #print(i,j)

#print(throughput)
'''
tput_flow_1 = extract_iperf_timing('jenks_results/out1.json')
tput_flow_2 = extract_iperf_timing('jenks_results/out2.json')
tput_flow_3 = extract_iperf_timing('jenks_results/out3.json')
tput_flow_4 = extract_iperf_timing('jenks_results/out4.json')
tput_flow_5 = extract_iperf_timing('jenks_results/out5.json')
tput_flow_6 = extract_iperf_timing('jenks_results/out6.json')
tput_flow_7 = extract_iperf_timing('jenks_results/out7.json')
tput_flow_8 = extract_iperf_timing('jenks_results/out8.json')
tput_flow_9 = extract_iperf_timing('jenks_results/out9.json')
tput_flow_10 = extract_iperf_timing('jenks_results/out10.json')
'''

fairness = [0 for i in range(cols)]     
for i in range(1, cols):
    num = 0
    den = 0
    for j in range(0, rows):
        num += throughput[j][i]
        den += throughput[j][i]**2
        print(num,den)
    fairness[i] += 100*num**2 / (10 * den)

fig, plt = plt.subplots(1, 1, sharex=True,figsize=(10.5,6.75))
fig.subplots_adjust(hspace=0.1)
print(fairness)
#Plot grids
plt.grid(True, which="both", lw=0.3, linestyle=(0,(1,10)), color='black')
plt.grid(True, which="both", lw=0.3, linestyle=(0,(1,10)), color='black')

#Colors
#Gold: #E5B245
#Blue: #2D72B7 
#Green: #82AA45
#Garnet: #95253B
#Orange: #FFA500

t = range(0, len(tput_flow_1))
print(len(tput_flow_2))
#Plotting the metrics as a time's function
plt.plot(t, fairness, '#95253B', linewidth=2, label='q1')  #label='Fairness', marker ='o'

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
plt.set_ylim([0, 105])#throughput
plt.set_xlim([-1, len(tput_flow_1)+1])#fairness

fig.savefig(f"fairness_jenks_results.pdf", bbox_inches='tight')