# The file is part of the pyneovi project and is provided under the MIT License terms.
# For license information see LICENSE.txt.
"""
Classes provided by this module:
 * :class:`NeoDevice`
 * :class:`icsSpyMessage`
 * :class:`spyFilterLong`
 * :class:`CAN_SETTINGS`
 * :class:`SWCAN_SETTINGS`
 * :class:`LIN_SETTINGS`
 * :class:`ISO9141_KEYWORD2000__INIT_STEP`
 * :class:`ISO9141_KEYWORD2000_SETTINGS`
 * :class:`UART_SETTINGS`
 * :class:`STextAPISettings`
 * :class:`SFireSettings`
 * :class:`SVCAN3Settings`

.. Author: John Kemp <kemp@kempj.co.uk>
"""


from ctypes import *


def array_equal(a1, a2):
    if len(a1) != len(a2):
        print("Mismatched array sizes!")
        return False
    for i1, i2 in zip(a1, a2):
        if i1 != i2:
            return False
    return True


def format_array(array):
    return '%X %X %X %X %X %X %X %X' % (array[0], array[1], array[2], array[3], array[4], array[5], array[6], array[7])
    

def get_status_bits_set(msg):
    values = [
        (0x01, 'GLOBAL_ERR'),
        (0x02, 'TX_MSG'),
        (0x04, 'XTD_FRAME'),
        (0x08, 'REMOTE_FRAME'),
        (0x10, 'CRC_ERROR'),
        (0x20, 'CAN_ERROR_PASSIVE'),
        (0x40, 'INCOMPLETE_FRAME'),
        (0x80, 'LOST_ARBITRATION'),
        (0x100, 'UNDEFINED_ERROR'),
        (0x200, 'CAN_BUS_OFF'),
        (0x400, 'CAN_ERROR_WARNING'),
        (0x800, 'BUS_SHORTED_PLUS'),
        (0x1000, 'BUS_SHORTED_GND'),
        (0x2000, 'CHECKSUM_ERROR'),
        (0x4000, 'BAD_MESSAGE_BIT_TIME_ERROR'),
        (0x8000, 'IFR_DATA'),
        (0x10000, 'HARDWARE_COMM_ERROR'),
        (0x20000, 'EXPECTED_LEN_ERROR'),
        (0x40000, 'INCOMING_NO_MATCH'),
        (0x80000, 'BREAK'),
        (0x100000, 'AVSI_REC_OVERFLOW'),
        (0x200000, 'TEST_TRIGGER'),
        (0X400000, 'AUDIO_COMMENT'),
        (0x800000, 'GPS_DATA'),
        (0x1000000, 'ANALOG_DIGITAL_INPUT'),
        (0x2000000, 'TEXT_COMMENT'),
        (0x4000000, 'NETWORK_MESSAGE_TYPE'),
        (0x8000000, 'VSI_TX_UNDERRUN'),
        (0x10000000, 'VSI_IFR_CRC_Bit'),
        (0x20000000, 'INIT_MESSAGE'),
        (0x40000000, 'HIGH_SPEED_MESSAGE')
    ]
    
    values2 = [
        (0x01, 'HAS_VALUE'),
        (0x02, 'VALUE_IS_BOOLEAN'),
        (0x04, 'HIGH_VOLTAGE'),
        (0x08, 'LONG_MESSAGE')
    ]
    
    bits_set = []
    bits_set2 = []
    
    for v in values:
        if msg.StatusBitField & v[0] == v[0]:
            bits_set.append(v[1])
    
    for v in values2:
        if msg.StatusBitField2 & v[0] == v[0]:
            bits_set2.append(v[1])
    
    return bits_set, bits_set2


class NeoDevice(Structure):
    _fields_ = [('DeviceType',        c_ulong),
                ('Handle',            c_int),
                ('NumberOfClients',   c_int),
                ('SerialNumber',      c_int),
                ('MaxAllowedClients', c_int)]
                

class icsSpyMessage(Structure):
    _fields_ = [('StatusBitField',      c_ulong),
                ('StatusBitField2',     c_ulong),
                ('TimeHardware',        c_ulong),
                ('TimeHardware2',       c_ulong),
                ('TimeSystem',          c_ulong),
                ('TimeSystem2',         c_ulong),
                ('TimeStampHardwareID', c_ubyte),
                ('TimeStampSystemID',   c_ubyte),
                ('NetworkID',           c_ubyte),
                ('NodeID',              c_ubyte),
                ('Protocol',            c_ubyte),
                ('MessagePieceID',      c_ubyte),
                ('ColorID',             c_ubyte),
                ('NumberBytesHeader',   c_ubyte),
                ('NumberBytesData',     c_ubyte),
                ('DescriptionID',       c_short),
                ('ArbIDOrHeader',       c_long),
                ('Data',                c_ubyte * 8),
                ('AckBytes',            c_ubyte * 8),
                ('Value',               c_float),
                ('MiscData',            c_ubyte)]
    
    def __repr__(self):
        fields = ['StatusBitField', 'StatusBitField2', 'NodeID', 'DescriptionID', 'ArbIDOrHeader', 'Value']
        field_values = ['%s=%s' % (k, v) for k, v in [(row, getattr(self, row)) for row in fields]]
        data_values = ['%s=(%X %X %X %X %X %X %X %X)' % (k, v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7]) for k, v in [(row, getattr(self, row)) for row in ['Data', 'AckBytes']]]
        return 'icsSpyMessage(%s)' % ', '.join(field_values + data_values)
                

