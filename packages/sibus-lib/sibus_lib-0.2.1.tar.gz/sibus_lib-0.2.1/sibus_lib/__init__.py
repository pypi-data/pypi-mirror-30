# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Ce module proclame la bonne parole de sieurs Sam et Max. Puissent-t-ils
    retrouver une totale liberté de pensée cosmique vers un nouvel age
    reminiscent.
"""

__version__ = "0.2.1"

from sibus_lib.DefaultLogger import mylogger
from sibus_lib.MessagingCore import BusClient, set_mqtt_broker
from sibus_lib.SmartConfig import SmartConfigFile

def sibus_init(logger_name):
    cfg_data = SmartConfigFile()

    LOG_FOLDER = cfg_data.get(["log", "log_directory", ], "/tmp/sibus")
    logger = mylogger(logger_name=logger_name, log_folder=LOG_FOLDER)

    MQTT_HOST = cfg_data.get(["mqtt_broker", "host", ], "127.0.0.1")
    MQTT_PORT = cfg_data.get(["mqtt_broker", "port", ], 1883)

    logger.info("###### SiBus initialization ###########")
    logger.info("* Config file = " + cfg_data.configfilepath)
    logger.info("* Log folder  = " + LOG_FOLDER)
    logger.info("* MQTT Broker = %s:%d" % (MQTT_HOST, MQTT_PORT))
    logger.info("###### SiBus init done ###########")

    set_mqtt_broker(MQTT_HOST, MQTT_PORT)

    return logger, cfg_data
