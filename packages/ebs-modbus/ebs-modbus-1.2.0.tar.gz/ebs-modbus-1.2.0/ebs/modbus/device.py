

from .client import ModbusClient
from functools import partial


class ModbusDevice(object):
    def __init__(self, address, mc=None, **kwargs):
        self.address = address
        if mc is None:
            kwargs.setdefault('method', 'rtu')
            kwargs.setdefault('port', '/dev/ttyACM1')
            kwargs.setdefault('baudrate', 256000)
            mc = ModbusClient(**kwargs)
        self.mc = mc

    def connect(self):
        return self.mc.connect()

    def close(self):
        return self.mc.close()

    def execute(self, request, broadcast=False):
        if not broadcast:
            request.unit_id = self.address
        else:
            request.unit_id = 0x00
        return self.mc.execute(request)

    _client_functions = [
        'read_coils',
        'read_discrete_inputs',
        'write_coil',
        'write_coils',
        'write_register',
        'write_registers',
        'read_holding_registers',
        'read_input_registers',
        'readwrite_registers',
        'mask_write_register',
        'claim_interface',
    ]

    def __getattr__(self, name):
        if name in self._client_functions:
            return partial(getattr(self.mc, name), unit=self.address)
