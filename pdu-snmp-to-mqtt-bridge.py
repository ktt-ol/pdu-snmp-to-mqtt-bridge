#!/usr/bin/python
import paho.mqtt.client as mqtt
import dateutil.parser
import datetime
import netsnmp
import time
import sys

# ------------------------
mqttcertfile = "/path/to/ssl/cert.crt"
mqttusername = "username"
mqttpassword = "password"
mqttserver = "mqtt.server"
mqttport = 8883
snmpserver = "pdu.snmp.server"
# ------------------------

outletstate = ""

def mqtt_update(client, session, snmpvars):
    global outletstate
    data = session.get(snmpvars)
    for x in data:
        if x is None:
            print("No SNMP data received! Connection lost?")
            sys.exit(1)
    date = dateutil.parser.parse(data[5])
    timestamp = int(time.mktime(date.timetuple()))

    client.publish("/test/pdu/power", str(int(data[3])*10)) # Watt
    client.publish("/test/pdu/voltage", data[2]) # Volt
    client.publish("/test/pdu/current", str(int(data[1])/10.0)) # Ampere
    client.publish("/test/pdu/energy", str(int(data[4])*100), retain = True) # Watt * hour
    client.publish("/test/pdu/energy_since", str(timestamp), retain = True) # unix timestamp
    client.publish("/test/pdu/bank1/current", str(int(data[6])/10.0)) # Ampere
    client.publish("/test/pdu/bank2/current", str(int(data[7])/10.0)) # Ampere

    if data[0] != outletstate:
        for x in range(1, len(data[0]),4):
            client.publish("/test/pdu/state/outlet-%02d" % ((x-1)/4 + 1), "1" if data[0][x] == "n" else "0", retain = True) # State
        outletstate = data[0]

def on_connect(client, userdata, flags, rc):
    if rc != 0:
        print("Connected with result code "+str(rc))

def on_disconnect(client, userdata, rc):
    print("MQTT disconnected with code "+str(rc))
    sys.exit(1)

# SNMP
session = netsnmp.Session( DestHost=snmpserver, Version=1, Community='public' )
snmpvars = netsnmp.VarList(
    netsnmp.Varbind('PowerNet-MIB::sPDUMasterState.0'),
    netsnmp.Varbind('PowerNet-MIB::rPDU2PhaseStatusCurrent.1'),
    netsnmp.Varbind('PowerNet-MIB::rPDU2PhaseStatusVoltage.1'),
    netsnmp.Varbind('PowerNet-MIB::rPDU2PhaseStatusPower.1'),
    netsnmp.Varbind('PowerNet-MIB::rPDU2DeviceStatusEnergy.1'),
    netsnmp.Varbind('PowerNet-MIB::rPDU2DeviceStatusEnergyStartTime.1'),
    netsnmp.Varbind('PowerNet-MIB::rPDU2BankStatusCurrent.1'),
    netsnmp.Varbind('PowerNet-MIB::rPDU2BankStatusCurrent.2')
)

# MQTT
client = mqtt.Client(client_id="pdu-snmp-to-mqtt-bridge")
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.tls_set(mqttcertfile)
client.username_pw_set(mqttusername, mqttpassword)
client.connect(mqttserver, mqttport, 60)

# Update Loop
client.loop_start()
while True:
    mqtt_update(client, session, snmpvars)
    time.sleep(60)
client.loop_stop()
