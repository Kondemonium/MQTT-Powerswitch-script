#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import logging
import time
import socket
import binascii


#Logging parameters

# Gets or creates a logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s : %(levelname)s : %(name)s : %(funcName)s : %(message)s')

#Generic Switch-GW parameters
mqttusername = "pwrtest"
mqttpassowrd = "passw0rd"
mqttconnname = "Switch-Gw"
mqttserveraddr = "192.168.1.70"
mqttserverport = 1883
mqttroottopic = "powerswitch/"
updateLoopInterval = 30 #Seconds

#PowerSwitch parameters

PowerSwitchIp = "192.168.1.70"
PowerSwitchPort = 18530
PowerSwitchStatus = ""

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

logging.info("Switch-GW 0.1")
logging.info("Status update interval : {} seconds".format(updateLoopInterval))

# MQTT INIT
mqttclient = mqtt.Client(mqttconnname)

# MQTT LOG
mqttclient.enable_logger(logger=None)
def on_log(client, userdata, level, buf):
    logging.debug("mqttclient log: ".format(buf))
mqttclient.on_log=on_log

#MQTT connection
mqttclient.username_pw_set(mqttusername, mqttpassowrd)
mqttclient.connect(mqttserveraddr, port=mqttserverport, keepalive=60, bind_address="")

def send_udp_command(payload, IP=PowerSwitchIp, PORT=PowerSwitchPort):

    payload_hex = binascii.a2b_hex(payload)
    logging.debug("Encoding payload string {} to hex {} and sending it to {}:{}".format(payload,payload_hex, IP, PORT))
    sock.sendto(payload_hex, (IP, PORT))

def turn_switch(mode):
    global PowerSwitchStatus
    if mode == "OFF":
        logging.info("Sending udp traffic to turn off powerswitch --> {}".format(mode))
        send_udp_command("014498d8630f06b610ee4c4ecbc0a20a0cb84897b58d2ac042")
        PowerSwitchStatus = "OFF"
    if mode == "ON":
        logging.info("Sending udp traffic to turn on powerswitch --> {}".format(mode))
        send_udp_command("014498d8630f06b6100d95f1a1cfa277e2ea4b4964b2824abc")
        PowerSwitchStatus = "ON"


# Publish to MQTT.
def mqttpublish(mqtttopicname, subtopic, message):
    topic = mqtttopicname + subtopic
    mqttclient.publish(topic, message)
    
def on_message(client, userdata, message):
    logging.debug("Got message from CMD channel : {}".format(message.payload.decode("utf-8")))
    received_command = str(message.payload.decode("utf-8")).lstrip()
    logging.debug("message received= {}".format(received_command))
    logging.debug("message topic= {}".format(message.topic))
    logging.debug("message qos= {}".format(message.qos))
    logging.debug("message retain flag= {}".format(message.retain))
    if received_command == "0":
        turn_switch("OFF")
    elif received_command == "1":
        turn_switch("ON")
    else:
        logging.warning("Unknown command from command channel : {}".format(received_command))

## Switch-GW script ---> MQTT broker

def powerswitch_get_status():
    logging.info("Getting status from powerswitch...")
    #HACK REMOVE WHEN STATUS MECHANICS INPLACE
    global PowerSwitchStatus
    return PowerSwitchStatus

def powerswitch_status_update():
    switch_status = powerswitch_get_status()
    mqttpublish(mqttroottopic, "switch_status", switch_status)
    logging.info("Powerswitch return value : {}".format(switch_status))

#Initial status query
powerswitch_status_update()

## MQTT Broker command channel to Switch-GW script

# Subscribe to this  topics, translate mqtt commands into python commands
subscribe_topic = mqttroottopic + "command"
logging.info("Subscribe topic: " + subscribe_topic)
mqttclient.subscribe(subscribe_topic)
mqttclient.on_message = on_message
#Loop to capture MQTT command channel commands
mqttclient.loop_start()
#PowerSwitch status updateloop
while True:
    powerswitch_status_update()
    time.sleep(updateLoopInterval)



