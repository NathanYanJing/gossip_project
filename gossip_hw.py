import sys
import os
import time
import socket
import random
import traceback
import ipaddress

from socket import gethostbyname
from threading import Lock
from threading import Thread

# validate the correctness of IP
# line protocol
# node_dict serves to keep tracking the current status of the nodes
# examples
'''
{
    node_id: 
        {"ip":,
         "port":,
         "time":,
         "digit":
        }
}
'''
def get_my_internal_ip():
    # dummpy way to get the IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

my_port = int(sys.argv[1]) # for test su
my_ip = get_my_internal_ip()
my_node_id = f"{my_ip}:{my_port}"
# line protocol
# node_dict serves to keep tracking the current status of the nodes
node_dict = {}
# cap the maximal 
ip_port_map = {}
MAX_NODES = 3
my_digit = 0 # in range 0-9, 0 represents to start
my_update_time = -1 # represents the time that has not started yet --> avoid confusion
block_set = []
MAX_SLEEP = 3


def ip_validation(ip):
    try:
        temp_ip = ipaddress.ip_address(ip)
#         print('%s is a correct IP%s address.' % (temp_ip, temp_ip.version))
        return True
    except ValueError:
        print('address/netmask is invalid: %s' % ip)
        return False
    except:
        print('Usage : %s  ip' % ip)
        return False

# validate the correctness of port
def port_validation(port):
    flag = False
    if 0 <= int(port) <= 65534:
        flag = True
    else:
        flag= False
        print("Invalid Port Input")

    return flag

def node_validation(line_input):
    ip = line_input.split(':')[0]
    port = line_input.split(':')[1]
    this_node_id = f"{ip}:{port}"
    flag = False
    if ip_validation(ip) and port_validation(int(port)):
        flag = True
    if this_node_id == my_node_id:
        flag = False
    
    return flag

def msg_parser(line_input):
    # parasing message to the right format
    line_input_list = line_input.strip().split(',')
    try:
        node_id = line_input_list[0]
        time = line_input_list[1]
        digit = line_input_list[2]
        ip = node_id.split(':')[0]
        port = node_id.split(':')[1]
        return ip, port, time, digit, node_id
    except:
        print("Errors in the msg received")  

# line protocol from here
# adding node to the ip_port_map
def line_protocol_add_node(line_input):
    '''
    Input: line protocol input
    nodes: a dictionary of all the nodes
           key: {IP:port}.format
           value: (time, digit) tuple
    '''
    ip = line_input.split(':')[0]
    port = line_input.split(':')[1]
    # Lock().acquire()
    if line_input == my_node_id:
        print("This is node is currently used by the current server")
    elif ip_validation(ip) and port_validation(port):
        if line_input not in node_dict.keys():
            node_dict[line_input] = {
                "ip": ip,
                "port":int(port),
                "time": -1,
                "digit":0 
            }
            if ip not in ip_port_map .keys():
                ip_port_map[ip] = []
                ip_port_map[ip].append(int(port))
    # try:
    #     Lock().release()
    # except:
    #     print("No thread is locked")

def line_protocol_remove_node(node_id):
    try:
        ip = node_id.split(':')[0]
        port = node_id.split(':')[1]
        if node_id in node_dict.keys():
            node_dict.pop(node_id)
            # print(int(port))
            ip_port_map[ip].remove(int(port))
    except:
        print("node has been removed")

# the protocol only allows up to three nodes in the same time
def line_protocol_remove_earliest_node():
    current_time = int(time.time())
    current_min_time = None
    current_earliest_node_id = None
    
    if len(ip_port_map[node_id.split(':')[0]]) > MAX_NODES:
        # find the most recent one
        for item in ip_port_map[node_id.split(':')[0]]:
            temp_ip = node_id.split(':')[0]
            temp_node_id = f"{temp_ip}:{item}"
            if node_dict[temp_node_id]["time"] < current_time:
                current_min_time = node_dict[temp_node_id]["time"]
                current_earliest_node_id = temp_node_id
    
    if current_earliest_node_id is not None:
        print('***Exceeding Maximal Port', current_earliest_node_id)
        line_protocol_remove_node(current_earliest_node_id)


def line_protocol_update_node(node_id, update_time, update_digit):
    global my_update_time, my_digit 
    if  1< update_time <= int(time.time()):
        line_protocol_add_node(node_id)
        # Lock().acquire()
        # update time and digit
        print("update time and digit information")
        node_dict[node_id]["time"] = update_time
        node_dict[node_id]["digit"] = update_digit
        line_protocol_remove_earliest_node(node_id)
        
        # check port
        # Lock().release()

