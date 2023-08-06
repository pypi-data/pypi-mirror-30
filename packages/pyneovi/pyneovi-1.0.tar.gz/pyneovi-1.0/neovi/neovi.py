# The file is part of the pyneovi project and is provided under the MIT License terms.
# For license information see LICENSE.txt.
"""
This module wraps the low-level interface to the neoVI range of devices. It is
unlikely that the functions defined here will be directly used as
:py:class:`.neodevice.NeoDevice` and related classes offer a more convenient
interface.

Of more interest will be the various constants defined here.

Device type identifiers (used by :py:func:`.neodevice.find_devices`):

======================= ====================== =====================
NEODEVICE_BLUE          NEODEVICE_SW_VCAN      NEODEVICE_FIRE
NEODEVICE_VCAN3         NEODEVICE_YELLOW       NEODEVICE_RED
NEODEVICE_ECU           NEODEVICE_IEVB         NEODEVICE_PENDANT
NEODEVICE_VIRTUAL_NEOVI NEODEVICE_ECUCHIP_UART NEODEVICE_PLASMA_1_11
NEODEVICE_FIRE_VNET     NEODEVICE_NEOANALOG    NEODEVICE_CT_OBD
NEODEVICE_PLASMA_1_12   NEODEVICE_PLASMA_1_13  NEODEVICE_ION_2
NEODEVICE_RADSTAR       NEODEVICE_ION_3        NEODEVICE_VCANFD
NEODEVICE_ECU15         NEODEVICE_ECU25        NEODEVICE_EEVB
NEODEVICE_VCANRF        NEODEVICE_FIRE2        NEODEVICE_FLEX
NEODEVICE_RADGALAXY     NEODEVICE_NEOECUCHIP
======================= ====================== =====================

Additional special identifiers are available:

==================== ================= =============
NEODEVICE_ANY_PLASMA NEODEVICE_ANY_ION NEODEVICE_ALL
==================== ================= =============

Network IDs:

=================================== =================================== ==========================
NETID_DEVICE

NETID_MSCAN                         NETID_SWCAN                         NETID_SWCAN2 
NETID_LSFTCAN                       NETID_LSFTCAN2                      NETID_HSCAN
NETID_HSCAN2                        NETID_HSCAN3                        NETID_HSCAN4
NETID_HSCAN5                        NETID_HSCAN6                        NETID_HSCAN7

NETID_LIN                           NETID_LIN2                          NETID_LIN3
NETID_LIN4                          NETID_LIN5                          NETID_LIN6

NETID_ETHERNET                      NETID_OP_ETHERNET1                  NETID_OP_ETHERNET2
NETID_OP_ETHERNET3                  NETID_OP_ETHERNET4                  NETID_OP_ETHERNET5
NETID_OP_ETHERNET6                  NETID_OP_ETHERNET7                  NETID_OP_ETHERNET8
NETID_OP_ETHERNET9                  NETID_OP_ETHERNET10                 NETID_OP_ETHERNET11
NETID_OP_ETHERNET12                 NETID_ETHERNET_DAQ

NETID_RS232                         NETID_UART                          NETID_UART2
NETID_UART3                         NETID_UART4

NETID_FLEXRAY                       NETID_FLEXRAY1A                     NETID_FLEXRAY1B
NETID_FLEXRAY2                      NETID_FLEXRAY2A                     NETID_FLEXRAY2B

NETID_3G_RESET_STATUS               NETID_3G_FB_STATUS                  NETID_3G_APP_SIGNAL_STATUS
NETID_3G_READ_DATALINK_CM_TX_MSG    NETID_3G_READ_DATALINK_CM_RX_MSG    NETID_3G_LOGGING_OVERFLOW
NETID_3G_READ_SETTINGS_EX

NETID_MOST                          NETID_MOST25                        NETID_MOST50
NETID_MOST150

NETID_FORDSCP                       NETID_J1708                         NETID_AUX
NETID_JVPW                          NETID_ISO                           NETID_ISO2
NETID_ISO3                          NETID_ISO4                          NETID_ISOPIC
NETID_MAIN51                        NETID_RED                           NETID_SCI
NETID_ISO14230                      NETID_RED_APP_ERROR                 NETID_CGI
NETID_DATA_TO_HOST                  NETID_TEXTAPI_TO_HOST               NETID_I2C1
NETID_SPI1                          NETID_RED_VBAT                      NETID_GMFSA
NETID_TCP
=================================== =================================== ==========================
"""


