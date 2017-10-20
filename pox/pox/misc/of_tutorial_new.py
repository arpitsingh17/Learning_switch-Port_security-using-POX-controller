#Copyright 2012 James McCauley                                                                                                                                  
#                                                                                                                                                                
# Licensed under the Apache License, Version 2.0 (the "License");                                                                                                
# you may not use this file except in compliance with the License.                                                                                               
# You may obtain a copy . the License at:                                                                                                                       
#                                                                                                                                                                
#     http://www.apache.org/licenses/LICENSE-2.0                                                                                                                 
#                                                                                                                                                                
# Unless required by applicable law or agreed to in writing, software                                                                                            
# distributed under the License is distributed on an "AS IS" BASIS,                                                                                              
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                                                                       
# See the License for the specific language governing permissions and                                                                                            
# limitations under the License.                                                                                                                                 

"""                                                                                                                                                              
This component is for use with the OpenFlow tutorial.                                                                                                            
                                                                                                                                                                 
It acts as a simple hub, but can be modified to act like an L2                                                                                                   
learning switch.                                                                                                                                                 
                                                                                                                                                                 
It's roughly similar to the one Brandon Heller did for NOX.                                                                                                      
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from pox.openflow.of_json import *
from pox.lib.recoco import Timer

log = core.getLogger()

class Tutorial (object):
  """                                                                                                                                                            
  A Tutorial object is created for each switch that connects.                                                                                                    
  A Connection object for that switch is passed to the __init__ function.                                                                                        
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can                                                                                                  
    # send it messages!                                                                                                                                          
    self.connection = connection

    # This binds our PacketIn event listener                                                                                                                     
    connection.addListeners(self)

    # Use this table to keep track of which ethernet address is on  
# which switch port (keys are MACs, values are ports).                                                                                                       
    self.mac_to_port = {}
  def _timer_func ():
    for connection in core.openflow._connections.values():
      connection.send(of.ofp_stats_reques(body=of.ofp_flow_stats_request()))
      connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
      log.debug("Sent %i flow/port stats request(s)", len(core.openflow._connections))

  # handler to display flow statistics received in JSON format
# structure of event.stats is defined by ofp_flow_stats()
  def _handle_flowstats_received (event):
    stats = flow_stats_to_list(event.stats)
    log.debug("FlowStatsReceived from %s: %s",dpidToStr(event.connection.dpid),stats)
    web_bytes = 0
    web_flows = 0
    web_packet = 0
    for f in event.stats:
      if f.match.tp_dst == 80 or f.match.tp_src == 80:
        web_bytes += f.byte_count
        web_packet += f.packet_count
        web_flows += 1
    log.info("Web traffic from %s: %s bytes (%s packets) over %s flows",dpidToStr(event.connection.dpid), web_bytes, web_packet, web_flows)

  def _handle_portstats_received (event):
    stats = flow_stats_to_list(event.stats)
    log.debug("PortStatsReceived from %s: %s",dpidToStr(event.connection.dpid), stats)

  def resend_packet (self, packet_in, out_port):
    """
    Instructs the switch to resend a packet that it had sent to us.
    "packet_in" is the ofp_packet_in object the switch had sent to the
    controller due to a table-miss.
    """
    msg = of.ofp_packet_out()
    msg.data = packet_in

    # Add an action to send to the specified port
    action = of.ofp_action_output(port=out_port)
    
    msg.actions.append(action)

    # Send message to switch
    self.connection.send(msg)

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

  def act_like_hub (self, packet, packet_in):
    """                                                                                                                                                          
    Implement hub-like behavior -- send all packets to all ports besides                                                                                         
    the input port.                                                                                                                                              
    """

    #print "packet: ", packet                                                                                                                                    
    #print "\n"                                                                                                                                                  
    #print "packet_in: ", packet_in                                                                                                                              
    # We want to output to all ports -- we do that using the special                                                                                             
    # OFPP_ALL port as the output port.  (We could have also used                                                                                                
    # OFPP_FLOOD.)                                                                                                                                               
    log.debug("Source Mac :%s, Dest MAC :%s, in_port :%d, type: %u", str(packet.src), str(packet.dst), packet_in.in_port, packet.type)
    self.resend_packet(packet_in, of.OFPP_ALL)

    # Note that if we didn't get a valid buffer_id, a slightly better                                                                                            
    # implementation would check that we got the full data before                                                                                                
    # sending it (len(packet_in.data) should be == packet_in.total_len)).                                                                                        
   
  def read_reject_mac(self):
    f = open("/home/floodlight/pox/pox/misc/reject_mac.txt","r+")
    mac = f.readline()
    f.close()
    return mac

  def act_like_switch (self, packet, packet_in):
    """                                                                                                                                                          
    Implement switch-like behavior.                                                                                                                              
    """
    if packet.type == 0x88cc:
      print "Receiver LLDP ..... "
      return

    if packet.type == 0x0800 and packet.next.protocol == 17 and packet.next.next.dstport == 9999:
      log.debug("RECEIVED UDP over port 9999 packet.next.protocol: %d", packet.next.protocol)
      return

    self.mac_to_port[str(packet.src)] = packet_in.in_port
    log.debug("Source MAC : %s, Dest MAC : %s, Port : %d, type : %u", str(packet.src), str(packet.dst), packet_in.in_port, packet.type)
    

    f = open("/home/floodlight/pox/pox/misc/reject_mac.txt","r+")
    mac = f.readline().rstrip()
    f.close()
    #mac = self.read_reject_mac().rstrip()
    if str(packet.src) == mac:
       print " Block this mac"
       return

    if str(packet.dst) in self.mac_to_port:
      log.debug("Installing flow...")
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
      log.debug("Flooding message...")
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
    # self.act_like_hub(packet, packet_in)                                                                                                                       
    self.act_like_switch(packet, packet_in)



def launch ():
  
  # attach handsers to listners
  core.openflow.addListenerByName("FlowStatsReceived",_handle_flowstats_received) 
  core.openflow.addListenerByName("PortStatsReceived",_handle_portstats_received)
  Timer(5, _timer_func, recurring=True) 
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Tutorial(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)

