# The file is part of the pyneovi project and is provided under the MIT License terms.
# For license information see LICENSE.txt.
"""
This module provides classes representing neoVI devices, all derived from core
functionality in the :py:class:`.NeoDevice` class.

.. Author: John Kemp <kemp@kempj.co.uk>

The following neoVI classes are defined:

.. inheritance-diagram::
      NeoDevice
      NeoFire
      NeoRed
      NeoVCAN3
      NeoBlue
      NeoDWVCAN
      
Below is a simple example that logs all messages to and from a specified ECU.

.. literalinclude:: ../examples/log_all.py
"""


# Python 2.x compatibility
from __future__ import absolute_import, division, print_function, unicode_literals

import threading
from ctypes import sizeof

import neovi.neovi as neovi
import neovi.structures as structures


def init_api():
    """
    Load the neoVI API library and initialise it. This must be called before
    making any API calls.
    """
    neovi.InitializeAPI()
    

def find_devices(types=neovi.NEODEVICE_ALL, auto_open=False):
    """
    find_devices(types=neovi.NEODEVICE_ALL, auto_open=False)

    Find any attached neoVI devices.
    
    :param int types: Filter the results to given types of devices. The
        NEODEVICE_* constants defined in :py:mod:`~neovi.neovi` can be OR'd together.
    :param bool auto_open: Determines whether each device should be
        automatically opened. If this is False then you must call
        :py:meth:`.NeoDevice.open` in order to open a given device.
    """
    return [device_class_lookup[device.DeviceType](device, auto_open) for device in neovi.FindNeoDevices(types)]
    

class OpenFailedError(Exception):
    """
    Failed to open a NeoVI device.
    """
    pass


class InvalidConfigurationError(Exception):
    """
    An invalid configuration was supplied to be written to the device.
    """
    pass


