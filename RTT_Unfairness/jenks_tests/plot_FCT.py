import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import json



def extract_FCT(filename):
    
    f = open(filename)
    data = json.loads(open(filename).read())

    FCT = data['end']['sum_sent']['bits_per_second']/1e6

    return FCT

def main():
    global plt, np
    FCT1 = []
    FCT2 = []

    for i in range(1, 100):
        FCT1.append(extract_FCT(f'FCT_bbr_w_separation/out{i}.json'))
        FCT2.append(extract_FCT(f'FCT_bbr_wo_separation/out{i}.json'))
    
    sorted_data1 = np.sort(FCT1)
    y_values1 = np.arange(1, len(sorted_data1) + 1) / len(sorted_data1)
    sorted_data2 = np.sort(FCT2)
    y_values2 = np.arange(1, len(sorted_data2) + 1) / len(sorted_data2)

    font = {'family' : 'normal',
            'weight' : 'normal',
            'size'   : 26}
    matplotlib.rc('font', **font)

    fig, plt = plt.subplots(figsize=(9, 7.5))
    fig.subplots_adjust(hspace=0.1)

    # Create the CDF plot
    plt.plot(sorted_data1, y_values1, '#82AA45', linewidth=2, label='w/separation')
    plt.plot(sorted_data2, y_values2, '#95253B', linewidth=2, label='wo/separation')

    # Add labels and title
    plt.set_xlabel('Throughput [Mbps]')
    plt.set_ylabel('CDF')

    plt.legend(loc="lower right", ncol=1, fontsize=21)

    # Show the plot
    plt.grid(True, which="both", lw=0.3, linestyle=(0,(1,10)), color='black')
    plt.set_xlim([0, 200])
    #plt.show()
    fig.savefig(f"FCT_bbr.pdf", bbox_inches='tight')
    
if __name__ == '__main__':
    main()

'''
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
'''