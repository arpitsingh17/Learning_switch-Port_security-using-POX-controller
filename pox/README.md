#POX JSON-REST API

##JSON-REST API

JSON-REST is a web interface that provides some RESTful services to communicate
with the POX controller and its managed resources through HTTP methods over
URL. JSON-REST is based on the micro web-framework Bottle (included as
[pox.lib.bottle](https://github.com/festradasolano/pox/blob/master/pox/lib/bottle.py)).

JSON-REST enables to set web host and port to deploy RESTful services. For
example, to listen any host in port 8082, invoke this:

    $ ./pox.py web.jsonrest --host=0.0.0.0 --port=8082

Some services depend on other modules to correctly perform their tasks. If you
do not launch these modules, these JSON-REST services will return empty or
incorrect data. Following these modules:
 - `pox.openflow.discovery`
 - `pox.host_tracker`
 - `pox.flatfile_record.switch_aggports_ffrecord`

In order to launch JSON-REST along with the aforementioned modules, execute:

    $ ./pox.py openflow.discovery host_tracker flatfile_record.switch_aggports_ffrecord web.jsonrest

Sometimes you may need a forwarding module to enable communication among hosts
and switches from the network. For example, to deploy a layer 2 learning switch
application, do the following:

    $ ./pox.py forwarding.l2_learning web.jsonrest

Full example: run the POX controller to listen OpenFlow messages in port 6633.
The POX controller deploys a layer 2 learning switch application and a RESTful
interface to listen any host in port 8082; all RESTful services should return
correct data. Set logging data to information level. To perform this, invoke as
follows:

    $ ./pox.py log.level --DEBUG openflow.of_01 --port=6633 openflow.discovery host_tracker flatfile_record.switch_aggports_ffrecord forwarding.l2_learning web.jsonrest --host=0.0.0.0 --port=8082

###RESTful web services

Following the implemented RESTful web services to interact with the POX
controller:

 - **URI:** `/web/jsonrest/of/controller/info`. **Method:** GET. 
 **Description:** retrieves information about the controller. Data includes:
  - Listen address (IP and port)
 - **URI:** `/web/jsonrest/discovery/links`. **Method:** GET. **Description:**
 retrieves a list of all inter-switch discovered links (note that these are
 only for switches connected to the controller). Requires to launch
 `pox.openflow.discovery`. Data includes:
  - Data layer source/destination
  - Port source/destination
 - **URI:** `/web/jsonrest/host_tracker/devices`. **Method:** GET.
 **Description:** retrieves a list a list of all hosts tracked by the
 controller. Requires to launch `pox.openflow.discovery` and `pox.host_tracker`.
 Data includes:
  - Data layer address
  - Network addresses
  - Attachment point (switch DPID and port)
  - Last time seen
 - **URI:** `/web/jsonrest/of/switches`. **Method:** GET. **Description:**
 retrieves a list of all switches connected to the controller. Data includes:
  - String DPID in format XX:XX:XX:XX:XX:XX:XX:XX
  - Remote address (IP and port)
  - Connection time
 - **URI:** `/web/jsonrest/of/switch/<switchDpid>/<statType>`. **Method:** GET.
 **Description:** retrieves per switch stats. Arguments are as follows:
  - *switchDpid:* switch DPID in format XX:XX:XX:XX:XX:XX:XX:XX
  - *statType:* aggregate, desc, flows, ports, queues, tables

 Data includes:
  - Aggregate stats:
    - Bytes
    - Flows
    - Packets
  - Description stats:
    - Serial number
    - Manufacturer
    - Hardware
    - Software
    - Datapath
  - Flows stats:
    - Input port
    - Data layer source/destination
    - Network source/destination
    - Transport source/destination
    - Wildcards
    - Bytes
    - Packets
    - Time
    - Idle timeout
    - Hard timeout
    - Cookies
    - Output ports
  - Ports stats:
    - Port number
    - Received/transmitted packets
    - Received/transmitted bytes
    - Received/transmitted dropped packets
    - Received/transmitted packets with error
    - Received packets with frame error
    - Received packets with overrun error
    - Received packets with CRC error
    - Collisions
  - Queues stats:
    - Queue ID
    - Port number
    - Transmitted bytes
    - Transmitted packets
    - Transmitted packets with error
  - Tables stats:
    - Table ID
    - Table name
    - Wildcards
    - Maximum entries
    - Active count
    - Lookup count
    - Matched count
 - **URI:** `/web/jsonrest/of/switch/<switchDpid>/ffrecord/<recordType>/<lastRecords>`.
 **Method:** GET. **Description:** retrieves per switch last recorded stats.
 Requires to launch `pox.flatfile_record.switch_aggports_ffrecord`. Arguments
 are as follows:
  - *switchDpid:* switch DPID in format XX:XX:XX:XX:XX:XX:XX:XX
  - *recordType:* aggports
  - *lastRecords:* number of last records to request

 Data includes:
  - Aggregate ports stats:
    - Received/transmitted packets
    - Received/transmitted bytes
    - Received/transmitted dropped packets
    - Received/transmitted packets with error
    - Received packets with frame error
    - Received packets with overrun error
    - Received packets with CRC error
    - Collisions

The POX JSON-REST API is based on the [POX Controller](https://github.com/noxrepo/pox),
a [NOXRepo.org](http://www.noxrepo.org/) project.

##POX

POX is a networking software platform written in Python.

POX started life as an OpenFlow controller, but can now also function
as an OpenFlow switch, and can be useful for writing networking software
in general.

POX officially requires Python 2.7 (though much of it will work fine
fine with Python 2.6), and should run under Linux, Mac OS, and Windows.
(And just about anywhere else -- we've run it on Android phones,
under FreeBSD, Haiku, and elsewhere.  All you need is Python!)
You can place a pypy distribution alongside pox.py (in a directory
named "pypy"), and POX will run with pypy (this can be a significant
performance boost!).

POX currently communicates with OpenFlow 1.0 switches and includes
special support for the Open vSwitch/Nicira extensions.

###pox.py

pox.py boots up POX. It takes a list of module names on the command line,
locates the modules, calls their launch() function (if it exists), and
then transitions to the "up" state.

Modules are looked for everywhere that Python normally looks, plus the
"pox" and "ext" directories.  Thus, you can do the following:

    $ ./pox.py forwarding.l2_learning

You can pass options to the modules by specifying options after the module
name.  These are passed to the module's launch() funcion.  For example,
to set the address or port of the controller, invoke as follows:

    $ ./pox.py openflow.of_01 --address=10.1.1.1 --port=6634

pox.py also supports a few command line options of its own which should
be given first:

    --verbose      print stack traces for initialization exceptions
    --no-openflow  don't start the openflow module automatically