class spyFilterLong(Structure):
    _fields_ = [('StatusValue',          c_ulong),
                ('StatusMask',           c_ulong),
                ('Status2Value',         c_ulong),
                ('Status2Mask',          c_ulong),
                ('Header',               c_ulong),
                ('HeaderMask',           c_ulong),
                ('MiscData',             c_ulong),
                ('MiscDataMask',         c_ulong),
                ('ByteDataMSB',          c_ulong),
                ('ByteDataLSB',          c_ulong),
                ('ByteDataMaskMSB',      c_ulong),
                ('ByteDataMaskLSB',      c_ulong),
                ('HeaderLength',         c_ulong),
                ('ByteDataLength',       c_ulong),
                ('NetworkID',            c_ulong),
                ('FrameMaster',          c_ushort),
                ('bUseArbIdRangeFilter', c_ubyte),
                ('bStuff2',              c_ubyte),
                ('ExpectedLength',       c_ulong),
                ('NodeID',               c_ulong)]
                
                
class CAN_SETTINGS(Structure):
    _fields_ = [('Mode',        c_ubyte),
                ('SetBaudrate', c_ubyte),
                ('Baudrate',    c_ubyte),
                ('NetworkType', c_ubyte),
                ('TqSeg1',      c_ubyte),
                ('TqSeg2',      c_ubyte),
                ('TqProp',      c_ubyte),
                ('TqSync',      c_ubyte),
                ('BRP',         c_ushort),
                ('auto_baud',   c_ushort)]


class SWCAN_SETTINGS(Structure):
    _fields_ = [('Mode',                   c_ubyte),
                ('SetBaudrate',            c_ubyte),
                ('Baudrate',               c_ubyte),
                ('NetworkType',            c_ubyte),
                ('TqSeg1',                 c_ubyte),
                ('TqSeg2',                 c_ubyte),
                ('TqProp',                 c_ubyte),
                ('TqSync',                 c_ubyte),
                ('BRP',                    c_ushort),
                ('high_speed_auto_switch', c_ushort),
                ('auto_baud',              c_ushort)]


class LIN_SETTINGS(Structure):
    _fields_ = [('Baudrate',       c_uint),
                ('spbrg',          c_ushort),
                ('brgh',           c_ushort),
                ('MasterResistor', c_ubyte),
                ('Mode',           c_ubyte)]


class ISO9141_KEYWORD2000__INIT_STEP(Structure):
    _fields_ = [('time_500us', c_ushort),
                ('k',          c_ushort),
                ('l',          c_ushort)]


class ISO9141_KEYWORD2000_SETTINGS(Structure):
    _fields_ = [('Baudrate',        c_uint),
                ('spbrg',           c_ushort),
                ('brgh',            c_ushort),
                ('init_steps',      ISO9141_KEYWORD2000__INIT_STEP * 16),
                ('init_step_count', c_ubyte),
                ('p2_500us',        c_ushort),
                ('p3_500us',        c_ushort),
                ('p4_500us',        c_ushort),
                ('chksum_enabled',  c_ushort)]


class UART_SETTINGS(Structure):
    _fields_ = [('Baudrate',     c_ushort),
                ('spbrg',        c_ushort),
                ('brgh',         c_ushort),
                ('parity',       c_ushort),
                ('stop_bits',    c_ushort),
                ('flow_control', c_ubyte),  # 0- off, 1 - Simple CTS RTS,
                ('reserved_1',   c_ubyte),
                ('bOptions',     c_uint)]   # AND to combind these values invert_tx = 1 invert_rx = 2 half_duplex = 4


class STextAPISettings(Structure):
    _fields_ = [('can1_tx_id',      c_uint),
                ('can1_rx_id',      c_uint),
                ('can1_options',    c_uint),    # Set to 1 for Extended, 0 for standard
                ('can2_tx_id',      c_uint),
                ('can2_rx_id',      c_uint),
                ('can2_options',    c_uint),    # Set to 1 for Extended, 0 for standard
                ('network_enables', c_uint),
                ('can3_tx_id3',     c_uint),
                ('can3_rx_id3',     c_uint),
                ('can3_options',    c_uint),    # Set to 1 for Extended, 0 for standard
                ('can4_tx_id4',     c_uint),
                ('can4_rx_id4',     c_uint),
                ('can4_options',    c_uint),    # Set to 1 for Extended, 0 for standard
                ('Reserved0',       c_int),
                ('Reserved1',       c_int),
                ('Reserved2',       c_int),
                ('Reserved3',       c_int),
                ('Reserved4',       c_int)]