# http://www.intrepidcs.com/support/ICSDocumentation/neoVIDLL/neoVIDLLhelpdoc.html
# https://docs.python.org/2/library/ctypes.html#ctypes.c_int

# Python 2.x compatibility
from __future__ import absolute_import, division, print_function, unicode_literals

from ctypes import *
import platform
import enum

import neovi.structures as structures


apilib = None


# noinspection PyUnusedLocal
def update_result(result, func, args):
    """
    Helper to convert an API call result into an error code.
    :param int result:
    :param func:
    :param tuple args:
    :return: Either SUCCESS or an error code.
    :rtype: int
    """
    if result == 0:
        return GetLastAPIError(args[0])[1]
    else:
        return SUCCESS


def _set_api_hints():
    apilib.icsneoFindNeoDevices.argtypes = [c_int, POINTER(structures.NeoDevice), POINTER(c_int)]
    apilib.icsneoOpenNeoDevice.argtypes = [POINTER(structures.NeoDevice), POINTER(c_int), POINTER(c_ubyte), c_int, c_int]
    apilib.icsneoClosePort.argtypes = [c_int, POINTER(c_int)]
    apilib.icsneoFreeObject.argtypes = [c_int]
    apilib.icsneoFreeObject.restype = None

    apilib.icsneoGetLastAPIError.argtypes = [c_int,  POINTER(c_int)]
    apilib.icsneoGetErrorMessages.argtypes = [c_int, POINTER(c_int), POINTER(c_int)]

    apilib.icsneoGetMessages.argtypes = [c_int, POINTER(structures.icsSpyMessage), POINTER(c_int), POINTER(c_int)]
    apilib.icsneoGetMessages.errcheck = update_result
    apilib.icsneoTxMessages.argtypes = [c_int, POINTER(structures.icsSpyMessage), c_int, c_int]
    apilib.icsneoTxMessages.errcheck = update_result
    apilib.icsneoWaitForRxMessagesWithTimeOut.argtypes = [c_int, c_uint]
    apilib.icsneoGetTimeStampForMsg.argtypes = [c_int, POINTER(structures.icsSpyMessage), POINTER(c_double)]
    apilib.icsneoGetTimeStampForMsg.errcheck = update_result
    apilib.icsneoEnableNetworkRXQueue.argtypes = [c_int, c_int]
    apilib.icsneoEnableNetworkRXQueue.errcheck = update_result
    apilib.icsneoGetISO15765Status.argtypes = [c_int, c_int, c_int, c_int, POINTER(c_int), POINTER(c_int)]
    apilib.icsneoGetISO15765Status.restype = None
    apilib.icsneoSetISO15765RxParameters.argtypes = [c_int, c_int, c_int, POINTER(structures.spyFilterLong), POINTER(structures.icsSpyMessage), c_int, c_int, c_int, c_int]
    apilib.icsneoSetISO15765RxParameters.restype = None

    apilib.icsneoGetConfiguration.argtypes = (c_int, POINTER(c_ubyte), POINTER(c_int))
    apilib.icsneoGetConfiguration.errcheck = update_result
    apilib.icsneoSendConfiguration.argtypes = (c_int, POINTER(c_ubyte), c_int)
    apilib.icsneoSendConfiguration.errcheck = update_result
    apilib.icsneoGetFireSettings.argtypes = (c_int, POINTER(structures.SFireSettings), c_int)
    apilib.icsneoGetFireSettings.errcheck = update_result
    apilib.icsneoSetFireSettings.argtypes = (c_int, POINTER(structures.SFireSettings), c_int, c_int)
    apilib.icsneoSetFireSettings.errcheck = update_result
    apilib.icsneoGetVCAN3Settings.argtypes = (c_int, POINTER(structures.SVCAN3Settings), c_int)
    apilib.icsneoGetVCAN3Settings.errcheck = update_result
    apilib.icsneoSetVCAN3Settings.argtypes = (c_int, POINTER(structures.SVCAN3Settings), c_int, c_int)
    apilib.icsneoSetVCAN3Settings.errcheck = update_result

    apilib.icsneoSetBitRate.argtypes = (c_int,  c_int, c_int)
    apilib.icsneoSetBitRate.errcheck = update_result

    apilib.icsneoGetHWFirmwareInfo.argtypes = (c_int, POINTER(structures.APIFirmwareInfo))
    apilib.icsneoGetDLLFirmwareInfo.argtypes = (c_int, POINTER(structures.APIFirmwareInfo))
    apilib.icsneoForceFirmwareUpdate.argtypes = (c_int,)
    apilib.icsneoForceFirmwareUpdate.restype = None


