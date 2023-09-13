import jenkspy
import time

# Sample data
RTTs = [0.1,3, 10, 12, 2, 50, 60, 20, 70, 83, 25, 3, 45, 90, 88, 7, 2, 3, 4]


def Jenks_classifier(RTT_flows):
    if len(RTT_flows) >= 4:
        # Find natural breaks (jenks) in the data
        limits = jenkspy.jenks_breaks(RTT_flows, n_classes=4)
        return limits
    else:
        return "q1"

RTT_list = []
limits = [0, 20, 40, 60, 80]
for i in range(0, len(RTTs) ):
    print("New RTT: ", RTTs[i], "ms")
    
    RTT_list.append(RTTs[i])
    queue_limits = Jenks_classifier(RTT_list)
    
    if(len(RTT_list) >= 4):
        limits = queue_limits
        print(limits)

    if(limits[0] <= RTTs[i] <= limits[1]):
        print("Redirected to q1")
    elif(limits[1] <= RTTs[i] <= limits[2]):
        print("Redirected to q2")
    elif(limits[2] <= RTTs[i] <= limits[3]):
        print("Redirected to q3")
    elif(limits[3] <= RTTs[i] <= limits[4]):
        print("Redirected to q4")
    

    time.sleep(2)

'''

# Print the breaks
print("Natural Breaks:")
print(breaks)
for i in range(len(breaks) - 1):
    print(f"Queue {i + 1}: {breaks[i]} - {breaks[i + 1]}")

# Classify the data points into queues based on the breaks
enqueued_data = []
for value in data:
    for i in range(len(breaks) - 1):
        if breaks[i] <= value < breaks[i + 1]:
            enqueued_data.append((value, i + 1))
            break
    else:
        enqueued_data .append((value, len(breaks) - 1))

# Print the classified data
print("\nqueueified Data:")
for value, queue_label in enqueued_data :
    print(f"{value} => Queue {queue_label}")
'''