class SFireSettings(Structure):
    _fields_ = [('can1',                            CAN_SETTINGS),
                ('can2',                            CAN_SETTINGS),
                ('can3',                            CAN_SETTINGS),
                ('can4',                            CAN_SETTINGS),
                ('swcan',                           SWCAN_SETTINGS),
                ('lsftcan',                         CAN_SETTINGS),
                ('lin1',                            LIN_SETTINGS),
                ('lin2',                            LIN_SETTINGS),
                ('lin3',                            LIN_SETTINGS),
                ('lin4',                            LIN_SETTINGS),
                ('cgi_enable_reserved',             c_ushort),
                ('cgi_baud',                        c_ushort),
                ('cgi_tx_ifs_bit_times',            c_ushort),
                ('cgi_rx_ifs_bit_times',            c_ushort),
                ('cgi_chksum_enable',               c_ushort),
                ('network_enables',                 c_ushort),
                ('network_enabled_on_boot',         c_ushort),
                ('pwm_man_timeout',                 c_ushort),
                ('pwr_man_enable',                  c_ushort),
                ('misc_io_initial_ddr',             c_ushort),
                ('misc_io_initial_latch',           c_ushort),
                ('misc_io_analog_enable',           c_ushort),
                ('misc_io_report_period',           c_ushort),
                ('misc_io_on_report_events',        c_ushort),
                ('ain_sample_period',               c_ushort),
                ('ain_threshold',                   c_ushort),
                ('iso15765_separation_time_offset', c_ushort),
                ('iso9141_kwp_enable_reserved',     c_ushort),
                ('iso9141_kwp_settings',            ISO9141_KEYWORD2000_SETTINGS),
                ('perf_en',                         c_ushort),
                ('iso_parity',                      c_ushort),
                ('iso_msg_termination',             c_ushort),
                ('iso_tester_pullup_enable',        c_ushort),
                ('network_enables_2',               c_ushort),
                ('iso9141_kwp_settings2',           ISO9141_KEYWORD2000_SETTINGS),
                ('iso_parity_2',                    c_ushort), 
                ('iso_msg_termination_2',           c_ushort),
                ('iso9141_kwp_settings_3',          ISO9141_KEYWORD2000_SETTINGS),
                ('iso_parity_3',                    c_ushort), 
                ('iso_msg_termination_3',           c_ushort), 
                ('iso9141_kwp_settings_4',          ISO9141_KEYWORD2000_SETTINGS),
                ('iso_parity_4',                    c_ushort), 
                ('iso_msg_termination_4',           c_ushort), 
                ('fast_init_network_enables_1',     c_ushort),
                ('fast_init_network_enables_2',     c_ushort),
                ('uart',                            UART_SETTINGS),
                ('uart2',                           UART_SETTINGS),
                ('text_api',                        STextAPISettings)]
                
                
class SVCAN3Settings(Structure):
    _fields_ = [('can1',                            CAN_SETTINGS),
                ('can2',                            CAN_SETTINGS),
                ('network_enables',                 c_ushort),
                ('network_enabled_on_boot',         c_ushort),
                ('iso15765_separation_time_offset', c_short),
                ('perf_en',                         c_ushort),
                ('misc_io_initial_ddr',             c_ushort),
                ('misc_io_initial_latch',           c_ushort),
                ('misc_io_report_period',           c_ushort),
                ('misc_io_on_report_events',        c_ushort)]


class APIFirmwareInfo(Structure):
    _fields_ = [('iType',                           c_int),
                # Date and Time (2nd generation neoVI only) 
                ('iMainFirmDateDay',                c_int),
                ('iMainFirmDateMonth',              c_int),
                ('iMainFirmDateYear',               c_int),
                ('iMainFirmDateHour',               c_int),
                ('iMainFirmDateMin',                c_int),
                ('iMainFirmDateSecond',             c_int),
                ('iMainFirmChkSum',                 c_int),
    
                # Version data (3rd generation neoVI only) 
                ('iAppMajor',                       c_ubyte),
                ('iAppMinor',                       c_ubyte),
                ('iManufactureDay',                 c_ubyte),
                ('iManufactureMonth',               c_ubyte),
                ('iManufactureYear',                c_ushort),
                ('iBoardRevMajor',                  c_ubyte),
                ('iBoardRevMinor',                  c_ubyte),
                ('iBootLoaderVersionMajor',         c_ubyte),
                ('iBootLoaderVersionMinor',         c_ubyte)]
