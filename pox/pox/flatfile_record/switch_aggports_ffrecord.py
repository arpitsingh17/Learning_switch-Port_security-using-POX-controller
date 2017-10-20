# Copyright 2014 Felipe Estrada-Solano <festradasolano at gmail>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Creates threads and flat files per each OpenFlow switch connected to the
controller in order to get and record (as plain text) the aggregate port stats
with a defined sample time (default is 10 seconds).

The flat file is created as following:

    /[USER HOME]/of-controller-db/pox/switchaggports_[DPID].log

[USER HOME] is the user's home directory. [DPID] is the switch DPID in numeric
format (int).

Copyright 2014 Felipe Estrada-Solano <festradasolano at gmail>

Distributed under the Apache License, Version 2.0
"""
# import required libraries
from pox.core import core
from threading import Thread
import pox.lib.util
import pox.openflow.libopenflow_01 as of
import time
import os

# initialize global variables
log = core.getLogger()
thread_dict = dict()
DIR_NAME = os.path.join("of-controller-db", "pox")
FILE_NAME = "switchaggports"

def get_dir_path ():
    """
    Returns the flat file directory path.
    
    :return: Directory path of flat file
    :rtype: str
    """
    return os.path.join(os.getenv("HOME"), DIR_NAME)

def get_file_path (dpid):
    """
    Returns the flat file path.
    
    :param dpid: Switch DPID in numeric format to identify flat file
    :type dpid: int
    :return: Path of flat file
    :rtype: str
    """
    f_name = FILE_NAME + "_" + str(dpid) + ".log"
    return os.path.join(get_dir_path(), f_name)

class ThreadSwitchAggPortsFFRecord (Thread):
    """
    Thread that correspond to each switch to record aggregate switch port stats
    in a flat file as plain text with a defined sample time. Inherits from
    :mod:`threading.Thread`
    """

    def __init__ (self, dpid):
        """
        Inherits from :mod:`threading.Thread` to create thread and initialize
        attributes.
        
        :param dpid: Switch DPID in numeric format.
        :type dpid: int
        """
        Thread.__init__(self)
        self.dpid = dpid
        self.sampletime = 10
        self.infinite = True

    def run (self):
        """
        Gets and aggregates switch port stats to record them in a flat file as
        plain text with a defined sample time.
        """
        # build and check flat file path
        dir_path = get_dir_path()
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        path = get_file_path(self.dpid)
        # create and/or write file (a = append)
        f = open(path, "a")
        while self.infinite:
            # initialize stats
            rx_packets = 0
            tx_packets = 0
            rx_bytes = 0
            tx_bytes = 0
            rx_drops = 0
            tx_drops = 0
            rx_error = 0
            tx_error = 0
            rx_frame_error = 0
            rx_overrun_error = 0
            rx_crc_error = 0
            collisions = 0
            # build openflow message
            bodyMsg = of.ofp_port_stats_request()
            bodyMsg.port_no = of.OFPP_NONE
            msg = of.ofp_stats_request(body = bodyMsg)
            msg.type = of.OFPST_PORT
            # get and verify stats
            stats = get_switch_stats(self.dpid, msg, "ports")
            if stats == None:
                log.error("Error getting port stats")
                stats = []
            # aggregate ports stats
            for portStats in stats:
                rx_packets += portStats.rx_packets
                tx_packets += portStats.tx_packets
                rx_bytes += portStats.rx_bytes
                tx_bytes += portStats.tx_bytes
                rx_drops += portStats.rx_dropped
                tx_drops += portStats.tx_dropped
                rx_error += portStats.rx_errors
                tx_error += portStats.tx_errors
                rx_frame_error += portStats.rx_frame_err
                rx_overrun_error += portStats.rx_over_err
                rx_crc_error += portStats.rx_crc_err
                collisions += portStats.collisions
            # write in file
            time_ms = int(round(time.time() * 1000))
            f.write("time=" + str(time_ms) + "|rxPackets=" + str(rx_packets)
                    + "|txPackets=" + str(tx_packets) + "|rxBytes="
                    + str(rx_bytes) + "|txBytes=" + str(tx_bytes) + "|rxDrops="
                    + str(rx_drops) + "|txDrops=" + str(tx_drops) + "|rxError="
                    + str(rx_error) + "|txError=" + str(tx_error)
                    + "|rxFrameError=" + str(rx_frame_error)
                    + "|rxOverrunError=" + str(rx_overrun_error)
                    + "|rxCrcError=" + str(rx_crc_error) + "|collisions="
                    + str(collisions) + "|\n")
            f.flush()
            log.debug("Thread is recording aggregate port stats from switch %s" % dpidToStr(self.dpid))
            # sleep sample time seconds
            time.sleep(self.sampletime)
        f.close()

    def set_infinite (self, infinite):
        """
        :param infinite: Handles infinite loop in thread
        :type infinite: bool
        """
        self.infinite = infinite

class switch_aggports_ffrecord (object):
    """
    Waits for OpenFlow switches to connect and create threads to record switch
    aggregate port stats. When connections go down, removes threads.
    """

    def __init__(self):
        """
        References itself as listener.
        """
        core.openflow.addListeners(self)

    def _handle_ConnectionUp (self, event):
        """
        Handles OpenFlow switches connection up to add threads.
        
        :param event: Connection up event
        """
        global thread_dict
        thread = ThreadSwitchAggPortsFFRecord(event.connection.dpid)
        thread_dict[event.connection.dpid] = thread
        thread.start()
        log.info("Added thread to record aggregate port stats from switch %s" % dpidToStr(event.connection.dpid))

    def _handle_ConnectionDown (self, event):
        """
        Handles OpenFlow switches connection down to remove threads.
        
        :param event: Connection down event
        """
        global thread_dict
        thread = thread_dict.pop(event.connection.dpid)
        thread.set_infinite(False)
        log.info("Removed thread to record aggregate port stats from switch %s" % dpidToStr(event.connection.dpid))

# event handler functions
def handle_PortStatsReceived (event):
    """
    Handles port stats event.
    
    :param event: Event received to handle.
    """
    global stats
    stats = event.stats
    log.debug("PortStatsReceived")

# helper functions
def get_switch_stats (dpid, msg, statsType):
    """
    Returns per switch and per type stats.
    
    :param dpid: Switch DPID to request in numeric format
    :type dpid: int
    :param msg: Message to send to the requested switch
    :type msg: str
    :param statsType: Identifies the type of stats requested
    :type statsType: str
    :return: Switch list of requested stats
    :rtype: dict or list
    :except BaseException: If any error occurs returns None
    """
    try:
        # send openflow message
        global stats
        stats = None
        core.openflow.sendToDPID(dpid, msg.pack())
        log.debug("Request switch DPID %s" % dpid)
        # wait for response to return stats
        initialTime = time.time()
        while stats == None:
            if (time.time() - initialTime) > 15:
                log.error("Timeout failure retrieving " + statsType + " stats")
                break
        return stats
    except BaseException, e:
        log.error("Failure retrieving " + statsType + " stats")
        log.error(e.message)
        return None

def dpidToStr (dpid):
    """
    Converts DPID from numeric format to format XX:XX:XX:XX:XX:XX:XX:XX.
    
    :param dpid: DPID in numeric format to convert
    :type dpid: int
    :return: DPID in format XX:XX:XX:XX:XX:XX:XX:XX
    :rtype: str
    """
    dpidStr = pox.lib.util.dpidToStr(dpid)
    dpidStr = dpidStr.replace("-", ":")
    dpidStr = "00:00:" + dpidStr
    return dpidStr

def strToDPID (dpidStr):
    """
    Converts DPID from format XX:XX:XX:XX:XX:XX:XX:XX in numeric format.
    
    :param dpidStr: DPID in format XX:XX:XX:XX:XX:XX:XX:XX to convert
    :type dpidStr: str
    :return: DPID in numeric format
    :rtype: int
    """
    dpidStr = dpidStr[6:]
    dpidStr = dpidStr.replace(":", "-")
    dpid = pox.lib.util.strToDPID(dpidStr)
    return dpid

# launch function
def launch ():
    """
    Runs swith aggregate port stats record.
    """
    core.openflow.addListenerByName("PortStatsReceived", handle_PortStatsReceived)
    # verify and launch module
    module = core.components.get("switch_aggports_ffrecord")
    if module is None:
        core.registerNew(switch_aggports_ffrecord)

