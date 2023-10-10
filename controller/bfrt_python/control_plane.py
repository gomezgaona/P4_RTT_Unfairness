import os
from os import system
import time
import threading
import socket


#bfrt.rtt_separation.pipe
MAXIMUM_BUFFER = 200000
p4 = bfrt.rtt_unfairness.pipe
prev_N = 0
long_flows = {}
SRTT = 0
avg_rtt = 0
ALPHA = 0.8
BW=5000000000
prev_rtt=0
prev_rtt_bscl=0
q_hat = 0.5 # 200ms
avg_q = 0 
loss_rate_hat_headroom = 0.00525
loss_rate_hat = 0.010 - loss_rate_hat_headroom# 2%
B_max = BW * q_hat / 8 # Maximum buffer size in bytes
B_min = 0
prev_bytes_counter = 0
total_sent = 0
total_retr = 0
avg_link_util = 0
avg_tput = 0
avg_loss_rate = 0
buffer = 0
new_flow=False
r = BW * 0.0025 / 1000
N = 0
prev_total_sent = -1
prev_total_retr = -1

src_IP_addr=0
instant_RTT=0



def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)

def new_long_flow(dev_id, pipe_id, direction, parser_id, session, msg):
    #print("1-new_long_flow")
    global p4
    global long_flows
    #print(msg)
    for digest in msg:
        long_flows[digest['rev_flow_id']] = 0
        p4.Ingress.counted_flow.add_with_meter(flow_id=digest['flow_id'], ENTRY_TTL = 1000)
    return 0

def long_flow_timeout(dev_id, pipe_id, direction, parser_id, entry):
    global p4
    global long_flows
    #print("2-long_flow_timeout")
    try:
        flow_id = entry.key[b'meta.flow_id']
        del long_flows[flow_id]
        if(len(long_flows) == 0):
            p4.Ingress.counted_flow.clear()
            p4.Ingress.sketch0.clear()
            p4.Ingress.sketch1.clear()
            p4.Ingress.sketch2.clear()
            p4.Ingress.sketch3.clear()
    except Exception as e:
            print(e)

def update_srtt():
    #print("3-update_srtt")
    import time
    while (1):
        if(len(long_flows) >  0):
            long_flows_copy = long_flows.copy()
            global prev_rtt
            global SRTT
            sum = 0
            for key, value in long_flows_copy.items():
                if(float(long_flows_copy[key]) < 100000000):
                    sum += (float(long_flows_copy[key]) / 1e9)
            
            avg_rtt = sum / len(long_flows_copy)
            ALPHA = 0.875
            if(prev_rtt == 0):
                prev_rtt = avg_rtt
            SRTT = avg_rtt
            '''
            if (SRTT != 0):
                #SRTT = ALPHA * SRTT + (1-ALPHA) * avg_rtt
            else:
                SRTT = avg_rtt
                
            prev_rtt = SRTT
        else:
            SRTT=0
            prev_rtt=0
            '''
        time.sleep(0.1)

def rtt_sample(dev_id, pipe_id, direction, parser_id, session, msg):
    global p4
    global rtts
    global long_flows
    global update_srtt
    global src_IP_addr
    global instant_RTT
    #print("4-rtt_sample")
    for digest in msg:
        
        if digest['flow_id'] in long_flows:
            long_flows[digest['flow_id']]  = str(digest['rtt'])
            src_IP_addr = digest['IP_addr']
            #print(str(digest['rtt']))
            instant_RTT = str(digest['rtt'])
    return 0



def queue_delay_sample():
    #print("5-queue_delay_sample")
    global p4
    import time
    global avg_q
    prev_q = 0
    count_same = 0
    queue_delay = 0
    while (1):
        previous_sample = queue_delay        
        queue_delay = p4.Egress.queue_delays.get(REGISTER_INDEX=0, from_hw=True, print_ents=False).data[b'Egress.queue_delays.f1'][1]
        queue_delay = (queue_delay) / (200000000)
        if(queue_delay == 0):
            avg_q = 0
            continue
        
        if(queue_delay == previous_sample):
            avg_q = 0
        else:
            avg_q = queue_delay
    
        time.sleep(0.1)
    return 0