class NeoDevice:
    """
    Represents a generic neoVI device, providing an interface for transmitting
    and receiving messages as well as configuring the device.
    
    :param structures.NeoDevice device: Device identifier, as returned by
        :py:func:`.neovi.FindNeoDevices` for example. See also
        :py:func:`.find_devices` which returns a list of pre-constructed
        NeoDevice objects.
    :param bool auto_open: Determines whether the device should be
        automatically opened. If this is False then you must call
        :py:meth:`.NeoDevice.open` in order to open the device.
    :param bool launch_msg_queue_thread: Determines whether to start a
        thread to receive incoming messages. If this is False then you must
        process the message queue via the
        :py:meth:`.NeoDevice._process_msg_queue` method or fetch the
        messages via the :py:meth:`.NeoDevice.get_messages` method.
    """
    def __init__(self, device, auto_open=False, launch_msg_queue_thread=True):
        self._device = device
        self._handle = None
        self._tx_id = 1
        self._subscriptions = []
        self._subscriptions_all = []
        self._msg_queue_thread = None
        self._pump_messages = False
        self._subscriptions_lock = threading.Lock()
        self._subscriptions_all_lock = threading.Lock()
        
        if auto_open:
            self.open(launch_msg_queue_thread)
            
    def open(self, launch_msg_queue_thread=True):
        """
        Open the device and optionally launch the message thread. This is only
        required if the object was constructed with auto_open = False.
        
        :param bool launch_msg_queue_thread: Determines whether to start a
            thread to receive incoming messages. If this is False then you must
            process the message queue via the
            :py:meth:`.NeoDevice._process_msg_queue` method or fetch the
            messages via the :py:meth:`.NeoDevice.get_messages` method.
        
        :raises OpenFailedError: If the device cannot be opened.
        """
        self._handle = neovi.OpenNeoDevice(self._device)
        if self._handle is None:
            raise OpenFailedError
        if launch_msg_queue_thread:
            self._start_msg_queue_thread()
    
    def get_type(self):
        """
        :return: The type of device represented. See NEODEVICE_* in
            :py:mod:`~neovi.neovi`.
        """
        return self._device.DeviceType
    
    def get_settings(self):
        """
        Get the current device configuration.
        :return:
        """
        raise NotImplementedError
        
    def set_settings(self, settings, save_to_eeprom=False):
        """
        Set the device configuration.
        :param settings: A device-specific configuration.
        :param save_to_eeprom: Determines if the configuration will be persisted across device power cycles.
        :return:
        """
        raise NotImplementedError
        
    def tx_raw_message(self, msg, network_id):
        """
        Transmits a pre-constructed message.
        
        :param icsSpyMessage msg: The message to transmit.
        :param int network_id: The network to transmit on. See NETID_* in
            :py:mod:`~neovi.neovi`.
        
        :return: Status code. :py:data:`.neovi.SUCCESS` or an error code. See
            `TxMessages <https://cdn.intrepidcs.net/support/neoVIDLL/TxMessages.htm>`_
            in the ICS API documentation
            for possible codes (constants not yet defined within pyneovi).
        """
        return neovi.TxMessages(self._handle, msg, network_id)
    
    def tx_message(self, network_id, dest, msg_type, payload):
        """
        Transmits a pre-constructed message.
        
        :param int network_id: The network to transmit on. See NETID_* in
            :py:mod:`~neovi.neovi`.
        :param int dest: The address of the destination ECU.
        :param int msg_type: The message type to send. See :py:mod:`.can`.
        :param payload: Up to 6 bytes to send.
        :type payload: list of ints
        
        :return: Tuple of status code and transmission id. Status code is
            :py:data:`.neovi.SUCCESS` or an error code. See
            `TxMessages <https://cdn.intrepidcs.net/support/neoVIDLL/TxMessages.htm>`_
            in the ICS API documentation
            for possible codes (constants not yet defined within pyneovi).
            Transmission id can be safely ignored.
        """
        msg = structures.icsSpyMessage()
        msg.ArbIDOrHeader = dest
        msg.NumberBytesData = 8
        for i in range(8):
            msg.Data[i] = 0
        msg.Data[0] = len(payload) + 1
        msg.Data[1] = msg_type
        for i in range(len(payload)):
            msg.Data[i + 2] = payload[i]
        msg.StatusBitField = 0
        msg.StatusBitField2 = 0
        msg.DescriptionID = self._tx_id
        self._tx_id += 1
        return self.tx_raw_message(msg, network_id), self._tx_id - 1
        
    def subscribe_to(self, callback, network=None, address=None, msg_type=None, additional_bytes=None, auto_remove=False, user_data=None):
        """
        Set a callback function to be called upon reception of a defined subset
        of messages. Note that this will only occur if the message thread has
        been started or if :py:meth:`.NeoDevice._process_msg_queue` is called
        manually. All parameters other than callback, auto_remove, and user_data
        define filtering criteria that will be used to determine whether to
        pass the message to this callback.
        
        :param func callback: The method or function to be called. This must
            take two parameters: 1) a message as a
            :py:class:`.structures.icsSpyMessage` object, and 2) a user data
            parameter with no pre-defined meaning within pyneovi.
        :param int network: The network ID of interest (see NETID_* in
            :py:mod:`~neovi.neovi`). If None (the default) then it will be
            ignored for filtering.
        :param int address: The address of the ECU of interest. If None (the
            default) then it will be ignored for filtering.
        :param int msg_type: The message type of interest (see :py:mod:`.can`).
            If None (the default) then it will be ignored for filtering.
        :param additional_bytes: Additional payload bytes to use for filtering.
            May be an empty list. A value of None (the default) will be converted
            to an empty list automatically.
        :type additional_bytes: list of ints
        :param bool auto_remove: If True then the subscription is removed once
            the first message matching the provided criteria has been received.
        :param user_data: This parameter has no pre-defined meaning within
            pyneovi - the value is passed to the callback function along with
            the received message.
        """
        self._subscriptions_lock.acquire()
        self._subscriptions.append((callback, network, address, msg_type, [] if additional_bytes is None else additional_bytes, auto_remove, user_data))
        self._subscriptions_lock.release()
    
    def subscribe_to_all(self, callback):
        """
        Set a callback function to be called upon reception of any message. Note
        that this will only occur if the message thread has been started or if
        :py:meth:`.NeoDevice._process_msg_queue` is called manually.
        
        :param func callback: The method or function to be called. This must
            take three parameters: 1) a statue code of either
            :py:data:`.neovi.SUCCESS` or an error code (see
            `TxMessages <https://cdn.intrepidcs.net/support/neoVIDLL/TxMessages.htm>`_
            in the ICS API documentation
            for possible codes (constants not yet defined within pyneovi)), 2)
            a list of messages as :py:class:`.structures.icsSpyMessage` objects,
            and 3) a list of errors as integers (see
            `Error Messages <https://cdn.intrepidcs.net/support/neoVIDLL/apiErrorMessages.htm>`_
            in the ICS API documentation
            for a complete error list).
        """
        self._subscriptions_all_lock.acquire()
        self._subscriptions_all.append(callback)
        self._subscriptions_all_lock.release()
    
    def get_messages(self):
        """
        Fetch pending received messages. Note that if the message thread was
        launched then this should not be called.
        
        :returns: A tuple containing 1) a statue code of either
            :py:data:`.neovi.SUCCESS` or an error code (see
            `TxMessages <https://cdn.intrepidcs.net/support/neoVIDLL/TxMessages.htm>`_
            in the ICS API documentation
            for possible codes (constants not yet defined within pyneovi)), 2)
            a list of messages as :py:class:`.structures.icsSpyMessage` objects,
            and 3) a list of errors as integers (see
            `Error Messages <https://cdn.intrepidcs.net/support/neoVIDLL/apiErrorMessages.htm>`_
            in the ICS API documentation
            for a complete error list).
        """
        return neovi.GetMessages(self._handle)
    
    def setup_networks(self, network_settings):
        # We don't know how to handle anything other than the Fire right now.
        # Also, this should probably move into the subclasses.
        if self.get_type() != neovi.NEODEVICE_FIRE:
            return
        
        settings = self.get_settings()
        
        if neovi.NETID_HSCAN in network_settings:
            settings.can1.Mode = 0
            settings.can1.SetBaudrate = 0
            settings.can1.Baudrate = network_settings[neovi.NETID_HSCAN]['bitrate']
        else:
            settings.can1.Mode = 1
        
        if neovi.NETID_MSCAN in network_settings:
            settings.can2.Mode = 0
            settings.can2.SetBaudrate = 0
            settings.can2.Baudrate = network_settings[neovi.NETID_MSCAN]['bitrate']
        else:
            settings.can2.Mode = 1
        
        self.set_settings(settings)
    
    def get_firmware_version(self):
        result, info = neovi.GetHWFirmwareInfo(self._handle)
        return info if result else None

    def get_dll_firmware_version(self):
        result, info = neovi.GetDLLFirmwareInfo(self._handle)
        return info if result else None

    def force_firmware_update(self):
        neovi.ForceFirmwareUpdate(self._handle)

    def close(self):
        """
        Close the device and shutdown the message thread (if there is one).
        """
        self._pump_messages = False
        if self._msg_queue_thread is not None:
            self._msg_queue_thread.join()

        if self._handle is not None:
            neovi.ClosePort(self._handle)
            neovi.FreeObject(self._handle)
            self._handle = None

    def _process_msg_queue(self):
        result, msgs, errors = self.get_messages()

        self._subscriptions_all_lock.acquire()
        for callback in self._subscriptions_all:
            callback(result, msgs, errors)
        self._subscriptions_all_lock.release()

        self._subscriptions_lock.acquire()
        for msg in msgs:
            for i in range(len(self._subscriptions) - 1, -1, -1):
                callback, network, address, msg_type, additional_bytes, auto_remove, user_data = self._subscriptions[i]
                if ((network is None or network == msg.NetworkID) and
                        (address is None or address == msg.ArbIDOrHeader) and
                        (msg_type is None or msg_type == msg.Data[1]) and
                        (additional_bytes is None or structures.array_equal(additional_bytes, msg.Data[2:2 + len(additional_bytes)]))):
                    callback(msg, user_data)
                    if auto_remove:
                        del self._subscriptions[i]
        self._subscriptions_lock.release()

    def _start_msg_queue_thread(self):
        self._pump_messages = True
        self._msg_queue_thread = threading.Thread(target=self._msg_queue_thread_func)
        self._msg_queue_thread.start()

    def _msg_queue_thread_func(self):
        while self._pump_messages:
            self._process_msg_queue()
    
    def __del__(self):
        self.close()
            