NEODEVICE_BLUE          = 0x00000001
NEODEVICE_SW_VCAN       = 0x00000002
NEODEVICE_DW_VCAN       = 0x00000004
NEODEVICE_FIRE          = 0x00000008
NEODEVICE_VCAN3         = 0x00000010
NEODEVICE_YELLOW        = 0x00000020
NEODEVICE_RED           = 0x00000040
NEODEVICE_ECU           = 0x00000080
NEODEVICE_IEVB          = 0x00000100
NEODEVICE_PENDANT       = 0x00000200
NEODEVICE_VIRTUAL_NEOVI = 0x00000400
NEODEVICE_ECUCHIP_UART  = 0x00000800
NEODEVICE_PLASMA_1_11   = 0x00001000
NEODEVICE_FIRE_VNET     = 0x00002000
NEODEVICE_NEOANALOG     = 0x00004000
NEODEVICE_CT_OBD        = 0x00008000
NEODEVICE_PLASMA_1_12   = 0x00010000
NEODEVICE_PLASMA_1_13   = 0x00020000
NEODEVICE_ION_2         = 0x00040000
NEODEVICE_RADSTAR       = 0x00080000
NEODEVICE_ION_3         = 0x00100000
NEODEVICE_VCANFD        = 0x00200000
NEODEVICE_ECU15         = 0x00400000
NEODEVICE_ECU25         = 0x00800000
NEODEVICE_EEVB          = 0x01000000
NEODEVICE_VCANRF        = 0x02000000
NEODEVICE_FIRE2         = 0x04000000
NEODEVICE_FLEX          = 0x08000000
NEODEVICE_RADGALAXY     = 0x10000000

NEODEVICE_ANY_PLASMA    = NEODEVICE_PLASMA_1_11 | NEODEVICE_FIRE_VNET | NEODEVICE_PLASMA_1_12 | NEODEVICE_PLASMA_1_13
NEODEVICE_ANY_ION       = NEODEVICE_ION_2 | NEODEVICE_ION_3
NEODEVICE_ALL           = 0xFFFFBFFF

NEODEVICE_NEOECUCHIP    = NEODEVICE_IEVB


# For general error checks (all values >= 0 are defined error codes)
SUCCESS = -1

# For wait_for_rx_messages_with_timeout (all values >= 0 are defined error codes)
NO_MESSAGES = -2
MESSAGES_RECVD = -1


