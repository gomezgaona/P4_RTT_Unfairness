import jenkspy
import time

# Sample data
RTT = [0.1, 3, 20, 2, 12, 22, 9, 50, 60, 20, 70, 83, 25, 3, 45, 90, 88, 7, 2, 3, 4]
limits = [-1, -1, -1, -1]

def Jenks_classifier(RTT_flows):
    if len(RTT_flows) > 3:
        limits = jenkspy.jenks_breaks(RTT_flows, n_classes=4)
        return limits
    else:
        limits = jenkspy.jenks_breaks(RTT_flows, n_classes=len(RTT_flows))
        return limits
        
def run_classification(RTTs):
    RTT_list = []
    q1 = []
    q2 = []
    q3 = []
    q4 = []
    
    for i in range(0, len(RTTs) ):
        print("New RTT: ", RTTs[i], "ms")
        
        RTT_list.append(RTTs[i])
        limits = Jenks_classifier(RTT_list)
        
        if(limits[0] <= RTTs[i] <= limits[1]):
            print("Redirected to q1")
            q1.append(RTTs[i])
        elif(limits[1] <= RTTs[i] <= limits[2]):
            print("Redirected to q2")
            q2.append(RTTs[i])
        elif(limits[2] <= RTTs[i] <= limits[3]):
            print("Redirected to q3")
            q3.append(RTTs[i])
        elif(limits[3] <= RTTs[i] <= limits[4]):
            print("Redirected to q4")
            q4.append(RTTs[i])
        
        time.sleep(0.1)

    print("Queue 1:", q1)
    print("Queue 2:", q2)
    print("Queue 3:", q3)
    print("Queue 4:", q4)

    new_RTT = q1 + q2 + q3 + q4
    print(new_RTT)
    return new_RTT

def update_queues(RTTs):
    q1 = []
    q2 = []
    q3 = []
    q4 = []
    limits = Jenks_classifier(RTTs)

    for i in range(0, len(RTTs) ):
        if(limits[0] <= RTTs[i] <= limits[1]):
            q1.append(RTTs[i])
        elif(limits[1] <= RTTs[i] <= limits[2]):
            q2.append(RTTs[i])
        elif(limits[2] <= RTTs[i] <= limits[3]):
            q3.append(RTTs[i])
        elif(limits[3] <= RTTs[i] <= limits[4]):
            q4.append(RTTs[i])
    print("Updated queue")
    print("Queue 1:", q1)
    print("Queue 2:", q2)
    print("Queue 3:", q3)
    print("Queue 4:", q4)


new_RTT = run_classification(RTT)
update_queues(new_RTT)


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