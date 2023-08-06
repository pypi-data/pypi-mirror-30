# The file is part of the pyneovi project and is provided under the MIT License terms.
# For license information see LICENSE.txt.
"""
This module provides classes and functions to allow a network specification to
be created for use with pyneovi. A network specification defines the valid
networks for a given model of vehicle, along with the ECUs on those networks
and the identifiers and signals made available by the ECUs.

.. Author: John Kemp <kemp@kempj.co.uk>

Below is an example of a simple network specification. Only the medium speed
CAN bus is defined and only a single ECU is associated with that network. The
ECU provides four identifiers, each made up of a single signal.

.. literalinclude:: ../examples/create_network_spec.py

"""


import json


# Identifier signal types
ANALOG = 0

# Identifier value types
UNSIGNED_INT = 0

# Signal IO type
READ = 0
WRITE = 1
READ_WRITE = 2


class NonByteBoundarySignalError(Exception):
    pass
    

class ValueTooLargeError(Exception):
    pass


class UnsupportedValueTypeError(Exception):
    pass


def prepend_zeroes(values, final_length):
    return ([0] * (final_length - len(values))) + values


class _IdentifierList:
    def __init__(self, identifiers):
        self.by_name = {identifier.name: identifier for identifier in identifiers}
        self.by_id = {identifier.data_id: identifier for identifier in identifiers}
    
    def get_names(self):
        return self.by_name.keys()
    
    def get_ids(self):
        return self.by_id.keys()
    
    def __contains__(self, k):
        return k in self.by_name or k in self.by_id
    
    def __getitem__(self, k):
        if type(k) == int:
            return self.by_id[k]
        elif type(k) == str:
            return self.by_name[k]
        else:
            raise KeyError(k)


class Signal:
    """
    __init__(self, name='value', signal_type=ANALOG, value_type=UNSIGNED_INT, start=0, length=8, min=None, max=None, units='', m=1, b=0, description='')
    
    Represents a signal. An :py:class:`.spec.Identifier` will contain one or
    more signals.
    
    :param str name: The name of this signal.
    :param int signal_type: The type of signal. Currently, only
        :py:data:`.spec.ANALOG` is supported.
    :param int value_type: The type of value returned for the signal.
        Currently only :py:data:`.spec.UNSIGNED_INT` is supported.
    :param int start: The bit within the identifier's aggregate value at
        which this signal starts.
    :param int length: The length in bits of this signal.
    :param float min_val: The minimum value for this signal. This is not enforced
        and is for reference only. If not specified then b is used as the
        default value.
    :param float max_val:  The minimum value for this signal. This is not enforced
        and is for reference only. If not specified then (255. * m) + b is
        used as the default value.
    :param str units: The units of the signal once converted.
    :param float m: The slope for conversion of the signal into engineering
        units.
    :param float b: The offset for conversion of the signal into engineering
        units.
    :param str description: A human-readable description of the signal.
   
    :raises NonByteBoundarySignalError: If length or start are not integer
        multiples of 8.
    """
    def __init__(self, name='value', signal_type=ANALOG, value_type=UNSIGNED_INT, start=0, length=8, min_val=None, max_val=None, units='', m=1, b=0, description=''):
        self.name = name
        self.signal_type = signal_type
        self.value_type = value_type
        self.start = start
        self.length = length
        if min_val is None:
            self.min = b
        else:
            self.min = min_val
        if max_val is None:
            self.max = (255. * m) + b
        else:
            self.max = max_val
        self.units = units
        self.m = m
        self.b = b
        self.description = description
        
        if length % 8 != 0 or start % 8 != 0:
            raise NonByteBoundarySignalError
    
    def decode_signal_bytes(self, signal_bytes):
        """
        Converts the individual data bytes into the final value for the signal.
        
        :param signal_bytes: The bytes received from the ECU.
        :type signal_bytes: list of ints
        :returns: Tuple of final value and the units of the signal.
        
        :raises UnsupportedValueTypeError: If the signal is of a type that is
            currently unsupported.
        """
        if self.signal_type == ANALOG and self.value_type == UNSIGNED_INT:
            value = sum(x << (i*8) for i, x in enumerate(reversed(signal_bytes[self.start:self.start + (self.length / 8)])))
            value = self.m * value + self.b
        else:
            raise UnsupportedValueTypeError
        
        return value, self.units
    
    def encode_value(self, value):
        """
        Converts a value into the individual data bytes required for
        transmission.
        
        :param float/int value: The value for conversion.
        
        :raises UnsupportedValueTypeError: If the signal is of a type that is
            currently unsupported.
        :raises ValueTooLargeError: If the value does not fit into the number
            of bits specified for the signal.
        """
        if self.signal_type == ANALOG and self.value_type == UNSIGNED_INT:
            data_bytes = []
            value = int(round((value - self.b) / self.m))

            if value == 0:
                return prepend_zeroes([0], self.length / 8)
            
            while value > 0:
                data_bytes.append(value & 0xFF)
                value >>= 8
            
            if len(data_bytes) > (self.length / 8):
                raise ValueTooLargeError

            return prepend_zeroes([x for x in reversed(data_bytes)], self.length / 8)
        else:
            raise UnsupportedValueTypeError
    
    def __repr__(self):
        return 'Signal(name="%(name)s", signal_type=%(signal_type)u, value_type=%(value_type)u, start=%(start)u, length=%(length)u, min=%(min)s, max=%(max)s, units="%(units)s", m=%(m)f, b=%(b)f)' % self.__dict__