NETID_DEVICE                        = 0
NETID_HSCAN                         = 1
NETID_MSCAN                         = 2
NETID_SWCAN                         = 3
NETID_LSFTCAN                       = 4
NETID_FORDSCP                       = 5
NETID_J1708                         = 6
NETID_AUX                           = 7
NETID_JVPW                          = 8
NETID_ISO                           = 9
NETID_ISOPIC                        = 10
NETID_MAIN51                        = 11
NETID_RED                           = 12
NETID_SCI                           = 13
NETID_ISO2                          = 14
NETID_ISO14230                      = 15
NETID_LIN                           = 16
NETID_OP_ETHERNET1                  = 17
NETID_OP_ETHERNET2                  = 18
NETID_OP_ETHERNET3                  = 19
NETID_ISO3                          = 41
NETID_HSCAN2                        = 42
NETID_HSCAN3                        = 44
NETID_OP_ETHERNET4                  = 45
NETID_OP_ETHERNET5                  = 46
NETID_ISO4                          = 47
NETID_LIN2                          = 48
NETID_LIN3                          = 49
NETID_LIN4                          = 50
NETID_MOST                          = 51
NETID_RED_APP_ERROR                 = 52
NETID_CGI                           = 53
NETID_3G_RESET_STATUS               = 54
NETID_3G_FB_STATUS                  = 55
NETID_3G_APP_SIGNAL_STATUS          = 56
NETID_3G_READ_DATALINK_CM_TX_MSG    = 57
NETID_3G_READ_DATALINK_CM_RX_MSG    = 58
NETID_3G_LOGGING_OVERFLOW           = 59
NETID_3G_READ_SETTINGS_EX           = 60
NETID_HSCAN4                        = 61
NETID_HSCAN5                        = 62
NETID_RS232                         = 63
NETID_UART                          = 64
NETID_UART2                         = 65
NETID_UART3                         = 66
NETID_UART4                         = 67
NETID_SWCAN2                        = 68
NETID_ETHERNET_DAQ                  = 69
NETID_DATA_TO_HOST                  = 70
NETID_TEXTAPI_TO_HOST               = 71
NETID_I2C1                          = 71
NETID_SPI1                          = 72
NETID_OP_ETHERNET6                  = 73
NETID_RED_VBAT                      = 74
NETID_OP_ETHERNET7                  = 75
NETID_OP_ETHERNET8                  = 76
NETID_OP_ETHERNET9                  = 77
NETID_OP_ETHERNET10                 = 78
NETID_OP_ETHERNET11                 = 79
NETID_FLEXRAY1A                     = 80
NETID_FLEXRAY1B                     = 81
NETID_FLEXRAY2A                     = 82
NETID_FLEXRAY2B                     = 83
NETID_LIN5                          = 84
NETID_FLEXRAY                       = 85
NETID_FLEXRAY2                      = 86
NETID_OP_ETHERNET12                 = 87
NETID_MOST25                        = 90
NETID_MOST50                        = 91
NETID_MOST150                       = 92
NETID_ETHERNET                      = 93
NETID_GMFSA                         = 94
NETID_TCP                           = 95
NETID_HSCAN6                        = 96
NETID_HSCAN7                        = 97
NETID_LIN6                          = 98
NETID_LSFTCAN2                      = 99


class BitRate(enum.IntEnum):
    """
    Available bit rates for NeoVI network interfaces.
    """
    BR_20000 = 0
    BR_33333 = 1
    BR_50000 = 2
    BR_62500 = 3
    BR_83333 = 4
    BR_100000 = 5
    BR_125000 = 6
    BR_250000 = 7
    BR_500000 = 8
    BR_800000 = 9
    BR_1000000 = 10


DEFAULT_BIT_RATE = BitRate.BR_500000


def network_name(nid):
    """
    Lookup the friendly name for a network ID.
    :param int nid: The network ID to look up.
    :return: The friendly name for the network.
    :rtype: str
    """
    networks = {
        1: 'HSCAN',
        2: 'MSCAN',
        3: 'SWCAN',
        4: 'LSFTCAN'
    }
    return networks.get(nid, 'Unknown')


