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

def extract_throughput(filename):
    for i in range(0, rows):
        #print(f'jenks_results/out{i+1}.json')
        tmp = extract_iperf_timing(filename + f'out{i+1}.json')
        for j in range(1, cols):
            throughput[i][j] = tmp[j]
    
    return throughput

def calc_fairness(throughput):
    fairness = [0 for i in range(cols)]  
    nflows = len(throughput)    
    for i in range(1, cols):
        num = 0
        den = 0
        for j in range(0, nflows):
            num += throughput[j][i]
            den += throughput[j][i]**2
            #print(num,den)
        fairness[i] += 100*num**2 / (nflows * den)

    return fairness

def aggregate_throughput(throughput, files):
    th = [0] * cols

    for i in files:
        for j in range(1, cols):
            th[j] += throughput[i-1][j]

    return th


throughput_1 = extract_throughput(f'jenks_results_cubic_10_flows_no_separation/')
throughput_2 = extract_throughput(f'jenks_results_cubic_10_flows_w_separation/')
th = [[0] * cols for _ in range(4)]

files = [4, 10, 9, 5, 1, 2]
queue = 2
th[queue-1] = aggregate_throughput(throughput_2, files)
files = [6]
queue = 3
th[queue-1] = aggregate_throughput(throughput_2, files)
files = [3]
queue = 4
th[queue-1] = aggregate_throughput(throughput_2, files)
files = [8, 7]
queue = 1
th[queue-1] = aggregate_throughput(throughput_2, files)

fairness_no_separation = calc_fairness(th)
fairness_with_separation = calc_fairness(throughput_2)

fig, plt = plt.subplots(2, 1, sharex=True,figsize=(10.5,6.75))
fig.subplots_adjust(hspace=0.1)

#Plot grids
plt[0].grid(True, which="both", lw=0.3, linestyle=(0,(1,10)), color='black')
plt[1].grid(True, which="both", lw=0.3, linestyle=(0,(1,10)), color='black')

#Colors
#Gold: #E5B245
#Blue: #2D72B7 
#Green: #82AA45
#Garnet: #95253B
#Orange: #FFA500

t = range(0, cols)

#Plotting the metrics as a time's function
plt[0].plot(t[1:], fairness_no_separation[1:], '#82AA45', linewidth=2, label='with separation')  #label='Fairness', marker ='o'
plt[1].plot(t[1:], fairness_with_separation[1:], '#95253B', linewidth=2, label='without separation')  #label='Fairness', marker ='o'

#Setting the y-axis labels and the x-axis label
plt[0].set_ylabel('Fairness [%]', fontsize=f_size)
plt[1].set_ylabel('Fairness [%]', fontsize=f_size)
plt[1].set_xlabel('Time [seconds]', fontsize=f_size)

#Plot legends
#plt.legend(loc="lower right", fontsize=f_size)
plt[0].legend(loc="lower right", ncol=2, fontsize=21)
plt[1].legend(loc="lower right", ncol=2, fontsize=21)

#Setting the position of the y-axis labels
plt[0].yaxis.set_label_coords(-0.10, 0.5)
plt[1].yaxis.set_label_coords(-0.10, 0.5)
#plt.xaxis.set_label_coords(-0.06, 0.5)

#Setting the x-axis labels font size
#plt.tick_params(axis='y', labelsize=f_size)
#plt.tick_params(axis='y', labelsize=f_size)
#plt.tick_params(axis='x', labelsize=f_size)

#Setting the y-axis limits
plt[0].set_ylim([19, 105])
plt[1].set_ylim([19, 105])
plt[0].set_xlim([-1, cols+1])#fairness

fig.savefig(f"fairness_jenks_results.pdf", bbox_inches='tight')