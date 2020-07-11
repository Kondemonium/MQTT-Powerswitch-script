# MQTT-Powerswitch-script

Script to communicate with mosquitto broker --> PowerSwitch

# MQTT Testing / Debug

Run mosquitto server with mosquitto -v flag

mosquitto_pub and mosquitto_sub tools : 
```
apt install mosquitto-clients
```

Command channel test : 
```
mosquitto_sub -h localhost -t powerswitch/command -u pwrtest -P passw0rd
mosquitto_pub -h localhost -t powerswitch/command -m "1" -u pwrtest -P passw0rd
mosquitto_pub -h localhost -t powerswitch/command -m "0" -u pwrtest -P passw0rd
```
status channel listener for script output : 
```
mosquitto_sub -h localhost -t powerswitch/switch_status -u pwrtest -P passw0rd
```
UDP Transmission listener with netcat for script UDP transmissions : 
```
netcat -ul 18530
```
run script 
```
python pwr-switch-gw.py 
```

# Building venv for testing @ Ubuntu
```
sudo apt install python3-venv
python3 -m venv pwr-switch
source pwr-switch/bin/activate
pip install paho-mqtt
git clone https://github.com/Kondemonium/MQTT-Powerswitch-script
cd MQTT-Powerswitch-script
python pwr-switch-gw.py 
```