def InitializeAPI():
    """
    Initialise the API and prepares it for use. It must be called before any
    other API calls are made.
    
    Note that the underlying neoVI library only requires this on Linux, but
    pyneovi requires it on all platforms. This provides a consistent interface
    without platform-specific checks in application code and also allows
    pyneovi to perform its own initialisation.
    """
    global apilib
    
    if platform.system() == 'Linux':
        apilib = CDLL('libicsneoAPI.so.0.1.3')
    else:
        apilib = windll.icsneo40
    
    _set_api_hints()

    if platform.system() == 'Linux':
        apilib.icsneoInitializeAPI()


def ShutdownAPI():
    """
    Shut down the API and releases any resources allocated during its use.
    
    Note that the underlying neoVI library only requires this on Linux, but
    pyneovi requires it on all platforms. This provides a consistent interface
    without platform-specific checks in application code.
    """
    if platform.system() == 'Linux':
        apilib.icsneoShutdownAPI()
    
    
def GetLastAPIError(hObject):
    """
    Get the error generated by the last API call.
    
    API errors are generated and stored on a 'per-thread' basis. The calling
    thread will only receive errors generated within it's own context. If a new
    API error is generated before the previous error has been retrieved, the
    previous error will be lost. All errors generated can still be retrieved
    using GetErrorMessages. However, GetErrorMessages will return errors
    generated in all threads, not just the current thread.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
        
    :return: A 2-tuple consisting of i) a boolean indicating if a new error was
        generated since the port was opened or GetLastAPIError was last called
        and ii) the error generated by the last API call.
    """
    error_num = c_int()

    result = apilib.icsneoGetLastAPIError(hObject,  byref(error_num))
    return bool(result), error_num.value
        
        
def GetErrorMessages(hObject):
    """
    Read the neoVI DLL error message queue. The error queue will be reset after
    this function is called.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
        
    :return: A 2-tuple consisting of i) a boolean indicating success or failure
        of the function and ii) a list of errors generated by all threads.
    """
    msgs = (c_int * 600)()
    num_errors = c_int()

    result = apilib.icsneoGetErrorMessages(hObject, msgs, byref(num_errors))
    return bool(result), msgs[:num_errors.value]
        
        
def FindNeoDevices(types):
    """
    Find any attached neoVI devices.
    
    :param int types: Filter the results to given types of devices. The
        NEODEVICE_* constants can be OR'd together.
        
    :return: A list of :py:class:`.structures.NeoDevice` objects.
    """
    num_devices = c_int(255)
    devices = (structures.NeoDevice * 255)()

    result = apilib.icsneoFindNeoDevices(types, devices, byref(num_devices))
    
    if result == 0:
        return []

    return devices[:num_devices.value]


def OpenNeoDevice(device, network_ids=None, config_read=True):
    """
    Open a communication link the a neoVI device.
    
    :param structures.NeoDevice device: A device information structure returned
        by :py:func:`.neovi.FindNeoDevices`.
    :param network_ids: An array of network IDs to assign to the available
        networks. The default is to use the predefined network IDs.
    :param bool config_read: Should the device's configuration be read before
        enabling it? It is recommended that this be set to true.
        
    :return: An object handle for use in other API functions or None if the
        call failed.
    """
    handle = c_int()

    result = apilib.icsneoOpenNeoDevice(device, byref(handle), network_ids, c_int(config_read), 0)
    
    if result == 1:
        return handle
    else:
        return None
        

def ClosePort(hObject):
    """
    Close the communication link with the neoVI hardware.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
    
    :return: A 2-tuple containing i) a bool representing the success or failure
        of the function and ii) a list of error codes if the bool is false
        (empty otherwise). See
        `Error Messages <https://cdn.intrepidcs.net/support/neoVIDLL/apiErrorMessages.htm>`_
        in the ICS API documentation.
    """
    num_errors = c_int()
    
    result = apilib.icsneoClosePort(hObject, byref(num_errors))
    if num_errors > 0:
        return bool(result), GetErrorMessages(hObject)[1]
    else:
        return bool(result), []
        
        
def FreeObject(hObject):
    """
    Release any resources that were allocated by OpenNeoDevice.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
    """
    apilib.icsneoFreeObject(hObject)


