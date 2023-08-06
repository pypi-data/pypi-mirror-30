#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import socket

import paho.mqtt.client as paho

from sibus_lib.utils import safe_get_in_dict

logger = logging.getLogger()

MQTT_HOST = None
MQTT_PORT = None


def set_mqtt_broker(mqtt_host, mqtt_port):
    global MQTT_HOST, MQTT_PORT
    MQTT_HOST = mqtt_host
    MQTT_PORT = mqtt_port


###############################################################################################
###############################################################################################

class BusClient():
    def __init__(self,
                 device_name,
                 service_name,
                 broker=None,
                 port=None,
                 onmessage_cb=None):
        self.device_name = device_name
        self.service_name = service_name
        self.sibus_values = {}

        self.broker_name = None
        self.broker_port = None
        self._callback = onmessage_cb

        self.client = paho.Client("%s:%s" % (self.device_name, self.service_name))
        self.client.on_message = self.on_message
        self.connect(broker, port=port)

    def set_message_callback(self, cb):
        self._callback = cb

    def connect(self, broker=None, port=None):
        if broker is None and self.broker_name is None:
            self.broker_name = MQTT_HOST
        if port is None and self.broker_port is None:
            self.broker_port = MQTT_PORT
        logger.info("Connecting to MQTT broker %s:%d" % (self.broker_name, self.broker_port))
        try:
            self.client.connect(self.broker_name, self.broker_port)
        except socket.error:
            logger.error("  ==> Fail to connect !")
            return False
        logger.info("  ==> Connected !")
        return True

    def reconnect(self):
        logger.info("Reconnecting to broker %s:%d" % (self.broker_name, self.broker_port))
        try:
            self.client.reconnect()
        except socket.error:
            logger.error("  ==> Fail to reconnect !")
            return False
        logger.info("  ==> Reconnected !")

    def disconnect(self):
        logger.info("Disconnecting from broker %s:%d" % (self.broker_name, self.broker_port))
        self.client.disconnect()
        logger.info("  ==> Disconnected !")

    def get_cache_value(self, path_string, safe=None):
        logger.info("Looking for cache value: %s" % path_string)
        path = path_string.strip("/").split("/")
        t = self.sibus_values
        for key in path[1:]:
            t = safe_get_in_dict(key, t)
            if t is None:
                raise Exception(" !!> Value not found for path: %s (near %s)" % (path_string, key))
        logger.info(" ==> Value found: %s" % str(t))
        return t

    def set_cache_value(self, path_string, value):
        logger.info("Setting cache value: %s=%s" % (path_string, str(value)))
        path = path_string.strip("/").split("/")
        t = self.sibus_values
        for key in path[1:-1]:
            st = safe_get_in_dict(key, t)
            if st is None:
                t[key] = {}
                t = t[key]
            else:
                t = st
        t[path[-1]] = value
        pass

    def forge_topic(self, sibus_topic):
        return "sibus/%s/%s/%s" % (self.device_name, self.service_name, sibus_topic)

    def mqtt_sys_subscribe(self):
        # topic = "sibus/+/+/info/%s"%sibus_topic.strip("/") # picus internal stuff: first topic element is the name of the origin !
        logger.info("Listening to MQTT $SYS topic")
        self.client.subscribe(topic="$SYS/#")
        self.start()

    def mqtt_subscribe(self, sibus_topic):
        # topic = "sibus/+/+/info/%s"%sibus_topic.strip("/") # picus internal stuff: first topic element is the name of the origin !
        logger.info("Listening to topic: %s" % sibus_topic)
        self.client.subscribe(topic=sibus_topic)
        self.start()

    def mqtt_publish(self, topic, payload, qos=0, retain=False):
        logger.info("=========== MQTT Publish =============")
        if not topic.startswith("sibus"):
            logger.error("!!!!!!!!!!!!!! Message not sent !!!!!!!!!!!!!!!!!!!!!!!!!")
            logger.error("Invalid topic, does not start with 'sibus/': %s" % topic)
            logger.error("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            return False

        if type(payload) <> dict:
            logger.error("!!!!!!!!!!!!!! Message not sent !!!!!!!!!!!!!!!!!!!!!!!!!")
            logger.error("Message payload must be provided as a dict ! Got '%s', %s" % (str(payload), type(payload)))
            logger.error("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            return False

        """data_dict["sibus_origin"] = {
            "host": socket.getfqdn(),
            "service": self.name
        }"""

        json_s = json.dumps(payload)
        # json_s = str(data_dict)
        # b64data = base64.b64encode(json_s)
        b64data = json_s

        res = self.client.publish(topic=topic,
                                  payload=b64data,
                                  qos=qos,
                                  retain=retain)

        if res.rc == paho.MQTT_ERR_NO_CONN:
            logger.error(
                "MQTT: Message not published, client not connected to %s:%d" % (self.broker_name, self.broker_port))
            logger.error(" * %s = %s" % (topic, json_s))
            return False
        elif res.rc == paho.MQTT_ERR_QUEUE_SIZE:
            logger.error("MQTT: Not published, queue full !")
            logger.error(" * %s = %s" % (topic, json_s))
            return False
        elif res.rc == paho.MQTT_ERR_SUCCESS:
            logger.debug("MQTT: Message published: %s = %s" % (topic, json_s))
            return True
        else:
            return False

    def on_message(self, client, userdata, message):
        logger.info("=========== MQTT on message =============")
        # json_s = base64.b64decode(message.payload)
        json_s = message.payload
        data_dict = json.loads(json_s)

        t = message.topic

        if not t.startswith("sibus"):
            logger.error("!!!!!!!!!!!!!! Message ignored  !!!!!!!!!!!!!!!!!!!!!!!!!")
            logger.error("Message topic does not start by 'sibus'")
            logger.error("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            return False

        logger.debug("Sibus Message received: %s = %s" % (t, data_dict))

        # self.set_cache_value(t, data_dict)

        if self._callback is not None:
            self._callback(topic=t, payload=data_dict)
        return True

    def start(self):
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