def line_protocol_contact_node(node_id):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connecting to the node
        s.settimeout(3) # set the time out to be 3 seconds
        s.connect((node_dict[node_id]["ip"], node_dict[node_id]["port"]))
        s.settimeout(None)
        read_lines = ''
        data = s.recv(4096)
        print(data)
        if data:
            read_lines += data.decode(encoding='utf-8', errors='strict')
            data = s.recv(4096)
            # print(read_lines)
            messages = read_lines.splitlines()
            msg_count = 0
            for msg in messages:
#                 print(msg)
                while msg_count<256: # cap is 256
                    # try:
                        ip, port, update_time, update_digit, node_id =  msg_parser(msg)
                        if node_validation(node_id):
                            line_protocol_update_node(node_id, update_time, update_digit) 
                        msg_count += 1
                    # except:
                    #     print("Error parsing the messgage, return the main menu")
        else:
            print("No message fetched")
        s.close()
    except Exception as error:
        print("Error contacting the node", node_id)
        print(traceback.format_exc())
        block_set.append(node_id)
        # Lock().acquire()
        line_protocol_remove_node(node_id)
        # Lock().release()


def server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((get_my_internal_ip(), my_port))
    print(get_my_internal_ip())
    s.listen()
    while True:
        conn, addr = s.accept()
        if conn:
            print(f"connected to {addr}")
        msgs_updated_from_connection = []
        # Lock().acquire()
        for node_id in node_dict.keys():
            cur_update_time = node_dict[node_id]["time"]
            cur_update_digit = node_dict[node_id]["digit"]
            msgs_updated_from_connection.append(f"{node_id}, {cur_update_time}, {cur_update_digit}").encode('ascii')

        # update msg on my end
        if my_update_time > 0:
            my_node_ip = socket.gethostname()
            my_node_id = f"{my_node_ip}:{my_port}"
            my_new_msg =  f"{my_node_id},{my_update_time},{digit}\n"
            msgs_updated_from_connection.append(my_new_msg.encode('ascii'))
        # nodes_lock.release()
        
        for msg in msgs_updated_from_connection:
            conn.sendall(msg)

        conn.close()
        print('Digit Sent')
        # Lock().release()
    s.close()


def client():
    while True:
        time.sleep(MAX_SLEEP)
        # Lock().acquire()
        # get all current nodes
        nodes_list = list(node_dict.keys())
        node_id = None
        if len(nodes_list)>1:
            node_id = random.choice(nodes_list)
            if node_id not in block_set:
                print('>> Contacting: ', node_id)
                line_protocol_contact_node(node_id)
                print(node_id)
        # except:
        #     print("Error raisesd while having the client thread contacting")


block_set = []
MAX_SLEEP = 3
# node_dict = {'127.0.0.1:8081': {'ip': '127.0.0.1',
#   'port': 8081,
#   'time': 123,
#   'digit': 123},
#  '127.0.0.1:8082': {'ip': '127.0.0.1', 'port': 8082, 'time': -1, 'digit': 0},
#  '127.0.0.1:8083': {'ip': '127.0.0.1', 'port': 8083, 'time': -1, 'digit': 0}}

# client()



# main_module
# merging all information from input
def gossip_nodes(line_input):
    # +127.0.0.1:5658
    line_input = str(line_input)
    if str(line_input).startswith('+'):
        line_input = line_input[1:]
        print('Adding node', str(line_input))
    
    # Lock().acquire()
    if line_input not  in node_dict.keys():
        if node_validation(line_input):
            line_protocol_add_node(line_input)
            line_protocol_contact_node(line_input)
    # Lock().release()

# Shows nodes in the map
def protocol_nodes_info():
    # Lock().acquire()
    for node_id in node_dict.keys():
        line_info = f"{node_id},{node_dict[node_id]['time']},{node_dict[node_id]['digit']}\n"
        print(line_info)
    my_line_info = f"{my_node_id},{my_update_time},{ my_digit}\n"
    print(my_line_info)
    # Lock().release()

def gossip_protocol(line_input):
    global my_digit, my_update_time
    line_input = str(line_input).strip()
    if line_input.startswith('+'):
        gossip_nodes(line_input)
    if line_input.isdigit():
        my_digit = int(line_input)
        my_update_time = int(time.time())
    elif line_input.lower() == 'info':
        protocol_nodes_info()

# main thread: takes input
print('my node:', get_my_internal_ip(), 'PORT:', my_port)
server_thread = Thread(target=server)
client_thread = Thread(target=client)

client_thread.start()
server_thread.start()

while True:
    input("Please enter a node to add, or show information, or a digit to change")
    input_line = input(">> ")
    # try:
    gossip_protocol(input_line)
    # except:
    #     print("Your input is incorrect, please fix")