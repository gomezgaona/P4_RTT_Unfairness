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
    rtt = []

    for i in range(0, duration):
        rtt.append(data['intervals'][i]['streams'][0]['rtt']/1e3)

    return rtt

tput_flow_1 = extract_iperf_timing('results/out5.json')
tput_flow_2 = extract_iperf_timing('results/out34.json')
tput_flow_3 = extract_iperf_timing('results/out68.json')
tput_flow_4 = extract_iperf_timing('results/out92.json')
'''
tput_flow_1 = list(-5 for _ in range(720))
tput_flow_2 = list(-5 for _ in range(540))
tput_flow_3 = list(-5 for _ in range(360))
tput_flow_4 = list(-5 for _ in range(180))

for i in range(1, 26):
    tmp = extract_iperf_timing(f'results/out{i}.json')
    for j in range(0, len(tmp)):
        tput_flow_1[j] += tmp[j]/25

for i in range(26, 51):
    tmp = extract_iperf_timing(f'results/out{i}.json')
    for j in range(0, len(tmp)):
        tput_flow_2[j] += tmp[j]/25

for i in range(51, 76):
    tmp = extract_iperf_timing(f'results/out{i}.json')
    for j in range(0, len(tmp)):
        tput_flow_3[j] += tmp[j]/25

for i in range(76, 101):
    tmp = extract_iperf_timing(f'results/out{i}.json')
    for j in range(0, len(tmp)):
        tput_flow_4[j] += tmp[j]/25
'''
fig, plt = plt.subplots(1, 1, sharex=True,figsize=(18, 3.75))
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

size = 180
zeros_shift_1 = list(-5 for _ in range(size))
zeros_shift_2 = list(-5 for _ in range(2*size))
zeros_shift_3 = list(-5 for _ in range(3*size))

t = range(0, len(tput_flow_1) )
print(len(tput_flow_2))
#Plotting the metrics as a time's function
plt.plot(t, tput_flow_1, '#95253B', linewidth=2)  #label='Fairness', marker ='o'
plt.plot(t, zeros_shift_1 + tput_flow_2, '#82AA45', linewidth=2)  #label='Fairness', marker ='o'
plt.plot(t, zeros_shift_2 + tput_flow_3, '#E5B245', linewidth=2)  #label='Fairness', marker ='o'
plt.plot(t, zeros_shift_3 + tput_flow_4, '#2D72B7', linewidth=2)  #label='Fairness', marker ='o'
#print(tput_flow_4)
#Setting the y-axis labels and the x-axis label
plt.set_ylabel('RTT [ms]', fontsize=f_size)
plt.set_xlabel('Time [seconds]', fontsize=f_size)

#Plot legends
#plt.legend(loc="lower right", fontsize=f_size)


#Setting the position of the y-axis labels
plt.yaxis.set_label_coords(-0.06, 0.5)
#plt.xaxis.set_label_coords(-0.06, 0.5)

#Setting the x-axis labels font size
plt.set_xticks([0, 180, 360, 540, 720], ['0', '180', '360', '540', '720'])
plt.set_yticks([0, 50, 100, 150], ['0', '50', '100', '150'])
plt.fill_between(range(0, 9), -5, 400,  alpha=0.25, color='lightsteelblue')
plt.fill_between(range(179, 189), -5, 400,  alpha=0.35, color='lightsteelblue')
plt.fill_between(range(359, 369), -5, 400,  alpha=0.35, color='lightsteelblue')
plt.fill_between(range(539, 549), -5, 400,  alpha=0.35, color='lightsteelblue')

plt.plot(4, 160, 'ro', clip_on=False, color='#95253B', markersize=10,  label='$\hat{N}$=25, 20ms\nN=25\nRTT=30ms')
plt.plot(184, 160, 'ro', clip_on=False, color='#82AA45', markersize=10,  label='$\hat{N}$=25, 50ms\nN=25\nRTT=60ms')
plt.plot(364, 160, 'ro', clip_on=False, color='#E5B245', markersize=10,  label='$\hat{N}$=25, 70ms\nN=75\nRTT=75ms')
plt.plot(544, 160, 'ro', clip_on=False, color='#2D72B7', markersize=10,  label='$\hat{N}$=25, 100ms\nN=100\nRTT=105ms')
plt.legend(loc="upper center", ncol=4, fontsize=21, bbox_to_anchor=(0.5, 1.6), numpoints=1)
#Setting the y-axis limits
plt.set_ylim([-0.5,150])#throughput
plt.set_xlim([-10,735])#throughput
plt.set_xlim([-1, len(tput_flow_1)+1])#fairness

fig.savefig(f"rtt_cubic_w_separation.pdf", bbox_inches='tight')