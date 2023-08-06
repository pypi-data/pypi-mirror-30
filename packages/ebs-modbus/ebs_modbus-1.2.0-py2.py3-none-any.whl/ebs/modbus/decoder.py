
from pymodbus.compat import byte2int
from pymodbus.interfaces import IModbusDecoder
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ExceptionResponse, ModbusExceptions as ecode
from pymodbus.factory import _logger

from pymodbus.register_read_message import ReadHoldingRegistersResponse
from pymodbus.register_read_message import ReadInputRegistersResponse
from pymodbus.register_read_message import ReadWriteMultipleRegistersResponse
from pymodbus.register_write_message import WriteMultipleRegistersResponse
from pymodbus.register_write_message import WriteSingleRegisterResponse
from pymodbus.register_write_message import MaskWriteRegisterResponse
from pymodbus.bit_read_message import ReadDiscreteInputsResponse
from pymodbus.bit_read_message import ReadCoilsResponse
from pymodbus.bit_write_message import WriteMultipleCoilsResponse
from pymodbus.bit_write_message import WriteSingleCoilResponse
from pymodbus.diag_message import DiagnosticStatusResponse
from pymodbus.diag_message import ReturnQueryDataResponse
from pymodbus.diag_message import RestartCommunicationsOptionResponse
from pymodbus.diag_message import ReturnDiagnosticRegisterResponse
from pymodbus.diag_message import ChangeAsciiInputDelimiterResponse
from pymodbus.diag_message import ForceListenOnlyModeResponse
from pymodbus.diag_message import ClearCountersResponse
from pymodbus.diag_message import ReturnBusMessageCountResponse
from pymodbus.diag_message import ReturnBusCommunicationErrorCountResponse
from pymodbus.diag_message import ReturnBusExceptionErrorCountResponse
from pymodbus.diag_message import ReturnSlaveMessageCountResponse
from pymodbus.diag_message import ReturnSlaveNoReponseCountResponse
from pymodbus.diag_message import ReturnSlaveNAKCountResponse
from pymodbus.diag_message import ReturnSlaveBusyCountResponse
from pymodbus.diag_message import ReturnSlaveBusCharacterOverrunCountResponse
from pymodbus.diag_message import ReturnIopOverrunCountResponse
from pymodbus.diag_message import ClearOverrunCountResponse
from pymodbus.diag_message import GetClearModbusPlusResponse
from pymodbus.file_message import ReadFileRecordResponse
from pymodbus.file_message import WriteFileRecordResponse
from pymodbus.file_message import ReadFifoQueueResponse
from pymodbus.other_message import ReadExceptionStatusResponse
from pymodbus.other_message import GetCommEventCounterResponse
from pymodbus.other_message import GetCommEventLogResponse
from pymodbus.other_message import ReportSlaveIdResponse

from .mei import ReadEBSDeviceInformationResponse


class EBSClientDecoder(IModbusDecoder):
    __function_table = [
            ReadHoldingRegistersResponse,
            ReadDiscreteInputsResponse,
            ReadInputRegistersResponse,
            ReadCoilsResponse,
            WriteMultipleCoilsResponse,
            WriteMultipleRegistersResponse,
            WriteSingleRegisterResponse,
            WriteSingleCoilResponse,
            ReadWriteMultipleRegistersResponse,

            DiagnosticStatusResponse,

            ReadExceptionStatusResponse,
            GetCommEventCounterResponse,
            GetCommEventLogResponse,
            ReportSlaveIdResponse,

            ReadFileRecordResponse,
            WriteFileRecordResponse,
            MaskWriteRegisterResponse,
            ReadFifoQueueResponse,

            ReadEBSDeviceInformationResponse,
    ]
    __sub_function_table = [
            ReturnQueryDataResponse,
            RestartCommunicationsOptionResponse,
            ReturnDiagnosticRegisterResponse,
            ChangeAsciiInputDelimiterResponse,
            ForceListenOnlyModeResponse,
            ClearCountersResponse,
            ReturnBusMessageCountResponse,
            ReturnBusCommunicationErrorCountResponse,
            ReturnBusExceptionErrorCountResponse,
            ReturnSlaveMessageCountResponse,
            ReturnSlaveNoReponseCountResponse,
            ReturnSlaveNAKCountResponse,
            ReturnSlaveBusyCountResponse,
            ReturnSlaveBusCharacterOverrunCountResponse,
            ReturnIopOverrunCountResponse,
            ClearOverrunCountResponse,
            GetClearModbusPlusResponse,

            ReadEBSDeviceInformationResponse,
    ]

    def __init__(self):
        functions = set(f.function_code for f in self.__function_table)
        self.__lookup = dict([(f.function_code, f) for f in self.__function_table])
        self.__sub_lookup = dict((f, {}) for f in functions)
        for f in self.__sub_function_table:
            self.__sub_lookup[f.function_code][f.sub_function_code] = f

    def lookupPduClass(self, function_code):
        return self.__lookup.get(function_code, ExceptionResponse)

    def decode(self, message):
        try:
            return self._helper(message)
        except ModbusException as er:
            _logger.error("Unable to decode response %s" % er)
        return None

    def _helper(self, data):
        function_code = byte2int(data[0])
        _logger.debug("Factory Response[%d]" % function_code)
        response = self.__lookup.get(function_code, lambda: None)()
        if function_code > 0x80:
            code = function_code & 0x7f  # strip error portion
            response = ExceptionResponse(code, ecode.IllegalFunction)
        if not response:
            raise ModbusException("Unknown response %d" % function_code)
        response.decode(data[1:])

        if hasattr(response, 'sub_function_code'):
            lookup = self.__sub_lookup.get(response.function_code, {})
            subtype = lookup.get(response.sub_function_code, None)
            if subtype:
                response.__class__ = subtype
        return response