def calc_link_util():
    #print("6-calc_link_util")
    global prev_bytes_counter
    global p4
    global avg_link_util
    global avg_tput
    global BW
    import time
    while (1):
        link_util_result=0
        new_bytes_counter = p4.Ingress.link_stats.get(COUNTER_INDEX=0, print_ents=False, from_hw=True).data[b'$COUNTER_SPEC_BYTES']
        link_util = (new_bytes_counter - prev_bytes_counter) * 8
        if(link_util < 0):
            link_util = 0
        if(link_util != 0):
            if(link_util/BW * 100 > 100):
                link_util_result = 100
            else:
                link_util_result = link_util/(BW) * 100
        prev_bytes_counter = new_bytes_counter
        
        ALPHA = 0.2
        if (avg_link_util != 0):
            avg_link_util = ALPHA * avg_link_util + (1-ALPHA) * link_util_result
            avg_tput = ALPHA * avg_tput + (1-ALPHA) * link_util
        else:
            avg_link_util = link_util_result
            avg_tput = link_util
        time.sleep(1)
       


def calc_loss_rate():    #<---- based on retransmissions
    #print("7-calc_loss_rate")
    global p4
    global prev_total_sent
    global prev_total_retr
    global total_sent
    global total_retr
    global avg_loss_rate
    import time
    global avg_link_util
    
    from datetime import datetime
    i=0
    tt=0
    while(1):
        rate = 0
        total_sent = float(p4.Ingress.total_sent.get(REGISTER_INDEX=0, from_hw=True, print_ents=False).data[b'Ingress.total_sent.f1'][1])
        total_retr = float(p4.Ingress.total_retr.get(REGISTER_INDEX=0, from_hw=True, print_ents=False).data[b'Ingress.total_retr.f1'][1])
        tt+=total_retr - prev_total_retr
        if(i%10 ==0 and i > 0):
            # os.system("echo " + str(datetime.now().timestamp()) + ',' + str(tt) + " >> /home/P4_Measurement_Collector/stats_loss.csv")
            tt=0
        i+=1
        if(prev_total_sent == -1):
            prev_total_sent = total_sent
        if(prev_total_retr == -1):
            prev_total_retr = total_retr
        if (total_sent - prev_total_sent != 0):
            rate = ((total_retr - prev_total_retr) / (total_sent - prev_total_sent) ) 
        
        if(avg_link_util < 90):
            avg_loss_rate = 0
            prev_total_sent = -1
            prev_total_retr = -1
        else:
            rate = rate * 1.4
            
            if(avg_loss_rate < 0):
                avg_loss_rate = 0
            
            ALPHA = 0.8
            if (avg_loss_rate != 0):
                avg_loss_rate = ALPHA * avg_loss_rate+ (1-ALPHA) * rate
            else:
                avg_loss_rate = rate
                                        
            prev_total_sent = total_sent 
            prev_total_retr = total_retr
            
        time.sleep(0.1)
        
prev_total_before = -1
prev_total_after = -1
prev_rate = - 1
total_before=0
total_after=0

def reset_sketches():
    #print("8-reset_sketches")
    global p4
    import time
    global long_flows
    
    while (True):
        time.sleep(4)
        p4.Ingress.sketch0.clear()
        p4.Ingress.sketch1.clear()
        p4.Ingress.sketch2.clear()
        p4.Ingress.sketch3.clear()
        
def get_N():
    #print("9-get_N")
    import time
    global N
    global prev_N
    global long_flows
    while(1):  
        #print(N)
        N = len(long_flows)
        time.sleep(1)
        
try:
    p4.Ingress.counted_flow.idle_table_set_notify(enable=True, callback=long_flow_timeout, interval=500, min_ttl=400, max_ttl=1000)
    p4.IngressDeparser.new_long_flow_digest.callback_register(new_long_flow)
    p4.IngressDeparser.rtt_sample_digest.callback_register(rtt_sample)
    # p4.IngressDeparser.before_after.callback_register(calc_loss_rate2)
    p4.Egress.lpf_queue_delay_1.add(0, 'SAMPLE', 1000000, 1000000, 0)
