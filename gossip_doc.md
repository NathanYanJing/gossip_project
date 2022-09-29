# Gossip Project Documentation

This serves as the documentation of Gossip Project, more details and our codebases could be found in our [Github Repo](https://github.com/NathanYanJing/gossip_demo). This project is done jointly by Jing Nathan Yan and Jack Wang. Our project is implemented in python. 

# Files

- gossip.py: has all node creation, update, and remove functions, server and client functions for three threads, we will include a detailed explanation in the late paragraph. 
- main.py: the main program where we give the input in the format of ``IP:PORT`` to start gossip. 


## Gossip_hw.py

### Global variables
- nodes_dict: a map of {key:value} pairs where the key is the `IP:PORT` and value has all the node information(IP, port, digit, and time)
- ip_port_dict:  a map of  {key:value} pairs where the key is the IP address of a node, and value is a list of ports that this IP has used. 
- MAX_IP_NUM: maximum IPs that
- my_update_time, my_port, my_ip

### Environment Check Module
- ``def ip_validation``: a function to validate the input ip from console;
- ``def port_validation``:   a function to validate the input port from console;
- ``def ip_port_check``: check whether the an input ip has been used, and record its port. If an input ip has been used, we will update current node's port information. Other wise, we will create such ip in our track dictionary;
- ``def line_parser``: accept bytes input, decoding into string format and line protocol format;
- ``def input_parser``: parse the input to start the main thread;

### Node Maintenance Module (Based on line protocol)
- `def line_protocol_add_node`: adding a node to the  nodes_dict;
- `def line_protocol_remove_node`: removing a node from the  nodes_dict;
- `def line_protocol_update_node`: update the digit and time of a node in the nodes_dict;
- when the number of nodes from an input IP exceeds MAX_IP_NUM, remove the earliest one;
- `def line_protocol_contact_node`: establish the connection with other nodes, and update the node information in nodes_dict including update the node, remove a failed node etc;
- `def line_protocol_my_node`: get the information of my node;

## threads Module
- `def line_protocol_server`: Thread 1 -- receive the information from other nodes and update existing digits;
- `def line_protocol_client`: Thread 2 -- read the input, and select ports to gossip;


# Running
```
python3 main.py IP(your input) PORT(your input)
```
|  |  |
|--|--|
|  |  |

