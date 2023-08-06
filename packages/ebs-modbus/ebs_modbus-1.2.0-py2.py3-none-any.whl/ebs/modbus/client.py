

from pymodbus.client.sync import BaseModbusClient
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.constants import Defaults
from pymodbus.exceptions import ParameterException
from pymodbus.pdu import ExceptionResponse
from pymodbus.transaction import ModbusAsciiFramer
from pymodbus.transaction import ModbusBinaryFramer
from pymodbus.transaction import ModbusRtuFramer
from pymodbus.transaction import ModbusSocketFramer

from .decoder import EBSClientDecoder


class ModbusServerException(Exception):
    def __init_(self, response):
        self.response = response


# The staticmethod on implementation() does not allow simple subclassing
class ModbusClient(ModbusSerialClient):
    def __init__(self, method='ascii', **kwargs):
        self.method = method
        self.socket = None
        BaseModbusClient.__init__(self, self._get_framer(method), **kwargs)

        self.port = kwargs.get('port', 0)
        self.stopbits = kwargs.get('stopbits', Defaults.Stopbits)
        self.bytesize = kwargs.get('bytesize', Defaults.Bytesize)
        self.parity = kwargs.get('parity',   Defaults.Parity)
        self.baudrate = kwargs.get('baudrate', Defaults.Baudrate)
        self.timeout = kwargs.get('timeout',  Defaults.Timeout)
        if self.method == "rtu":
            self._last_frame_end = 0.0
            self._silent_interval = 3.5 * (1 + 8 + 2) / self.baudrate

    def execute(self, request=None):
        result = super(ModbusClient, self).execute(request)
        if isinstance(result, ExceptionResponse):
            raise ModbusServerException(result)
        return result

    def _get_framer(self, method):
        method = method.lower()
        if method == 'ascii':
            return ModbusAsciiFramer(EBSClientDecoder())
        elif method == 'rtu':
            return ModbusRtuFramer(EBSClientDecoder())
        elif method == 'binary':
            return ModbusBinaryFramer(EBSClientDecoder())
        elif method == 'socket':
            return ModbusSocketFramer(EBSClientDecoder())
        raise ParameterException("Invalid framer method requested")
