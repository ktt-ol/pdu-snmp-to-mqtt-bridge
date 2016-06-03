# pdu-snmp-to-mqtt-bridge
SNMP to MQTT bridge for PDU in our hackspace's serverroom

# Configuration

Open "pdu-snmp-to-mqtt-bridge.py" in editor and configuration
variables for mqtt and snmp server.

# Installation

1. apt-get install python-netsnmp python-dateutil python-stdeb dh-python python-all snmp
2. wget -O /usr/share/snmp/mibs/powernet410.mib "https://raw.githubusercontent.com/b4d/APC/master/powernet410.mib"
3. sed -i "s/^mibs :/# mibs :/g" /etc/snmp/snmp.conf
4. pypi-download paho-mqtt
5. py2dsc paho-mqtt-1.2.tar.gz
6. dpkg -i deb_dist/python-paho-mqtt_1.2-1_all.deb
7. install -m755 pdu-snmp-to-mqtt-bridge.py /usr/local/bin
8. install -m644 pdu-snmp-to-mqtt-bridge.service /etc/systemd/system
9. systemctl enable pdu-snmp-to-mqtt-bridge.service
10. systemctl start pdu-snmp-to-mqtt-bridge.service

