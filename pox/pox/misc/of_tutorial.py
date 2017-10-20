                                                                                                                                

"""                                                                                                                                                              
CMPE 210 Project: Learning Switch implemented in Mininet using Pox controller.
Developed by:
Naveen 20 011409229	
Ankita 07 010804833
Shweta 17 010130107
Arpit 52 010810514                                                                                                     
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from pox.openflow.of_json import *
from pox.lib.recoco import Timer
import os.path
import thread
import time

log = core.getLogger()
''' Below function handles the received flow statistics from the switch
    It takes event statistics as input '''

def _handle_portstats_received (event):
    # structure of event.stats is defined by ofp_flow_stats()
    # handler to display flow statistics received in JSON format
    stats = flow_stats_to_list(event.stats)
    #log.debug("PortStatsReceived from %s: %s",dpidToStr(event.connection.dpid), stats)

def update_flow(self,stats):
    connection.send(of.ofp_flow_mod(command=of.OFPFC_DELETE_STRICT,action=of.ofp_action_output(port=stats.next.next.dstport),match=of.ofp_match(dl_type=stats.type,nw_src=stats.srcip,nw_dst=stats.dstip)))
    return 

def _handle_flowstats_received (event):

    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    f = open(os.path.join(__location__, 'test_data.txt'),"r+");
    stats = flow_stats_to_list(event.stats)
    try:
      thread.start_new_thread(self.update_flow(stats))
      time.sleep(delay)
    except:
      log.debug("Unable to start the thread")
    #log.debug("FlowStatsReceived from %s: %s",dpidToStr(event.connection.dpid),stats)

    '''connectionlist table keeps the track of number of connections
       per mac address'''
    connectionlist={}
    for i in stats:
	
	for key,values in i['match'].items():
		print key, values
		if values not in connectionlist:
			connectionlist[values] = 1
		else:
			connectionlist[values] += 1
			''' This condition sets the threshold on the number of maximum connections.'''
			if connectionlist[values] > 5:
			        
                                __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
                                f = open(os.path.join(__location__, 'reject_mac.txt'),"r+");
                                log.debug("Keys:")
                                log.debug(keys)
                                log.debug("Values:")
                                log.debug(values)
    				f.write(values)
    				f.close()
				

    print connectionlist
    print "\n"
    web_bytes = 0
    web_flows = 0
    web_packet = 0
    for f in event.stats:
      if f.match.tp_dst == 80 or f.match.tp_src == 80:
        web_bytes += f.byte_count
        web_packet += f.packet_count
        web_flows += 1
    #log.info("Web traffic from %s: %s bytes (%s packets) over %s flows",dpidToStr(event.connection.dpid), web_bytes, web_packet, web_flows)


#This function handles the port statistics from the event statistics.
'''This function handles the port statistics from the event statistics.'''
def _handle_portstats_received (event):
    # structure of event.stats is defined by ofp_flow_stats().
    # handler to display flow statistics received in JSON format.
    stats = flow_stats_to_list(event.stats)
    #log.debug("PortStatsReceived from %s: %s",dpidToStr(event.connection.dpid), stats)



def _timer_func ():
    for connection in core.openflow._connections.values():
      connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
      connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
      #log.debug("Sent %i flow/port stats request(s)", len(core.openflow._connections))


class Tutorial (object):
  """                                                                                                                                                            
  A Tutorial object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
"""                                                                                    
  
  def __init__ (self, connection):
    #Keep track of the connection to the switch so that we can send it messages!  
                                                                                                                                        
    self.connection = connection

    # This binds our PacketIn event listener   
                                                                                                                  
    connection.addListeners(self)

    """ Used this table to keep track of which ethernet address is on 
      which switch port (keys are MACs, values are ports)"""  
                                                                                                   
    self.mac_to_port = {}
  

  def send_packet (self, buffer_id, raw_data, out_port, in_port):
 
    msg = of.ofp_packet_out()
    msg.in_port = in_port
    if buffer_id != -1 and buffer_id is not None:
   # We got a buffer ID from the switch; use that                                                                                                              
     msg.buffer_id = buffer_id
    else:
   # No buffer ID from switch -- we got the raw data                                                                                                           
      if raw_data is None:
     # No raw_data specified -- nothing to send!                                                                                                               
        return
      msg.data = raw_data

    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)
    # Send message to switch
    self.connection.send(msg)
    return
  def read_reject_mac(self):
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    f = open(os.path.join(__location__, 'reject_mac.txt'),"r+")
    mac = f.readline().rstrip()
    f.close()
    return mac

  def read_reject_ip(self):
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    f = open(os.path.join(__location__, 'reject_ip.txt'),"r+")
    ip = f.readline().rstrip()
    f.close()
    return ip
    
  def act_like_switch (self, packet, packet_in):

    if packet.type == 0x88cc:
      print "Receiver LLDP ..... "
      return

    if packet.type == 0x0800 and packet.next.protocol == 17 and packet.next.next.dstport == 9999:
      log.debug("RECEIVED UDP over port 9999 packet.next.protocol: %d", packet.next.protocol)
      return

    self.mac_to_port[str(packet.src)] = packet_in.in_port
    #log.debug("Source MAC : %s, Dest MAC : %s, Port : %d, type : %u", str(packet.src), str(packet.dst), packet_in.in_port, packet.type)
    mac = self.read_reject_mac()
    ip =  self.read_reject_ip()

    if packet.type == 2048:
      if packet.next.protocol == 6:
        if packet.next.next.dstport == 80:
          print "Port Blocked"
          return
      ip_new = packet.next.srcip
      if str(ip_new) == ip:
        print "IP blocked"
        return 
    
    
    if str(packet.src) == mac:
       print "MAC Blocked"
       return


    if str(packet.dst) in self.mac_to_port:
      log.debug("Installing Flow")
      msg = of.ofp_flow_mod()
      msg.match = of.ofp_match()
      msg.match.dl_dst = packet.dst
      msg.match.dl_src = packet.src
      msg.match.dl_type = packet.type
      msg.idle_timeout = 0
      msg.hard_timeout = 0


      msg.actions.append(of.ofp_action_output(port = self.mac_to_port[str(packet.dst)]))
      self.connection.send(msg)
      self.send_packet(packet_in.buffer_id, packet_in.data, self.mac_to_port[str(packet.dst)], packet_in.in_port)
    else:
      #self.mac_to_port[str(packet.src)] = packet_in.in_port                                                                                                     
      log.debug("Flooding Message")
      self.send_packet(packet_in.buffer_id, packet_in.data, of.OFPP_FLOOD, packet_in.in_port)

  def _handle_PacketIn (self, event):
    """
Handles packet in messages from the switch.                                                                                                                  
    """

    packet = event.parsed #This is the parsed packet data.                                                                                                      
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.                


    # Comment out the following line and uncomment the one after                                                                                                 
    # when starting the exercise.                                                                                                                                
                                                                                                                      
    self.act_like_switch(packet, packet_in)



def launch ():
  
   
  def start_switch (event):
    # attach handsers to listners
    core.openflow.addListenerByName("FlowStatsReceived",_handle_flowstats_received) 
    core.openflow.addListenerByName("PortStatsReceived",_handle_portstats_received)
    Timer(5, _timer_func, recurring=True)
    #log.debug("Controlling: %s" % (event.connection,))
    Tutorial(event.connection)
    try:
      thread.start_new_thread(log.debug("Thread started"))
      time.sleep(delay)
    except:
      log.debug("Unable to start the thread")
  core.openflow.addListenerByName("ConnectionUp", start_switch)


