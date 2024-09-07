from pox.core import core
import pox.openflow.libopenflow_01 as of

# MY NOTES: with the topology connected to a controller, now when switches receive a packet, it will reach out to this ethernet-learning.py to be told what to do with the given packet...

# Even a simple usage of the logger is much nicer than print!
log = core.getLogger()


# !!!!! PROJ3 Define your data structures here
all_switch_tables = {} # DICT (key == switchID, value == switch_table)


# Handle messages the switch has sent us because it has no
# matching rule.

def _handle_PacketIn (event): #MY NOTES: every time a switch receives a packet, it will call this method from this event, and itll do some packet parsing/bookkeeping, and then you'll send back some 'decision' to it (the decision on what it should do with the packet)

  # get the port the packet came in on for the switch contacting the controller
  packetInPort = event.port

  # use POX to parse the packet
  packet = event.parsed

  # get src and dst mac addresses
  src_mac = str(packet.src)
  dst_mac = str(packet.dst)

  # get switch ID
  switchID = str(event.connection.dpid) + str(event.connection.ID)
  
  log.info('Packet has arrived: SRCMAC:{} DSTMAC:{} from switch:{} in-port:{}'.format(src_mac, dst_mac, switchID, packetInPort))

  # !!!!! PROJ3 Your logic goes here
  
  # ******************************************************************
  # DATA STRUCTURE OVERVIEW:
  # ******************************************************************
  
  # CONTROLLER: 
  # the controller learns/maps the network with a DICT called all_switch_tables. The key-value pairs of this dict are the switchID and the corresponding switch table 
  # (key == switchID, val == switch_table) 
  # This allows the controller to quickly check if it already has a switch_table for the switch that just sent it the packet in question, while also ensuring it doesn't have 
  # multiple tables for the same switch.

  # SWITCH-TABLE: 
  # a switch table is a LIST, called switch_table, where each elem is itself a DICT (and this DICT will have TWO elements, each of which is a key-val pair)
  # The 2-elem DICT's will be as follows: (one element is for the mac address and the other is for the port)
  #  left elem: key-mac:addr-val
  #  right elem: key-port:port-val

  # The primary task the controller needs to be able to do is search through a particular switches table to match the packets address (either source or dest) with the address in the table. 
  # Because each element of the table is a dictionary, the address the controller needs in the table is the 'value' of the first element. 
  # So for each entry in the table, it will evaluate that entries first element by referencing the "mac" key to get the associated 'value', which is the actual address for the entry, and this 
  # is the value the controller will be trying to match the packets addresses with.
  
  # ******************************************************************
  # STEP 1: ensuring the controller has an entry for this switchID...
  # ******************************************************************
  if switchID in all_switch_tables:
    pass # entry already in controllers dict, no need to create one
  else:
    #add an empty switch table for the given switch (using switchID as key in dict)
    all_switch_tables[switchID] = []

  # accessing the table specific to the switch which sent the packet...
  switch_table = all_switch_tables[switchID]


  # ******************************************************************
  # STEP 2: check if need to add the 'source' related mapping to switch table...
  # ******************************************************************
  match_found = False
  for elem in switch_table: # check if this source-port mapping is already in table...
    if elem["mac"] == packet.src: # packet.src == source mac address 
      match_found = True # mapping already in table, so can break out of the loop
      break

  if not match_found: # entry not already present, so add as entry in switch_table
    switch_table.append({"mac": packet.src, "port": packetInPort})


  # ******************************************************************
  # STEP 3: search for dest-port entry and handle the two cases
  # ******************************************************************
  # TWO CASES: the switch table has the dest-port or it doesn't (aka match_found vs not-found)
  match_found = False
  corresp_port_num = None # if match is found, then we want to save the corresp port number 
  # iterating through the switches table to find a key that matches the packets dest address...
  for elem in switch_table:
    if elem["mac"] == packet.dst: # packet.dst == dest mac address 
      match_found = True # match found, therefore we can get the port number the switch needs
      corresp_port_num = elem["port"] # this is the port number we'll send back to the switch
      break # no purpose in further looping since we already found the port we needed
  
  # HANDLING THE TWO CASES...
  if match_found: 
    # ************************************************
    # CASE 1: MATCH FOUND: send results back to switch
    # ************************************************
    # building response message with the port num found...
    response_to_switch = of.ofp_flow_mod() 
    response_to_switch.match.dl_dst = packet.dst
    response_to_switch.actions.append(of.ofp_action_output(port = corresp_port_num))
    event.connection.send(response_to_switch)
    print("sending packet to port ", corresp_port_num)
    response_to_switch = of.ofp_packet_out(data=event.ofp)
    response_to_switch.actions.append(of.ofp_action_output(port = corresp_port_num))
    event.connection.send(response_to_switch)
  else:
    # ************************************************
    # CASE 2: MATCH NOT-FOUND: tell switch to flood 
    # ************************************************
    # building response message to inform the switch to flood all of its other ports
    print("flooding packet")
    response_to_switch = of.ofp_packet_out(data=event.ofp)
    response_to_switch.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
    event.connection.send(response_to_switch)


def launch ():
  core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
  log.info("Pair-Learning switch running.")
