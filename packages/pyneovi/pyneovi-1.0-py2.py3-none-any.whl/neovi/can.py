# The file is part of the pyneovi project and is provided under the MIT License terms.
# For license information see LICENSE.txt.
"""
.. literalinclude:: ../neovi/can.py
"""

import enum


# Message types
DIAG_CURRENT_DATA          = 0x01
DIAG_FREEZE_FRAME_DATA     = 0x02
DIAG_STORED_DTCS           = 0x03
DIAG_CLEAR_DTCS            = 0x04
DIAG_PENDING_DTCS          = 0x07
DIAG_VEHICLE_INFORMATION   = 0x09
DIAG_PERMANENT_DTCS        = 0x0A

DIAGNOSTIC_SESSION_CONTROL = 0x10
ECU_RESET                  = 0x11
SECURITY_ACCESS            = 0x27
COMMUNICATION_CONTROL      = 0x28
TESTER_PRESENT             = 0x3E
ACCESS_TIMING_PARAMETER    = 0x83
SECURED_DATA_TRANSMISSION  = 0x84
CONTROL_DTC_SETTING        = 0x85
RESPONSE_ON_EVENT          = 0x86
LINK_CONTROL               = 0x87

READ_DATA_BY_ID            = 0x22
READ_MEMORY_BY_ADDRESS     = 0x23
READ_SCALING_DATA_BY_ID    = 0x24
READ_DATA_BY_PERIODIC_ID   = 0x2A
DYNAMICALLY_DEFINE_DATA_ID = 0x2C
WRITE_DATA_BY_ID           = 0x2E
WRITE_MEMORY_BY_ADDRESS    = 0x3D

CLEAR_DIAGNOSTIC_INFORMATION = 0x14
READ_DTC_INFORMATION         = 0x19

IO_CONTROL_BY_ID           = 0x2F

ROUTINE_CONTROL            = 0x31

REQUEST_DOWNLOAD           = 0x34
REQUEST_UPLOAD             = 0x35
TRANSFER_DATA              = 0x36
REQUEST_TRANSFER_EXIT      = 0x37


# DIAG_VEHICLE_INFORMATION PIDs
SUPPORTED_PIDS                 = 0x00
VIN_MESSAGE_COUNT              = 0x01
VIN                            = 0x02
CALIBRATION_ID_COUNT           = 0x03
CALIBRATION_ID                 = 0x04
CALIBRATION_VERIFICATION_COUNT = 0x05
CALIBRATION_VERIFICATION       = 0x06
PERFORMANCE_TRACKING_COUNT_S   = 0x07
PERFORMANCE_TRACKING           = 0x08
ECU_NAME_COUNT                 = 0x09
ECU_NAME                       = 0x0A
PERFORMANCE_TRACKING_COUNT_C   = 0x0B


class SessionType(enum.IntEnum):
    """
    Session types that can be requested with a DIAGNOSTIC_SESSION_CONTROL message.
    """
    Default                = 0x01
    Programming            = 0x02
    ExtendedDiagnostic     = 0x03
    SafetySystemDiagnostic = 0x04


class ControlType(enum.IntEnum):
    """
    Control types that can be used with an ID_CONTROL_BY_ID message.
    """
    ReturnControlToECU  = 0x00
    ResetToDefault      = 0x01
    FreezeCurrentState  = 0x02
    ShortTermAdjustment = 0x03


error_code_lookup = {
    0x10: 'General reject',
    0x11: 'Service not supported',
    0x12: 'Subfunction not supported',
    0x13: 'Invalid message length or format',
    0x14: 'Response too long',
    0x21: 'Busy repeat request',
    0x22: 'System state not correct (is ignition on?)',
    0x24: 'Request sequence error',
    0x25: 'No response from sub-net component',
    0x26: 'Failure prevented execution',
    0x31: 'Bad message format / request out of range',
    0x33: 'Security access denied',
    0x35: 'Invalid key',
    0x36: 'Exceeded number of attempts',
    0x37: 'Required time delay not expired',
    0x70: 'Upload/download not accepted',
    0x71: 'Transfer data suspended',
    0x72: 'General programming failure',
    0x73: 'Wrong Block Sequence Counter',
    0x78: 'Request ok, response pending',
    0x7E: 'Sub-function not supported in active session',
    0x7F: 'Service not supported in active session',
    0x80: 'Not supported in active session',   # Not standard, where did this come from?
}

