

from .client import ModbusServerException
from .device import ModbusDevice


class ModbusHotplugMixin(object):
    def claim_interface(
            self  # type: ModbusDevice
    ):
        try:
            self.write_register(1, 1, unit=self.address)
        except ModbusServerException:
            pass