def GetMessages(hObject):
    """
    Read messages from the neoVI device. The driver object will hold 20,000
    received messages before it will generate an RX buffer overflow error.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
    
    :return: A 3-tuple containing i) either SUCCESS or an error code (see
        `Error Messages <https://cdn.intrepidcs.net/support/neoVIDLL/apiErrorMessages.htm>`_
        in the ICS API documentation), ii) a list of
        :py:class:`.structures.icsSpyMessage` objects, and iii) a list of error
        codes obtained via :py:func:`.neovi.GetErrorMessages`.
    """
    msgs = (structures.icsSpyMessage * 20000)()
    num_msgs = c_int()
    num_errors = c_int()
    
    result = apilib.icsneoGetMessages(hObject, msgs, byref(num_msgs), byref(num_errors))
    
    if num_errors > 0:
        errors = GetErrorMessages(hObject)[1]
    else:
        errors = []
    
    return result, msgs[:num_msgs.value], errors
    

def TxMessages(hObject, msgs, network, num_msgs=1):
    """
    Transmit messages asynchronously to vehicle networks using the neoVI
    hardware.
    
    After the messages has been transmitted there will be a transmit report
    message returned from the device. The transmit report will be read out with
    :py:func:`.neovi.GetMessages`. Any message read which has the
    SPY_STATUS_TX_MSG bit set in the status bitfield is a transmit report. 

    You can also identify a particular transmitted message with DescriptionID
    field. This two byte field (only 14 bits are used) allows the programmer to
    assign an arbitrary number to a message. This number is then returned in
    the transmit report.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
    :param msgs: A list of :py:class:`.structures.icsSpyMessage` objects.
    :param int network: The network to transmit the message on.
    :param int num_msgs: The number of messages to transmit. This should always
        be 1 unless you are transmitting a long Message on ISO or J1708.
    
    :return: Either SUCCESS or an error code (see
        `Error Messages <https://cdn.intrepidcs.net/support/neoVIDLL/apiErrorMessages.htm>`_
        in the ICS API documentation).
    """
    return apilib.icsneoTxMessages(hObject, msgs, network, num_msgs)
    
    
def WaitForRxMessagesWithTimeOut(hObject, timeout_ms):
    """
    Wait a specified amount of time for received messages.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
    :param int timeout_ms: A timeout in ms to wait for a received message
        before returning.
    
    :return: Either MESSAGES_RECVD, NO_MESSAGES, or an error code (see
        `Error Messages <https://cdn.intrepidcs.net/support/neoVIDLL/apiErrorMessages.htm>`_
        in the ICS API documentation).
    """
    result = apilib.icsneoWaitForRxMessagesWithTimeOut(hObject, timeout_ms)
    
    if result == -1:
        return GetLastAPIError(hObject)[1]
    elif result == 0:
        return NO_MESSAGES
    else:
        return MESSAGES_RECVD


def GetTimeStampForMsg(hObject, msg):
    """
    Calculate the timestamp for a message, based on the connected hardware type, and convert it to a usable variable.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
    :param msg: A :py:class:`.structures.icsSpyMessage` object.
    
    :return: A 2-tuple of i) either SUCCESS or an error code (see
        `Error Messages <https://cdn.intrepidcs.net/support/neoVIDLL/apiErrorMessages.htm>`_
        in the ICS API documentation) and ii) the calculated timestamp.
    """
    timestamp = c_double()
    
    result = apilib.icsneoGetTimeStampForMsg(hObject, msg, byref(timestamp))
    
    return result, timestamp.value
    
    
def EnableNetworkRXQueue(hObject, enable):
    """
    Enable or disable the received message queue (and thus reception of
    network traffic). This applies only to the application that called this
    function, other applications are not affected.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
    :param bool enable: Specifies whether to enable (true) or disable (false)
        reception of network traffic.
        
    :return: Either SUCCESS or an error code (see
        `Error Messages <https://cdn.intrepidcs.net/support/neoVIDLL/apiErrorMessages.htm>`_
        in the ICS API documentation).
    """
    return apilib.icsneoEnableNetworkRXQueue(hObject, c_int(enable))
    
    
