# BACnet/IP Glossary — Week 2

**BACnet:** A communication protocol for building automation devices (ANSI/ASHRAE 135). Two variants: BACnet/IP (Ethernet, UDP port 47808) and BACnet MS/TP (RS-485 serial).

**Device:** A BACnet-compliant controller, identified on the network by a unique Device Instance number.

**Object:** A single data point within a device (sensor or actuator), identified by Object Type + Instance (e.g. AI:1).

**Who-Is:** A broadcast (or directed) request used to discover BACnet devices on a network.

**I-Am:** The response to a Who-Is, announcing a device's instance number, address, max APDU length, segmentation support, and vendor ID.

**ReadProperty / WriteProperty:** Services used to read or write a value on a BACnet object's property (e.g. PresentValue).

**Directed Who-Is:** A unicast Who-Is sent to a specific IP:port instead of broadcasting — required in network environments (like AWS VPC) where Layer-2 broadcast isn't supported.
