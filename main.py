#EHEHEHEHEHE
import ujson
from umqttsimple import MQTTClient
import socket
import ussl
import gc
import sogit

print("a")
relay = Pin(14, Pin.OUT)
fet = Pin(16, Pin.OUT)

data = { "id": 0,
         "status": 0
}

try:
    with open('config.json', 'r') as f:
        content = f.read()
        config = ujson.loads(content)
        print("Config file loaded!")
except Exception as ex:
    print("No config file! Creating...")
    try:
        with open('config.json', 'w') as f:
            f.write(ujson.dumps(config))
            print("Config file created!")
    except Exception as ex:
        print("Can't create config file!")

def message(topic, msg):
    try:
        param = ujson.loads(msg)
        if(param["id"] != 0):
            print(topic, msg)
            if("reset" in param):
                print("Reset machine...")
                machine.reset()
            if("update" in param):
                print("Updating..")
                client.publish("device/test", "{\"id\":0, \"msg:\":\"OTA update starting...\"}")
                sogit.ota_update()
                client.publish("device/test", "{\"id\":0, \"msg:\":\"OTA update complete! Restarting...\"}")
                machine.reset()
                print("Update complete! Restart...")
            if("door" in param):
                if(param["door"] == 1):
                    print("Opening door...")
                    relay.value(1)
                    time.sleep(config["relay_delay"])
                    fet.value(1)
                    time.sleep(config["fet_close_delay"])
                    fet.value(0)
                    relay.value(0)
                    print("Door is now open!")
                    data["status"] = 1;
                    client.publish("device/esp8266", ujson.dumps(data))
                else:
                    print("Closing door...")
                    time.sleep(0.2)
                    fet.value(1)
                    time.sleep(config["fet_open_delay"])
                    fet.value(0)
                    print("Door closed!")
                    data["status"] = 0;
                    client.publish("device/esp8266", ujson.dumps(data))
    except:
        pass

client = None

def connect_mqtt():
    global client, client_id, mqtt_server
    
    if station.isconnected() == False:
        station.connect(ssid, password)
    if station.isconnected():
        client = MQTTClient(client_id, mqtt_server, port=1883, user=None, password=None, keepalive=60, ssl=False, ssl_params={})
        client.set_callback(message)
        client.connect()
        client.subscribe("device/test")
        print('Connected to %s MQTT broker' % (mqtt_server))

def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    client = connect_mqtt()
    time.sleep(5)
    #machine.reset()

try:
    connect_mqtt()
except OSError as e:
    restart_and_reconnect()

while True:
    try:
        client.check_msg()
        if (time.time() - last_message) > message_interval:
            client.publish("device/esp8266", ujson.dumps(data))
            last_message = time.time()
    except Exception as ex:
        print("MQTT error:", ex)
        restart_and_reconnect()