class NeoFire(NeoDevice):
    """
    Represents a neoVI Fire device. Should be used if settings specific to the
    neoVI Fire must be read/written.
    """
    def __init__(self, device, auto_open=True, launch_msg_queue_thread=True):
        NeoDevice.__init__(self, device, auto_open, launch_msg_queue_thread)
       
    def get_settings(self):
        return neovi.GetFireSettings(self._handle)
    
    def set_settings(self, settings, save_to_eeprom=False):
        return neovi.SetFireSettings(self._handle, settings, save_to_eeprom)


class NeoRed(NeoFire):
    """
    Represents a neoVI Red device. Should be used if settings specific to the
    neoVI Red must be read/written.
    """
    pass


class NeoVCAN3(NeoDevice):
    """
    Represents a ValueCAN3 device. Should be used if settings specific to the
    ValueCAN3 must be read/written.
    """
    def __init__(self, device, auto_open=True, launch_msg_queue_thread=True):
        NeoDevice.__init__(self, device, auto_open, launch_msg_queue_thread)
       
    def get_settings(self):
        return neovi.GetVCAN3Settings(self._handle)
    
    def set_settings(self, settings, save_to_eeprom=False):
        return neovi.SetVCAN3Settings(self._handle, settings, save_to_eeprom)
        
        
class NeoBlue(NeoDevice):
    """
    Represents a neoVI Blue device. Should be used if settings specific to the
    neoVI Blue must be read/written.
    """
    def __init__(self, device, auto_open=True, launch_msg_queue_thread=True):
        NeoDevice.__init__(self, device, auto_open, launch_msg_queue_thread)
    
    def set_settings(self, settings, save_to_eeprom=False):
        if sizeof(settings) != 1024:
            raise InvalidConfigurationError
        return neovi.SendConfiguration(self._handle, settings)


class NeoDWVCAN(NeoBlue):
    pass


# noinspection PyPep8
device_class_lookup = {
    neovi.NEODEVICE_FIRE    : NeoFire,
    neovi.NEODEVICE_RED     : NeoRed,
    neovi.NEODEVICE_VCAN3   : NeoVCAN3,
    neovi.NEODEVICE_BLUE    : NeoBlue,
    neovi.NEODEVICE_DW_VCAN : NeoDWVCAN
}