# TODO: Add method to encode all signal values into a final value to send
class Identifier:
    """
    __init__(self, name, data_id, signals = [], io_type = READ)
    
    Represents an identifier (an example of which would be "Blower Speed Output"
    in a HVAC ECU). The value of an identifier can consist of multiple
    individual signals but often there is only a single signal associated with
    an identifier.
    
    :param str name: The name of the identifier.
    :param int data_id: The address (internal to the ECU) with which this
        identifier is associated.
    :param signals: The signals that form this identifier.
    :type signals: list of spec.Signal
    :param int io_type: Allowed IO for this identifier: :py:data:`.spec.READ`,
        :py:data:`.spec.WRITE`, :py:data:`.spec.READ_WRITE`.
    """
    def __init__(self, name, data_id, signals=(), io_type=READ):
        self.name = name
        self.data_id = data_id
        self.data_id_bytes = [(data_id & 0xFF00) >> 8, data_id & 0x00FF]
        self.signals = signals
        self.io_type = io_type
    
    def get_data_id_bytes(self):
        """
        :returns: The data_id as individual bytes. Used when constructing a
            message.
        """
        return self.data_id_bytes
    
    def __repr__(self):
        return 'Identifier(name="%(name)s", data_id=%(data_id)X, signals=%(signals)s)' % self.__dict__
    
    def __str__(self):
        return 'Identifier: %(name)s (%(data_id)X)' % self.__dict__


class ECU:
    """
    Represents an ECU for the purpose of building a network specification. Note
    that if you need an object that allows you to communicate with the ECU then
    you're looking for :py:class:`.ecu.ECU`.
    
    :param int network: The network to transmit on. See NETID_* in
        :py:mod:`~neovi.neovi`.
    :param int address: The address of the ECU.
    :param str short_desc: A short name for the ECU (e.g. "HVAC").
    :param str long_desc: A long description for the ECU (e.g. including model
        number or other information).
    """
    def __init__(self, network, address, short_desc='', long_desc=''):
        self.network = network
        self.request_id = address
        self.response_id = address + 8
        self.short_desc = short_desc
        self.long_desc = long_desc
    
    def get_network(self):
        return self.network
    
    def get_request_id(self):
        return self.request_id
    
    def get_response_id(self):
        return self.response_id
    
    def __repr__(self):
        return 'ECU(network=%(network)u, address=0x%(request_id)X, short_desc="%(short_desc)s", long_desc="%(long_desc)s")' % self.__dict__
 
    
class PyNeoViJSONEncoder(json.JSONEncoder):
    """
    Can be passed to json.dump as the cls parameter to handle the additional
    object types defined here.
    """
    def default(self, o):
        if o.__class__.__name__ == 'Identifier':
            return 'PyNeoVi.Identifier', o.name, o.data_id, o.signals, o.io_type
        elif o.__class__.__name__ == 'ECU':
            return 'PyNeoVi.ECU', o.network, o.request_id, o.short_desc, o.long_desc
        elif o.__class__.__name__ == 'Signal':
            return 'PyNeoVi.Signal', o.name, o.signal_type, o.value_type, o.start, o.length, o.min, o.max, o.units, o.m, o.b, o.description
        else:
            return json.JSONEncoder.default(self, o)


def from_json(json_object):
    """
    Can be passed to json.load as the object_hook parameter to handle the
    additional object types defined here.
    """
    output = {}
    
    for k, v in json_object.items():
        if type(v) != list:
            if k == 'networks':
                output[k] = {int(k1): v1 for k1, v1 in v.items()}
            else:
                output[k] = v
        elif v[0] == 'PyNeoVi.ECU':
            output[k] = ECU(*v[1:])
        elif v[0] == 'PyNeoVi.Identifier':
            output[k] = Identifier(*v[1:])
        elif k == 'identifiers':
            new_idents = []
            for identifier in v:
                signals = [Signal(*signal_info[1:]) for signal_info in identifier[3]]
                new_idents.append(Identifier(identifier[1], identifier[2], signals))
            output[k] = _IdentifierList(new_idents)
        else:
            print('%s %s' % (k, v))
            output[k] = v
    
    return output

