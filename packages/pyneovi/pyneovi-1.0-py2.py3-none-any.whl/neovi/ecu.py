# The file is part of the pyneovi project and is provided under the MIT License terms.
# For license information see LICENSE.txt.
"""
Provides the :py:class:`.ECU` class that represents an individual ECU.

.. Author: John Kemp <kemp@kempj.co.uk>

Below is an example of reading values from an ECU. Note that it requires a
network spec such as the one created in the example on the :py:mod:`.spec` module page.

.. literalinclude:: ../examples/read_values.py
"""


# Python 2.x compatibility
from __future__ import absolute_import, division, print_function, unicode_literals

import threading
import logging

from neovi.structures import format_array, get_status_bits_set, array_equal, icsSpyMessage
import neovi.can as can


class CommandError(Exception):
    """
    An error response was received after sending a message on the bus.
    """
    def __init__(self, code):
        self.code = code
        if code in can.error_code_lookup:
            self.desc = can.error_code_lookup[code]
            message = '0x%X (%s)' % (self.code, can.error_code_lookup[self.code])
        else:
            self.desc = ''
            message = '0x%X' % self.code

        super(CommandError, self).__init__(message)


class NoResponseError(Exception):
    """
    No response was received after sending a message on the bus.
    """
    pass


class ECU:
    """
    Represents a vehicle ECU.
    
    :param spec.ECU ecu_info: Details of the ECU (network, address...).
    :param neodevice.NeoDevice interface: The neoVI device to use for
        communication.
    :param bool auto_tester_present_on_auth: Should a "tester present" message
        be sent at a regular interval if successful authentication (by an
        external tool) is detected?
    :param bool log_unhandled_messages: Should messages to this ECU that have
        no associated subscription be logged?
    """
    def __init__(self, ecu_info, interface, auto_tester_present_on_auth=True, log_unhandled_messages=False):
        self.ecu = ecu_info['ecu']
        self.identifiers = ecu_info['identifiers']
        self.interface = interface

        self.tester_present_interval = None
        self.tester_present_timer = None
        self.tester_present_lock = threading.Lock()

        self.waiting_for = []
        self.waiting_for_lock = threading.Lock()
        self.log_unhandled_messages = log_unhandled_messages

        self.msg_lock = threading.Lock()

        self.auto_tester_present_on_auth = auto_tester_present_on_auth

        self.interface.subscribe_to(self._handle_incoming_message, self.ecu.get_network(), self.ecu.get_response_id())

    def _get_identifier_bytes(self, identifier):
        if identifier in self.identifiers:
            return self.identifiers[identifier].get_data_id_bytes()
        elif identifier.__class__.__name__ == 'Identifier':
            return identifier.get_data_id_bytes()
        else:
            return identifier

    def _get_identifier_object(self, identifier):
        if identifier in self.identifiers:
            return self.identifiers[identifier]
        elif identifier.__class__.__name__ == 'Identifier':
            return identifier
        else:
            return None

    # noinspection PyMethodMayBeStatic
    def _msg_recv_callback(self, msg, misc):
        misc[1][0] = msg
        misc[0].set()

    def _transaction(self, msg_type, match_bytes, send_func, send_params):
        event = threading.Event()
        msg = [None]
        subs_key = (msg_type + 0x40, match_bytes, self._msg_recv_callback, (event, msg))

        self.msg_lock.acquire()

        self.waiting_for_lock.acquire()
        self.waiting_for.append(subs_key)
        self.waiting_for_lock.release()

        send_func(*send_params)
        result = event.wait(0.2)

        if not result:
            # Give up waiting for the message and clean up our request
            self.waiting_for_lock.acquire()
            self.waiting_for.remove(subs_key)
            self.waiting_for_lock.release()
            self.msg_lock.release()
            raise NoResponseError

        self.msg_lock.release()

        # msg (as passed around in subs_key) should have been modified by the thread handling the incoming messages.
        msg = msg[0]    # type: icsSpyMessage

        if msg.Data[1] == 0x7F:
            raise CommandError(msg.Data[3])

        return msg

    def _send_read_data_by_id(self, identifier):
        """
        Send a "Read Data By ID" message.
        
        :param identifier: An array of integers specifying the identifier to
                           read (e.g. [0x98, 0x05]).
        """
        return self.interface.tx_message(self.ecu.get_network(), self.ecu.get_request_id(), can.READ_DATA_BY_ID, identifier)

    def read_data_by_id(self, identifier):
        """
        Send a "Read Data By ID" message and return the response value(s). The
        return value will be a dictionary of decoded values if an identifier
        name or an identifier object is passed in, or the raw message bytes if
        an integer array is passed in.
        
        :param identifier: This may be one of three types of object/value:
           1) the name of an identifier known to the :py:class:`.spec.ECU` that
           was passed to the constructor, 
           2) a :py:class:`.spec.Identifier` object, or 
           3) an array of integers specifying the identifier to read (e.g.
           [0x98, 0x05]).
        """
        id_bytes = self._get_identifier_bytes(identifier)

        msg = self._transaction(can.READ_DATA_BY_ID, id_bytes, self._send_read_data_by_id, (id_bytes,))

        ident_obj = self._get_identifier_object(identifier)
        if ident_obj is None:
            return msg.Data[4:]

        values = {}
        for signal in ident_obj.signals:
            values[signal.name] = signal.decode_signal_bytes(msg.Data[4:])

        return values

    def _send_io_control_by_id(self, identifier, value=None, control_type=can.ControlType.ShortTermAdjustment):
        """
        Send a "IO Control By ID" message.
        
        :param identifier: An array of integers specifying the identifier to read (e.g. [0x98, 0x05]).
        :param value: The value to set the output to. A value of None will use the default. Default = [0x00].
        :param can.ControlType control_type: The type of control to apply. Default = ControlType.ShortTermAdjustment.
        """
        if control_type == can.ControlType.ShortTermAdjustment:
            if value is None:
                value = [0x00]
            return self.interface.tx_message(self.ecu.get_network(), self.ecu.get_request_id(), can.IO_CONTROL_BY_ID, identifier + [control_type] + value)
        else:
            return self.interface.tx_message(self.ecu.get_network(), self.ecu.get_request_id(), can.IO_CONTROL_BY_ID, identifier + [control_type])

    def io_control_by_id(self, identifier, value=0x00, control_type=can.ControlType.ShortTermAdjustment):
        """
        Send a "IO Control By ID" message.
        
        :param identifier: This may be one of three types of object/value:
           1) the name of an identifier known to the :py:class:`.spec.ECU` that was passed to the constructor,
           2) a :py:class:`.spec.Identifier` object, or
           3) an array of integers specifying the identifier to read (e.g. [0x98, 0x05]).
           Note that due to limitations of the current implementation, the value will be assumed to correspond to the
           first signal defined for the identifier.
        :param int value: The value to set the output to. Conversion of the value into the form required by the
                          underlying signal will be performed here. Default = 0x00.
        :param can.ControlType control_type: The type of control to apply. Default = SHORT_TERM_ADJUSTMENT.
        """
        id_bytes = self._get_identifier_bytes(identifier)

        if control_type == can.ControlType.ShortTermAdjustment:
            value = self._get_identifier_object(identifier).signals[0].encode_value(value)

        msg = self._transaction(can.IO_CONTROL_BY_ID, id_bytes, self._send_io_control_by_id, (id_bytes, value, control_type))

        # Figure out what we want to return here
        return True

    def _send_diagnostic_session_control(self, session_type):
        """
        Send a "Diagnostic Session Control" message.
        
        :param can.SessionType session_type: The type of session to switch to.
        """
        return self.interface.tx_message(self.ecu.get_network(), self.ecu.get_request_id(), can.DIAGNOSTIC_SESSION_CONTROL, [session_type])

    def diagnostic_session_control(self, session_type):
        """
        Send a "Diagnostic Session Control" message.

        :param can.SessionType session_type: The type of session to switch to.
        """
        msg = self._transaction(can.DIAGNOSTIC_SESSION_CONTROL, [], self._send_diagnostic_session_control, (session_type,))
        return list(msg.Data[3:])

    def _send_security_access(self, subfunction, key):
        return self.interface.tx_message(self.ecu.get_network(), self.ecu.get_request_id(), can.SECURITY_ACCESS, [subfunction] + key)

    def security_access(self, subfunction, key=None):
        if key is None:
            key = []
        msg = self._transaction(can.SECURITY_ACCESS, [subfunction], self._send_security_access, (subfunction, key))

        if subfunction % 2 == 0:
            # We were sending a key
            return True
        else:
            # We were requesting a seed
            seed_length = msg.Data[0] - 2
            return list(msg.Data[3:3 + seed_length])

    def send_tester_present(self):
        """
        Send a "Tester Present" message to avoid a diagnostic session timing out.
        """
        self.interface.tx_message(self.ecu.get_network(), self.ecu.get_request_id(), can.TESTER_PRESENT, [0x80])

    def send_periodic_tester_present(self, interval=2):
        """
        Start sending a periodic "tester present" message to avoid a diagnostic session timing out.
        :param int interval: Period in seconds between messages.
        """
        self.tester_present_lock.acquire()

        # To avoid all sorts of nonsense, we just don't do anything if the
        # timer is already set up. Call stop_periodic_tester_present before
        # calling this again.
        if self.tester_present_timer is not None:
            self.tester_present_lock.release()
            return

        self.send_tester_present()

        self.tester_present_interval = interval
        self.tester_present_timer = threading.Timer(interval, self._send_periodic_tester_present)
        self.tester_present_timer.start()

        self.tester_present_lock.release()

    def _send_periodic_tester_present(self):
        self.tester_present_lock.acquire()
        # We do this check to avoid the following:
        #  - stop_periodic_tester_present is entered and obtains the lock.
        #  - The timer fires, enters this method, and blocks on the lock.
        #  - stop_periodic_tester_present cancels the timer, and releases the lock.
        #  - This method continues and spawns another timer, ensuring that the signal continues.
        # We, in fact, *can* stop the signal.
        if self.tester_present_interval is not None:
            self.send_tester_present()
            self.tester_present_timer = threading.Timer(self.tester_present_interval, self._send_periodic_tester_present)
            self.tester_present_timer.start()
        self.tester_present_lock.release()

    def stop_periodic_tester_present(self):
        """
        Stop sending the periodic "tester present" message.
        """
        self.tester_present_lock.acquire()

        if self.tester_present_timer is not None:
            self.tester_present_timer.cancel()
            self.tester_present_timer = None

        self.tester_present_interval = None

        self.tester_present_lock.release()

    def _handle_incoming_message(self, msg, user_data):
        handled = False
        self.waiting_for_lock.acquire()
        # First, check if it's an error message, if so then we have to search differently
        if msg.Data[1] == 0x7F:
            for i, (msg_type, additional_bytes, callback, misc) in enumerate(self.waiting_for):
                if msg_type == (msg.Data[2] + 0x40):
                    callback(msg, misc)
                    self.waiting_for.pop(i)
                    handled = True
                    break
        else:
            for i, (msg_type, additional_bytes, callback, misc) in enumerate(self.waiting_for):
                if msg_type == msg.Data[1] and array_equal(msg.Data[2:2 + len(additional_bytes)], additional_bytes):
                    callback(msg, misc)
                    self.waiting_for.pop(i)
                    handled = True
                    break
        self.waiting_for_lock.release()

        # Special handling for tester present
        if self.auto_tester_present_on_auth and [x for x in msg.Data][:3] == [0x02, 0x67, 0x04]:
            print("Successful auth detected, starting periodic tester present signal")
            self.send_periodic_tester_present()

        if self.log_unhandled_messages and not handled:
            logging.debug('Unhandled message from ECU %s' % self.ecu.short_desc)
            logging.debug(' - ArbIDOrHeader = %X, number data bytes = %X' % (msg.ArbIDOrHeader, msg.NumberBytesData))
            logging.debug(' - Data = %s' % format_array(msg.Data))
            logging.debug(' - Ack = %s' % format_array(msg.AckBytes))
            logging.debug(' - Value = %f, misc data = %X' % (msg.Value, msg.MiscData))
            stat, stat2 = get_status_bits_set(msg)
            stat = stat + stat2
            for i in range(0, len(stat), 3):
                stats = stat[i:i+3]
                logging.debug(' - %s' % ', '.join(stats))

    def __del__(self):
        self.stop_periodic_tester_present()