except:
    print('Error registering callback')
    
weight_loss = 0.5#0.9
weight_delay = 0.5#0.1
prev_loss = 0
prev_q = 0
prev_obj_function_value=0
last_loss_used=10
last_q_used=0
    
    
calc_link_util_thread = threading.Thread(target=calc_link_util, name="calc_link_util")
calc_loss_rate_thread = threading.Thread(target=calc_loss_rate, name="calc_loss_rate")
calc_queue_delay_thread = threading.Thread(target=queue_delay_sample, name="queue_delay_sample")
get_N_thread = threading.Thread(target=get_N, name="get_N")
#update_srtt_thread = threading.Thread(target=update_srtt, name="update_srtt")
periodic_reset = threading.Thread(target=reset_sketches, name="reset_sketches")

calc_link_util_thread.start()
calc_loss_rate_thread.start()
calc_queue_delay_thread.start()
get_N_thread.start()
periodic_reset.start()
#update_srtt_thread.start()

os.system("echo "" > test_buffers")
last_good_buffer = 0
bs = False
print ("   N  |     Throughput  |    Link utilization  |   Loss rate  |     RTT  |    Current Buffer")
print ('--------------------------------------------------------------------------------------------')



sock = socket.socket()         # Create a socket object
host = socket.gethostname()    # Get local machine name
port = 60002                   # Reserve a port for your service.
sock.connect((host, port))

weight_loss  = 0.5
weight_delay = 0.5


last_buffer = 0

current_buffer = 0

i=0
while(1):
    stat_instant_RTT = instant_RTT
    #stat_instant_RTT = "{:.4f}".format(instant_RTT)
    stat_LOSS = "{:.4f}".format(avg_loss_rate)
    stat_Q = "{:.4f}".format(avg_q)
    stat_LINK = "{:.4f}".format(avg_link_util)    
    if((float(stat_Q) == 0) or N == 0):
        i+=1
    else:
        i=0

    if(i==100): #10):
        try:
            i=0
            long_flows.clear()
            prev_rtt = 0
            instant_RTT = 0
              
            p4.Ingress.calc_flow_id.clear() 
            prev_total_before = -1
            prev_total_after = -1
            avg_loss_rate = 0
            p4.Ingress.calc_rev_flow_id.clear()    
            p4.Ingress.copy32_1.clear()    
            p4.Ingress.copy32_2.clear()    
            p4.Ingress.crc16_1.clear()    
            p4.Ingress.crc16_2.clear()    
            p4.Ingress.crc32_1.clear()    
            p4.Ingress.crc32_2.clear()    

            p4.Ingress.last_seq.clear()    
            p4.Ingress.link_stats.clear()    
  
            p4.Ingress.reg_table_1.clear()    
            p4.Ingress.rev_hash.clear()    
   
            p4.Ingress.total_retr.clear()    
            p4.Ingress.total_sent.clear()    
            
            long_flows.clear()
            p4.Ingress.sketch0.clear()
            p4.Ingress.sketch1.clear()
            p4.Ingress.sketch2.clear()
            p4.Ingress.sketch3.clear()

            

        except Exception as e:
            print(e)
            pass
    
    # if(current_buffer/200000 > float(stat_Q)):
    print('IP: ' + str(src_IP_addr) + '\tSRTT: ' + 
    str(stat_instant_RTT) + '\tLoss: ' + str(stat_LOSS) + '\tQ: ' + str(stat_Q) + '\tLink: ' + str(stat_LINK))

    #stats = str(N) + '_' + str(stat_SRTT) + '_' + str(stat_LOSS) + '_' + str(stat_Q) + '_' + str(stat_LINK)
    #Here is where the program sends the metrics to the listener ( the other python program)
    stats = str(src_IP_addr) +'_' + str(stat_instant_RTT) + '_' + str(N) # + '_' + str(stat_LOSS) + '_' + str(stat_Q) + '_' + str(stat_LINK)
    sock.send(stats.encode())
    print()
    time.sleep(0.01)

sock.close()                     # Close the socket when done