def GetISO15765Status(hObject, network, clear_rx_status):
    """
    Get, and optionally clear, the current receive status of the CAN ISO15765-2
    network layer.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
    :param int network: Which CAN network the status is requested for.
    :param bool clear_rx_status: If true will clear the receive status and
        reset the receive state machine.
        
    :return: The receive status. See
        `GetISO15765Status <https://cdn.intrepidcs.net/support/neoVIDLL/GetISO15765Status.htm>`_
        in the ICS API documentation.
    """
    reserved = c_int()
    rx_status = c_int()
    
    apilib.icsneoGetISO15765Status(hObject, network, 0, c_int(clear_rx_status), byref(reserved), byref(rx_status))
    return rx_status


def SetISO15765RxParameters(hObject, network, enable, msg_filter, flow_ctx_msg, timeout_ms, flow_control_block_size, uses_extended_addressing):
    """
    set the parameters necessary to control CAN ISO15765-2 network layer message reception.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
    :param int network: The network to transmit the message on.
    :param bool enable: If true ISO15765 services will be enabled for this network.
    
    See
    `SetISO15765RxParameters <https://cdn.intrepidcs.net/support/neoVIDLL/SetISO15765RxParameters.htm>`_
    in the ICS API documentation for full descriptions of the remaining parameters.
    """
    apilib.icsneoSetISO15765RxParameters(hObject, network, c_int(enable), msg_filter, flow_ctx_msg, timeout_ms, flow_control_block_size, uses_extended_addressing, 0)


def GetConfiguration(hObject):
    """
    Read the configuration from a NeoVI Blue or ValueCAN device.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
    
    :return: A 2-tuple of i) either SUCCESS or an error code (see
        `Error Messages <https://cdn.intrepidcs.net/support/neoVIDLL/apiErrorMessages.htm>`_
        in the ICS API documentation) and ii) an array of 1024 configuration
        bytes (see
        `Configuration Array <https://cdn.intrepidcs.net/support/neoVIDLL/ConfigArray.htm>`_
        in the ICS API documentation).
    """
    pData = (c_ubyte * 1024)()
    plNumBytes = c_int()

    result = apilib.icsneoGetConfiguration(hObject, pData, plNumBytes)
    
    return result, pData[:plNumBytes.value]


def SendConfiguration(hObject, pData):
    """
    Send configuration information to a NeoVI Blue or ValueCAN device.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
    :param pData: An array of configuration bytes (see
        `Configuration Array <https://cdn.intrepidcs.net/support/neoVIDLL/ConfigArray.htm>`_
        in the ICS API documentation).
    
    :return: Either SUCCESS or an error code (see
        `Error Messages <https://cdn.intrepidcs.net/support/neoVIDLL/apiErrorMessages.htm>`_
        in the ICS API documentation).
    """
    result = apilib.icsneoSendConfiguration(hObject, pData, sizeof(pData))
    
    return result
    

def GetFireSettings(hObject):
    """
    Read the configuration settings from a neoVI Fire device.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
    
    :return: A 2-tuple of i) either SUCCESS or an error code (see
        `Error Messages <https://cdn.intrepidcs.net/support/neoVIDLL/apiErrorMessages.htm>`_
        in the ICS API documentation) and ii) a
        :py:class:`.structures.SFireSettings` object.
    """
    pSettings = structures.SFireSettings()

    result = apilib.icsneoGetFireSettings(hObject, pSettings, sizeof(pSettings))
    
    return result, pSettings
    

