# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

""" Module for AM2315 'poll' type plugin """

import copy
import datetime
import uuid
import logging

import smbus

from foglamp.common import logger
from foglamp.plugins.common import utils
from foglamp.services.south import exceptions


__author__ = "Ashwin Gopalakrishnan, Amarendra K Sinha"
__copyright__ = "Copyright (c) 2018 OSIsoft, LLC"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_DEFAULT_CONFIG = {
    'plugin': {
         'description': 'AM2315 Poll Plugin',
         'type': 'string',
         'default': 'am2315',
         'readonly': 'true'
    },
    'assetName': {
        'description': 'Asset name',
        'type': 'string',
        'default': 'am2315/%M/',
        'order': '1'
    },
    'i2cAddress': {
        'description': 'I2C address in hex',
        'type': 'string',
        'default': '0x5C',
        'order': '2'
    },

    'pollInterval': {
        'description': 'The interval between poll calls to the South device poll routine expressed in milliseconds.',
        'type': 'integer',
        'default': '5000',
        'order': '2',
        'minimum': '1000'
}
}

_LOGGER = logger.setup(__name__, level=logging.INFO)


def plugin_info():
    """ Returns information about the plugin.

    Args:
    Returns:
        dict: plugin information
    Raises:
    """

    return {
        'name': 'AM2315 Poll Plugin',
        'version': '1.0',
        'mode': 'poll',
        'type': 'south',
        'interface': '1.0',
        'config': _DEFAULT_CONFIG
    }


def plugin_init(config):
    """ Initialise the plugin.

    Args:
        config: JSON configuration document for the South device configuration category
    Returns:
        handle: JSON object to be used in future calls to the plugin
    Raises:
    """
    data = copy.deepcopy(config)
    bus = smbus.SMBus(1)
    data['bus'] = bus
    _LOGGER.info('AM2315 initialized')
    return data


def plugin_poll(handle):
    """ Extracts data from the sensor and returns it in a JSON document as a Python dict.

    Available for poll mode only.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
        returns a sensor reading in a JSON document, as a Python dict, if it is available
        None - If no reading is available
    Raises:
        DataRetrievalError
    """
    bus = handle["bus"]
    i2c_address = handle['i2cAddress']['value']

    sensor_add      = hex(int(i2c_address, 16))
    start_add       = 0x00
    function_code   = 0x03
    register_number = 0x04
    response_bytes = 8
    attempt_threshold = 50
    asset_name = '{}'.format(handle['assetName']['value']).replace('%M', i2c_address)

    try:

        try:
            # wake up call
            bus.write_i2c_block_data(sensor_add, function_code, [start_add, register_number])
        except Exception as e:
            # expected exception as sensor is sleeping
            pass
        # request data
        bus.write_i2c_block_data(sensor_add, function_code, [start_add, register_number])
        # read data 
        sensor_response = bytearray(bus.read_i2c_block_data(sensor_add, function_code, response_bytes))
        # temperature
        temperature= (sensor_response[4] * 256 + sensor_response[5])/10
        # humidity
        humidity= (sensor_response[2] * 256 + sensor_response[3])/10
        # crc
        crc = sensor_response[7] * 256 + sensor_response[6]
        # calc crc to verify
        calc_crc = 0xFFFF
        for byte in sensor_response[0:6]:
            calc_crc = calc_crc ^ byte
            for i in range(1,9):
                if(calc_crc & 0x01):
                    calc_crc = calc_crc >> 1
                    calc_crc = calc_crc ^ 0xA001
                else:
                    calc_crc = calc_crc >> 1
        if calc_crc != crc:
            pass
        time_stamp = utils.local_timestamp()
        data = {
            'asset': asset_name,
            'timestamp': time_stamp,
            'key': str(uuid.uuid4()),
            'readings': {
                "temperature": temperature,
                "humidity": humidity
            }
        }
    except (Exception, RuntimeError) as ex:
        _LOGGER.exception("AM2315 exception: {}".format(str(ex)))
        raise exceptions.DataRetrievalError(ex)

    return data


def plugin_reconfigure(handle, new_config):
    """  Reconfigures the plugin

    it should be called when the configuration of the plugin is changed during the operation of the South device service;
    The new configuration category should be passed.

    Args:
        handle: handle returned by the plugin initialisation call
        new_config: JSON object representing the new configuration category for the category
    Returns:
        new_handle: new handle to be used in the future calls
    Raises:
    """
    _LOGGER.info("Old config for AM2315 plugin {} \n new config {}".format(handle, new_config))
    new_handle = copy.deepcopy(new_config)
    new_handle['restart'] = 'no'
    return new_handle


def plugin_shutdown(handle):
    """ Shutdowns the plugin doing required cleanup, to be called prior to the South device service being shut down.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
    Raises:
    """
    _LOGGER.info('AM2315 poll plugin shut down.')
