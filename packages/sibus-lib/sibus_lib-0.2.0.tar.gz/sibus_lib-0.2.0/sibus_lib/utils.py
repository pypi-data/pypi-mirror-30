#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime as dt
import logging
import random
import signal
import subprocess
import sys

logger = logging.getLogger()


def nice_float(value, very_nice=False):
    if very_nice:
        return float("%.2f" % float(value))
    else:
        return float("%.6f" % float(value))

def parse_num(s):
    try:
        return int(s)
    except ValueError:
        try:
            return nice_float(s)
        except ValueError:
            return s

def datetime_now():
    return dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")


def datetime_now_float():
    return datetime_to_float(dt.datetime.now())

def random_value(value, percent_range=30):
    t = (random.random() - 0.5)*(percent_range/100.0)
    return value * (1+t)

def datetime_to_float(d):
    epoch = dt.datetime.utcfromtimestamp(0)
    total_seconds =  (d - epoch).total_seconds()
    # total_seconds will be in decimals (millisecond precision)
    return total_seconds

def float_to_datetime(fl):
    return dt.datetime.fromtimestamp(fl)


def safe_get_in_dict(key, ddict, safe=None):
    if key not in ddict:
        return safe
    return ddict[key]


def sigterm_handler(_signo, _stack_frame):
    # Raises SystemExit(0):
    if _signo <> 0:
        logger.error("Progam exited with error (status=%d)" % _signo)
        logger.error(str(_stack_frame))
    else:
        logger.info("Progam exited correctly (status=%d)" % _signo)
    sys.exit(_signo)


def handle_signals():
    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGINT, sigterm_handler)

def sibus_install():
    import os, shutil
    from pkg_resources import resource_filename, resource_exists
    from sibus_lib.SmartConfig import SmartConfigFile

    print "installing SiBus Library..."

    sibus_config = resource_filename("sibus_lib", "resources/sibus.yml")
    config_dst_dir = os.path.join(os.path.expanduser("~"), ".sibus")
    config_dst = os.path.join(config_dst_dir, "sibus.yml")

    if not resource_exists("sibus_lib", "resources/sibus.yml"):
        raise Exception("Config file not found ! " + sibus_config)

    if not os.path.isdir(config_dst_dir):
        os.makedirs(config_dst_dir)

    if not os.path.isfile(config_dst):
        print "Copying config file in " + config_dst
        shutil.copy(sibus_config, config_dst)
    else:
        print "Config file " + config_dst + " already exists"

    cfg_data = SmartConfigFile(config_dst)

    db_host = cfg_data.get(["sql_database", "host", ], "127.0.0.1")
    db_port = cfg_data.get(["sql_database", "port", ], 3306)
    db_login = cfg_data.get(["sql_database", "login", ], None)
    db_password = cfg_data.get(["sql_database", "password", ], None)
    db_database = cfg_data.get(["sql_database", "database", ], "sibus_database")

    from sqlalchemy import create_engine
    from sqlalchemy_utils import database_exists, create_database

    if db_login is not None and db_password is not None:
        _sql_url = "mysql+pymysql://%s:%s@%s:%d/%s" % (db_login, db_password, db_host, db_port, db_database)
    else:
        _sql_url = "mysql+pymysql://%s:%d/%s" % (db_host, db_port, db_database)

    engine = create_engine(_sql_url)
    if not database_exists(engine.url):
        print "Creating SQL database with " + _sql_url
        create_database(engine.url)
    else:
        print "SQL database " + _sql_url + " already exists"

    print "Installation complete !"


def exec_process(cmd_line):
    logger.info("## Launching command '%s'" % str(cmd_line))
    p = subprocess.Popen(cmd_line, stderr=subprocess.PIPE, shell=True)
    rc = p.poll()
    while rc is None:
        output = p.stderr.readline()
        if output != "":
            logger.debug(output.strip())
        rc = p.poll()
    if (rc != 0):
        raise Exception("  !! ERROR: Process exits with code: %d" % rc)
    else:
        logger.info(" == Command '%s' executed correctly" % str(cmd_line))
        return rc