def SetFireSettings(hObject, pSettings, bSaveToEEPROM):
    """
    Write configuration settings to a neoVI Fire device.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
    :param structures.SFireSettings pSettings: The configuration to write.
    :param bool bSaveToEEPROM: Overwrite the stored EEPROM values so that these
        settings persist across power-cycles.
    
    :return: Either SUCCESS or an error code (see
        `Error Messages <https://cdn.intrepidcs.net/support/neoVIDLL/apiErrorMessages.htm>`_
        in the ICS API documentation).
    """
    result = apilib.icsneoSetFireSettings(hObject, pSettings, sizeof(pSettings), c_int(bSaveToEEPROM))
    
    return result


def GetVCAN3Settings(hObject):
    """
    Read the configuration settings from a ValueCAN3 device.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
    
    :return: A 2-tuple of i) either SUCCESS or an error code (see
        `Error Messages <https://cdn.intrepidcs.net/support/neoVIDLL/apiErrorMessages.htm>`_
        in the ICS API documentation) and ii) a
        :py:class:`.structures.SVCAN3Settings` object.
    """
    pSettings = structures.SVCAN3Settings()

    result = apilib.icsneoGetVCAN3Settings(hObject, pSettings, sizeof(pSettings))
    
    return result, pSettings


def SetVCAN3Settings(hObject, pSettings, bSaveToEEPROM):
    """
    Write configuration settings to a ValueCAN3 device.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
    :param structures.SVCAN3Settings pSettings: The configuration to write.
    :param bool bSaveToEEPROM: Overwrite the stored EEPROM values so that these
        settings persist across power-cycles.
    
    :return: Either SUCCESS or an error code (see
        `Error Messages <https://cdn.intrepidcs.net/support/neoVIDLL/apiErrorMessages.htm>`_
        in the ICS API documentation).
    """
    result = apilib.icsneoSetVCAN3Settings(hObject, pSettings, sizeof(pSettings), c_int(bSaveToEEPROM))
    
    return result


def SetBitRate(hObject, iBitRate, iNetworkID):
    """
    Set the bit rates for networks.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
    :param int iBitRate: The new bit rate setting.
    :param int iNetworkID: The network to set the bit rate on.
    
    :return: Either SUCCESS or an error code (see
        `Error Messages <https://cdn.intrepidcs.net/support/neoVIDLL/apiErrorMessages.htm>`_
        in the ICS API documentation).
    """
    result = apilib.icsneoSetBitRate(hObject, iBitRate, iNetworkID)
    
    return result
    
    
def GetHWFirmwareInfo(hObject):
    """
    Return the firmware version of the open neoVI device.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
    
    :return: A 2-tuple of i) either SUCCESS or an error code (see
        `Error Messages <https://cdn.intrepidcs.net/support/neoVIDLL/apiErrorMessages.htm>`_
        in the ICS API documentation) and ii) a
        :py:class:`.structures.APIFirmwareInfo` object.
    """
    pInfo = structures.APIFirmwareInfo()
    result = apilib.icsneoGetHWFirmwareInfo(hObject, pInfo)
    return bool(result), pInfo
    
    
def GetDLLFirmwareInfo(hObject):
    """
    Return the firmware version stored within the DLL API.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
    
    :return: A 2-tuple of i) either SUCCESS or an error code (see
        `Error Messages <https://cdn.intrepidcs.net/support/neoVIDLL/apiErrorMessages.htm>`_
        in the ICS API documentation) and ii) a
        :py:class:`.structures.APIFirmwareInfo` object.
    """
    pInfo = structures.APIFirmwareInfo()
    result = apilib.icsneoGetDLLFirmwareInfo(hObject, pInfo)
    return bool(result), pInfo
    
    
def ForceFirmwareUpdate(hObject):
    """
    Force the firmware on a neoVI device to be updated to the version stored in the DLL API.
    
    :param hObject: An object handle returned by
        :py:func:`.neovi.OpenNeoDevice`.
    """
    apilib.icsneoForceFirmwareUpdate(hObject)
    

def GetDLLVersion():
    """
    Return the software version of the DLL.
    
    :return: The version of the API DLL as an integer.
    :rtype: int
    """
    return apilib.icsneoGetDLLVersion()

